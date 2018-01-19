import atexit
import ssl
import sys
import time

from pyVim import connect
from pyVim.connect import Disconnect
from pyVmomi import vim, vmodl
from model.ovf_handler import OvfHandler

from utils.common import Common


class VMManager(object):
    si = None
    connected = False
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)

    def __init__(self):
        pass

    def connect(self, vip, vuser, vpwd):
        try:
            self.si = connect.Connect(vip, 443, vuser, vpwd,
                                 sslContext=self.ssl_context)
            self.connected = True
        except Exception as e:
            print "Failed to connect to vCenter by given parameters [vip=%s, vuser=%s, vpwd=%s]" % (vip, vuser, '******')
            raise e

    def get_obj(self, content, vimtype, name):
        obj = None
        container = content.viewManager.CreateContainerView(content.rootFolder, vimtype, True)
        for c in container.view:
            if c.name == name:
                obj = c
                break
        return obj

    def get_objs(self, content, vimtype, prefix):
        objs = []
        container = content.viewManager.CreateContainerView(content.rootFolder, vimtype, True)
        for c in container.view:
            if c.name.startswith(prefix):
                objs.append(c)
        return objs

    def _wait_for_task(self, task, actionName='job', hideResult=False):
        try:
            while task.info.state == vim.TaskInfo.State.running:
                time.sleep(2)
            time.sleep(2)
            if task.info.state == vim.TaskInfo.State.success:
                if task.info.result is not None and not hideResult:
                    out = '%s completed successfully, result: %s' % (actionName, task.info.result)
                    print out
                else:
                    out = '%s completed successfully.' % actionName
                    print out
            else:
                out = '%s did not complete successfully: %s' % (actionName, task.info.error)
                raise task.info.error
                print out
        except Exception, ex:
            print "Caught exception: %s" % str(ex)
            return 1

    def set_ip(self, vmname, vmip, vmdns, dnsdomain=None, nmask=None, gateway=None):

        if vmname is None or vmip is None or vmdns is None:
            print "invalid arguments"
            return
        if len(vmdns) == 0:
            print "invalid argument: [dns]"

        if not Common.is_ip(vmip):
            print "invalid argument: [ip]"
            return
        if not self.connected:
            print "vsphere is not connected"
            return
        if nmask is None:
            nmask = '255.255.255.0'
        if gateway is None:
            ipbits=[x.strip() for x in vmip.split('.')]
            ipbits[3]='1'
            gateway = '.'.join(ipbits)

        vm = self.get_vm(vmname)
        if vm.runtime.powerState != 'poweredOff':
            print "WARNING:: Power off your VM before reconfigure"
            sys.exit(1)
            return

        adaptermap = vim.vm.customization.AdapterMapping()
        globalip = vim.vm.customization.GlobalIPSettings()
        adaptermap.adapter = vim.vm.customization.IPSettings()

        """Static IP Configuration"""
        adaptermap.adapter.ip = vim.vm.customization.FixedIp()
        adaptermap.adapter.ip.ipAddress = vmip
        adaptermap.adapter.subnetMask = nmask
        adaptermap.adapter.gateway = gateway
        globalip.dnsServerList = vmdns

        if not dnsdomain is None:
            adaptermap.adapter.dnsDomain = dnsdomain

        # For Linux . For windows follow sysprep
        if not dnsdomain is None:
            d=dnsdomain
        else:
            d=''

        ident = vim.vm.customization.LinuxPrep(domain=d,
                                               hostName=vim.vm.customization.FixedName(name=vmname))

        customspec = vim.vm.customization.Specification()
        # For only one adapter
        customspec.identity = ident
        customspec.nicSettingMap = [adaptermap]
        customspec.globalIPSettings = globalip

        print "reconfiguring VM networks . . ."
        task = vm.Customize(spec=customspec)

        # Wait for Network Reconfigure to complete
        try:
            self._wait_for_task(task, self.si)
        except vim.fault.CustomizationPending, p:
            print 'do nothing here, just start the vm to apply the previous customization'

    def upload_ova(self, datacenter, datastore, hostname, ova_path, vm_name=None, net_from='VM Network 10', net_to='VM Network'):
        dc = self.get_dc(datacenter)
        host = self.get_host(hostname)
        rp = self.get_rp_by_host(host)
        ds = self.get_ds(dc, datastore)

        if vm_name:
            ovf_handle = OvfHandler(ova_path, vm_name)
        else:
            ovf_handle = OvfHandler(ova_path)

        # remove the existing vm first
        if ovf_handle.vmname:
            vm = self.get_vm(ovf_handle.vmname)
            if vm:
                print "WARNING: Remove the existing VM [%s]" % ovf_handle.vmname
                self._remove_vm_obj(vm)

        ovfManager = self.si.content.ovfManager
        nets=vim.OvfManager.NetworkMapping.Array()
        net=self.get_network_by_host(host, net_to)
        netMapping=vim.OvfManager.NetworkMapping(name=net_from, network=net)
        nets.append(netMapping)
        cisp = vim.OvfManager.CreateImportSpecParams(networkMapping=nets)
        cisr = ovfManager.CreateImportSpec(ovf_handle.get_descriptor(),
                                           rp, ds, cisp)
        if len(cisr.error):
            print("The following errors will prevent import of this OVA:")
            for error in cisr.error:
                print("%s" % error)
            return 1
        ovf_handle.set_spec(cisr)
        lease = rp.ImportVApp(cisr.importSpec, dc.vmFolder)
        while lease.state == vim.HttpNfcLease.State.initializing:
            print("Waiting for lease to be ready...")
            time.sleep(1)
        if lease.state == vim.HttpNfcLease.State.error:
            print ("Lease error: %s" % lease.error)
            return 1
        if lease.state == vim.HttpNfcLease.State.done:
            return 0

        print("Starting deploy...")
        return ovf_handle.upload_disks(lease, hostname)

    # def get_network(self, datacenter, network_name):
    #     for n in datacenter.network:
    #         if n.name == network_name:
    #             return n
    #     raise Exception('Failed to find netowrk named [%s]' % network_name)

    def get_network_by_host(self, host, network_name):

        if isinstance(host, basestring):
            host = self.get_host(host)

        for n in host.network:
            if n.name == network_name:
                return n
        raise Exception('Failed to find network named [%s]' % network_name)

    def clone_vm_to_template(self, datacenter, host, datastore, vm_name, template_name):
        content = self.si.RetrieveContent()
        datacenter = self.get_obj(content, [vim.Datacenter], datacenter)
        # get the folder where VMs are kept for this datacenter
        vmFolder = datacenter.vmFolder
        vm = self.get_obj(content, [vim.VirtualMachine], vm_name)
        if vm.runtime.powerState != 'poweredOff':
            print "WARNING:: Power off your VM before creating template"
            sys.exit(1)
        # remove the existing vm template frist
        vm_template = self.get_vm(template_name)
        if vm_template:
            print "WARNING: Remove the existing VM template [%s]" % template_name
            self._remove_vm_obj(vm_template)

        target_host = self.get_obj(content, [vim.HostSystem], host)

        relocate_spec = vim.vm.RelocateSpec()
        for ds in target_host.datastore:
            # Store the OVS vApp VM in local datastore of each host
            if ds.summary.type == 'VMFS' and ds.name == datastore:
                print "Storing the template in [%s]" % ds.name
                relocate_spec.datastore = ds
                break

        relocate_spec.host = target_host
        relocate_spec.pool = vm.resourcePool

        cloneSpec = vim.vm.CloneSpec(powerOn=False, template=True, location=relocate_spec)
        print "Creating template [%s] ... " % template_name
        task = vm.Clone(name=template_name, folder=vmFolder, spec=cloneSpec)
        job_status = self._wait_for_task(task, self.si)

        if job_status == 0:
            print "Template [%s] created successfully" % 'template_name'

    def remove_vm(self, vmname):
        vm = self.get_vm(vmname)
        if vm is None:
            print "Can't get vm by given vm name, skip the current vm removal task %s" % vmname
            return
        self._remove_vm_obj(vm)

    def _remove_vm_obj(self, vm):
        if format(vm.runtime.powerState) == "poweredOn":
            self.stop_vm(vm)

        print("Destroying VM from vSphere.")
        destroy_task = vm.Destroy()
        self._wait_for_task(destroy_task, self.si)

    def get_vm(self, vmname):
        content = self.si.RetrieveContent()
        return self.get_obj(content, [vim.VirtualMachine], vmname)

    def get_vms_startwith(self, prefix):
        def convert(x): return x.name
        content = self.si.RetrieveContent()
        return map(convert, self.get_objs(content, [vim.VirtualMachine], prefix))

    def get_hostname(self, datastore):
        content = self.si.RetrieveContent()
        hostname = None
        container = content.viewManager.CreateContainerView(content.rootFolder, [vim.HostSystem], True)
        for c in container.view:
            for ds in c.datastore:
                if ds.name == datastore:
                    hostname = c.name
                    break
        return hostname

    def exist_vm(self, vmname):
        vm = self.get_vm(vmname)
        return not vm is None

    def start_vm(self, vmname):
        vm = self.get_vm(vmname)
        start_task = vm.PowerOn()
        if vm.runtime.powerState == 'poweredOn':
            print 'already powered on'
            return
        self._wait_for_task(start_task, self.si)

    def stop_vm(self, vm):
        if isinstance(vm, str):
            vm = self.get_vm(vm)
        stop_task = vm.PowerOff()
        if vm.runtime.powerState == 'poweredOff':
            print 'already powered off'
            return
        self._wait_for_task(stop_task, self.si)

    def get_vm_ip(self, vmname):
        vm = self.get_vm(vmname)
        ret=''
        if not vm is None:
            ret = vm.summary.guest.ipAddress

    def get_dc(self, name):
        dc_list = []
        target = self.si.content.rootFolder
        self._get_target_dc_list(target, dc_list)

        for dc in dc_list:
            if dc.name == name:
                return dc
        raise Exception('Failed to find datacenter named [%s]' % name)

    def get_host(self, host):
        h = self.get_obj(self.si.content, [vim.HostSystem], host)
        if h:
           return h
        raise Exception('Failed to find host named [%s]' % host)

    def _get_target_dc_list(self, target, dc_list):
        if dc_list is None:
            dc_list = [];
        if isinstance(target, vim.Datacenter):
            dc_list.append(target)
            return
        elif hasattr(target, 'childEntity'):
            for c in target.childEntity:
                self._get_target_dc_list(c, dc_list)

    def get_largest_free_rp(self, dc):
        viewManager = self.si.content.viewManager
        containerView = viewManager.CreateContainerView(dc, [vim.ResourcePool],
                                                        True)
        largestRp = None
        unreservedForVm = 0
        try:
            for rp in containerView.view:
                if rp.runtime.memory.unreservedForVm > unreservedForVm:
                    largestRp = rp
                    unreservedForVm = rp.runtime.memory.unreservedForVm
        finally:
            containerView.Destroy()
        if largestRp is None:
            raise Exception("Failed to find a resource pool in dc [%s]" % dc.name)
        return largestRp

    def get_rp_by_host(self, host):
        if isinstance(host, basestring):
            host = self.get_host(host)
        if host is None:
            raise Exception("Failed to find host by given name [%s]" % host)
        return host.parent.resourcePool

    def get_ds(self, dc, name):
        for ds in dc.datastore:
            try:
                if ds.name == name:
                    return ds
            except:  # Ignore datastores that have issues
                pass
        raise Exception("Failed to find %s on datacenter [%s]" % (name, dc.name))

    def get_cluster_by_datastore(self, name):
        content = self.si.RetrieveContent()
        cluster_list_view = content.viewManager.CreateContainerView(content.rootFolder, [vim.ClusterComputeResource], True)
        if cluster_list_view is None:
            return ""
        cluster_list = cluster_list_view.view
        for cluster in cluster_list:
            if len(cluster.datastore) !=0:
                for ds in cluster.datastore:
                    if ds.name == name:
                        return cluster
        raise Exception("Failed to find cluster with name [%s]" % name)
