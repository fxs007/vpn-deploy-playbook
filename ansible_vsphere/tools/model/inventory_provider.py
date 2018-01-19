import json
import yaml
from utils.common import Common
from utils.constants import INVENTORY_MASTER_VM_NAME_TEMPLATE, INVENTORY_WORKER_VM_NAME_TEMPLATE


class InventoryProvider(object):

    def __init__(self, cname, masterIps, workerIps):
        self.mips = masterIps
        self.wips = workerIps
        self.cname = cname


    def generate_inventory_old(self):
        data = {}
        master = {}
        worker = {}

        for index, ip in enumerate(self.mips):
            master[ip] = {'hostname': self.cname + INVENTORY_MASTER_VM_NAME_TEMPLATE + str(index + 1)}
        for index, ip in enumerate(self.wips):
            worker[ip] = {'hostname': self.cname + INVENTORY_WORKER_VM_NAME_TEMPLATE + str(index + 1)}

        data['worker'] = worker
        data['master'] = master
        return json.dumps(data)

    def generate_inventory(self):
        data = {}
        master = []
        worker = []

        for index, ip in enumerate(self.mips):
            master.append({'ip_addr': str(ip), 'hostname': InventoryProvider.generate_hostname(self.cname, INVENTORY_MASTER_VM_NAME_TEMPLATE, index + 1)})
        for index, ip in enumerate(self.wips):
            worker.append({'ip_addr': str(ip), 'hostname': InventoryProvider.generate_hostname(self.cname, INVENTORY_WORKER_VM_NAME_TEMPLATE, index + 1)})

        data['worker'] = worker
        data['master'] = master
        return json.dumps(data)
        #return yaml.dump(data, default_flow_style=False, explicit_start=True)

    @staticmethod
    def generate_inventory_by_input(m_ips, m_vms, w_ips, w_vms):
        data = {}
        master = []
        worker = []
        for idx, ip in enumerate(m_ips):
            master.append({'ip_addr': str(ip),
                   'hostname': m_vms[idx]})
        for idx, ip in enumerate(w_ips):
            worker.append({'ip_addr': str(ip),
                           'hostname': w_vms[idx]})
        master.sort(key=lambda n: n['hostname'])
        worker.sort(key=lambda n: n['hostname'])
        data['worker'] = worker
        data['master'] = master
        return json.dumps(data)

    @staticmethod
    # r_ips: ip1,ip2,ip3
    def strip_inventory(inv_file, r_ips, ntype='worker'):
        if r_ips is None or len(r_ips) == 0:
            raise Exception("Invalid ip address(es) in [%s]" % r_ips)

        ips = [x.strip() for x in r_ips.split(',')]
        for i in ips:
            if not Common.is_ip(i):
                raise Exception("Invalid ip address(es) in [%s]" % r_ips)
        with open(inv_file, 'r') as f:
            data = json.load(f)
            node = data[ntype]
            data[ntype]=list(filter(lambda n: r_ips.find(n['ip_addr']) == -1, node))
        return json.dumps(data)

    @staticmethod
    def fill_inventory(inv_file, r_ips, ntype='worker'):
        if r_ips is None or len(r_ips) == 0:
            raise Exception("Invalid ip address(es) in [%s]" % r_ips)

        ips = [x.strip() for x in r_ips.split(',')]
        for ip in ips:
            if not Common.is_ip(ip):
                raise Exception("Invalid ip address(es) in [%s]" % r_ips)
        vm_names = InventoryProvider.get_vm_names(inv_file, ntype)
        vm_names_idx = list(map(lambda idx: int(str(idx).rpartition('-')[-1]), vm_names))
        vm_names_idx.sort(lambda a, b: a - b)
        vm_names_idx_absent = []
        cname = InventoryProvider.get_cname(inv_file)
        pre = 1
        for v in vm_names_idx:
            for i in range(pre, v):
                vm_names_idx_absent.append(i)
            pre = v + 1
        vm_names_idx_absent.reverse()
        max_idx = vm_names_idx[len(vm_names_idx) - 1]
        with open(inv_file, 'r') as f:
            data = json.load(f)
            node = data[ntype]
            for nip in ips:
                if len(vm_names_idx_absent) == 0:
                    max_idx += 1
                    valid_idx = max_idx
                else:
                    valid_idx = vm_names_idx_absent.pop()
                node.append({'ip_addr': str(nip),
                             'hostname': InventoryProvider.generate_hostname(cname,
                        INVENTORY_WORKER_VM_NAME_TEMPLATE if ntype == 'worker' else INVENTORY_MASTER_VM_NAME_TEMPLATE,
                                                                     valid_idx)})
            node.sort(key=lambda n: n['hostname'])
            data[ntype] = node
        return json.dumps(data)

    @staticmethod
    def generate_hostname(cname, prefix, idx):
        return cname + prefix + str(idx)

    @staticmethod
    def get_vm_names_old(inv_file, type='master'):

        vmnames = []
        with open(inv_file, 'r') as f:
            data = json.load(f)
            node = data[type]
            for m in node:
                vmnames.append(node[m]['hostname'])
        return vmnames

    @staticmethod
    def get_vm_names(inv_file, type='master'):
        vmnames = []
        with open(inv_file, 'r') as f:
            data = json.load(f)
            #data = yaml.load(f)
            node = data[type]
            for m in node:
                vmnames.append(m['hostname'])
        #print 'vms:%s' % vmnames
        return vmnames

    @staticmethod
    def get_vm_ips(inv_file, type='master'):
        vmips = []
        with open(inv_file, 'r') as f:
            data = json.load(f)
            node = data[type]
            for m in node:
                vmips.append(m['ip_addr'])
        return vmips

    @staticmethod
    def get_vm_names_by_ips(inv_file, ips, type='master'):
        vmnames = []
        with open(inv_file, 'r') as f:
            data = json.load(f)
            node = data[type]
            for ip in ips:
                for m in node:
                    if m['ip_addr'] == ip:
                        vmnames.append(m['hostname'])
        return vmnames

    @staticmethod
    def get_cname(inv_file):
        with open(inv_file, 'r') as f:
            data = json.load(f)
            node = data['master']
            for m in node:
                vm_name=m['hostname']
                return vm_name[0:vm_name.index(INVENTORY_MASTER_VM_NAME_TEMPLATE)]

    # {"master": [{"hostname": "vvv-master-1", "ip_addr": "10.74.68.5"}],
    #  "worker": [{"hostname": "vvv-worker-1", "ip_addr": "10.74.68.6"}]}
    @staticmethod
    def validate_ips(ips):
        for ip in ips:
            if not Common.is_ip(ip):
                print "not valid ip: %s" % ip
                return False
            else:
                return True