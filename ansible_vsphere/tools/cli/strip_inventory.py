import sys

from model.inventory_provider import InventoryProvider
from utils.constants import COMMA

def main():
    if len(sys.argv) < 4:
        print "Invalid arguments"
        exit(1)
    inv_file = sys.argv[1]
    ntype = sys.argv[2]

    if isinstance(sys.argv[3], int):
        count = int(sys.argv[3])
    else:
        ips=sys.argv[3]
    if ips is None:
        mips=InventoryProvider.get_vm_ips(inv_file, 'master')
        wips = InventoryProvider.get_vm_ips(inv_file, 'worker')
        strip_ips=[]
        if ntype == 'master':
            for i in range(0, count):
                strip_ips.append(mips.pop())
        else:
            for i in range(0, count):
                strip_ips.append(wips.pop())
        r_ips = COMMA.join(strip_ips)
        print InventoryProvider.strip_inventory(inv_file, r_ips, ntype)
    else:
        print InventoryProvider.strip_inventory(inv_file, ips, ntype)

if __name__ == '__main__':
    main()
