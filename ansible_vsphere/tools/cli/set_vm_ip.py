import sys
import time
from pyVmomi import vim, vmodl
from model.vmmanager import VMManager

def main():

    if len(sys.argv) < 7 or len(sys.argv) > 10:
        print "invalid arguments"
        return 1

    vmmanager = VMManager()
    vip = str(sys.argv[1])
    vuser = str(sys.argv[2])
    vpwd = str(sys.argv[3])
    vmname = str(sys.argv[4])
    vmip = str(sys.argv[5])
    vmdns = str(sys.argv[6])
    dnsdomain = None
    nmask = None
    gateway = None
    if len(sys.argv) > 7:
        dnsdomain = str(sys.argv[7])
    if len(sys.argv) > 8:
        nmask = str(sys.argv[8])
    if len(sys.argv) > 9:
        gateway = str(sys.argv[9])

    vmnames = [x.strip() for x in vmname.split(',')]
    vmips = [x.strip() for x in vmip.split(',')]
    dnsList = [x.strip() for x in vmdns.split(',')]

    vmnames_len = len(vmnames)
    vmips_len = len(vmips)
    short = vmnames_len
    if vmnames_len < 1 or vmips_len < 1:
        print "invalid argument: [vmname, vmip]"
        exit(1)

    if short >= vmips_len:
        short = vmips_len
    print "vmnames:%s" % vmnames
    print "vmips:%s" % vmips
    print "dnsList:%s, dnsdomain:%s, nmask:%s, gateway:%s" % (dnsList, dnsdomain, nmask, gateway)
    try:
        vmmanager.connect(vip, vuser, vpwd)
        i = 0
        while i < short:
            print "start to set ip %s to vm %s" % (vmips[i], vmnames[i])
            time.sleep(20)
            vmmanager.stop_vm(vmnames[i])
            vmmanager.set_ip(vmnames[i], vmips[i], dnsList, dnsdomain, nmask, gateway)
            vmmanager.start_vm(vmnames[i])
            print "set ip %s to vm %s completed" % (vmips[i], vmnames[i])
            i = i + 1
    except Exception as e:
        print "Caught exception: %s" % str(e)
        exit(1)

# Start program
if __name__ == "__main__":
    main()
