import sys

sys.path.append('/usr/bin/findit.d/provision/tools')
from model.inventory_provider import InventoryProvider


def main():
    cname = str(sys.argv[1])
    master_ips = str(sys.argv[2])
    worker_ips = str(sys.argv[3])
    old_invs = False
    if (len(sys.argv) == 5):
        old_invs = True

    if master_ips is None \
            or worker_ips is None \
            or cname is None:
        print 'Invalid arguments'
        exit(1)

    mips = [x.strip() for x in master_ips.split(',')]
    wips = [x.strip() for x in worker_ips.split(',')]
    if not InventoryProvider.validate_ips(mips) or not InventoryProvider.validate_ips(wips):
        exit(1)
    inp = InventoryProvider(cname, mips, wips)

    if old_invs:
        print inp.generate_inventory_old()
    else:
        print inp.generate_inventory()
if __name__ == '__main__':
    main()
