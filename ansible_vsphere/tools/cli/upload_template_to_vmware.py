import sys
from pyVmomi import vim, vmodl
from model.vmmanager import VMManager

def main():

    print "arg count: %s" % len(sys.argv)
    if len(sys.argv) != 11 and len(sys.argv) != 12:
        print "invalid arguments, arg count: %s" % len(sys.argv)
        exit(1)

    vmmanager = VMManager()
    vip = str(sys.argv[1])
    vuser = str(sys.argv[2])
    vpwd = str(sys.argv[3])
    datacenter = str(sys.argv[4])
    datastore = str(sys.argv[5])
    ova_path = str(sys.argv[6])
    vm_name = str(sys.argv[7])
    template_name = str(sys.argv[8])
    host = str(sys.argv[9])
    net_to = str(sys.argv[10])
    if len(sys.argv) == 12:
        net_from = str(sys.argv[11])
    else:
        net_from = 'VM Network 10'
    print "net_from: %s" % net_from
    print "net_to: %s" % net_to
    print "host: %s" % host
    print "vm_name: %s" % vm_name

    try:
        vmmanager.connect(vip, vuser, vpwd)
        # remove temp vm if exist
        if vmmanager.exist_vm(vm_name):
            vmmanager.remove_vm(vm_name)
        ret = vmmanager.upload_ova(datacenter, datastore, host, ova_path, vm_name, net_from, net_to)
        if ret == 1:
            raise Exception("failed to upload ova [%s]" % ova_path)
        ret = vmmanager.clone_vm_to_template(datacenter, host, datastore, vm_name, template_name)
        if ret == 1:
            raise Exception("failed to clone the uploaded vm [%s] to template [%s]" % (vm_name, template_name))
        ret = vmmanager.remove_vm(vm_name)
        if ret == 1:
            raise Exception("failed to remove the vm [%s]" % vm_name)
    except Exception as e:
        print "Caught exception: %s" % str(e)
        exit(1)

# Start program
if __name__ == "__main__":
    main()
