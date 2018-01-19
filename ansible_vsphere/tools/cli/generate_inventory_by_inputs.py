import sys

from model.inventory_provider import InventoryProvider

def main():
    if len(sys.argv) < 5:
        print "invalid arguments"
        exit(1)
    master_ips = str(sys.argv[1])
    master_vms = str(sys.argv[2])
    worker_ips = str(sys.argv[3])
    worker_vms = str(sys.argv[4])
    m_ips = [x.strip() for x in master_ips.split(',')]
    m_vms = [x.strip() for x in master_vms.split(',')]
    w_ips = [x.strip() for x in worker_ips.split(',')]
    w_vms = [x.strip() for x in worker_vms.split(',')]

    print InventoryProvider.generate_inventory_by_input(m_ips, m_vms, w_ips, w_vms)
if __name__ == '__main__':
    main()