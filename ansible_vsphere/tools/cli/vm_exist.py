import sys
from pyVmomi import vim, vmodl
from model.vmmanager import VMManager

def main():
    print "arg count: %s" % len(sys.argv)
    if len(sys.argv) != 5:
        print "invalid arguments, arg count: %s" % len(sys.argv)
        exit(1)

    vmmanager = VMManager()
    vip = str(sys.argv[1])
    vuser = str(sys.argv[2])
    vpwd = str(sys.argv[3])
    vm_name = str(sys.argv[4])

    try:
        vmmanager.connect(vip, vuser, vpwd)
        if vmmanager.exist_vm(vm_name):
            return
        else:
            exit(1)
    except Exception as e:
        print "Caught exception: %s" % str(e)
        exit(1)

# Start program
if __name__ == "__main__":
    main()
