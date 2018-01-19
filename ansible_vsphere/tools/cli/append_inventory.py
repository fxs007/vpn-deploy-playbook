import sys

from model.inventory_provider import InventoryProvider


def main():
    if len(sys.argv) < 4:
        print "Invalid arguments"
        exit(1)
    inv_file = str(sys.argv[1])
    ntype = str(sys.argv[2])
    ips = str(sys.argv[3])

    print InventoryProvider.fill_inventory(inv_file, ips, ntype)
if __name__ == '__main__':
    main()
