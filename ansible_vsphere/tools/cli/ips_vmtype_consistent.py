import sys

from model.inventory_provider import InventoryProvider
from utils.constants import COMMA


def main():
    if len(sys.argv) < 4:
        print "invalid arguments"
        exit(1)
    inv_file = str(sys.argv[1])
    ntype = str(sys.argv[2])
    ip = str(sys.argv[3])
    ips = [x.strip() for x in ip.split(',')]

    for i in ips:
        vm = InventoryProvider.get_vm_names_by_ips(inv_file, [i], ntype)
        if len(vm) == 0:
            raise Exception("ip [%s] is not a [%s] node" % (i, ntype))
            exit(1)
if __name__ == '__main__':
    main()