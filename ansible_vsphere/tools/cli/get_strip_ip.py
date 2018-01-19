import sys

from model.inventory_provider import InventoryProvider
from utils.constants import COMMA


def main():
    if len(sys.argv) < 4:
        print "Invalid arguments"
        exit(1)

    inv_file = sys.argv[1]
    ntype = sys.argv[2]
    count = int(sys.argv[3])

    mips = InventoryProvider.get_vm_ips(inv_file, 'master')
    wips = InventoryProvider.get_vm_ips(inv_file, 'worker')
    ret = []
    if ntype == 'master':
        for i in range(0, count):
            ret.append(mips.pop())
    else:
        for i in range(0, count):
            ret.append(wips.pop())
    ret.reverse()
    print COMMA.join(ret)


if __name__ == '__main__':
    main()
