import sys

from model.inventory_provider import InventoryProvider
from utils.constants import COMMA


def main():
    if len(sys.argv) < 3:
        print "invalid arguments"
        exit(1)
    inv_file = str(sys.argv[1])
    ntype = str(sys.argv[2])
    ret = COMMA.join(InventoryProvider.get_vm_names(inv_file, ntype))
    print ret
    return ret

if __name__ == '__main__':
    main()