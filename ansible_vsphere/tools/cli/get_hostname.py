import sys
from pyVmomi import vim, vmodl
from model.vmmanager import VMManager

def main():
    #
    if len(sys.argv) != 5:
        print "invalid arguments"
        exit(1)

    vmmanager = VMManager()
    vip = str(sys.argv[1])
    vuser = str(sys.argv[2])
    vpwd = str(sys.argv[3])
    datastore = str(sys.argv[4])
    try:
        vmmanager.connect(vip, vuser, vpwd)
        result = vmmanager.get_hostname(datastore)
        if result is None:
            print "not found datastore [%s]" % datastore
            exit(1)
        else:
            print result

    except Exception as e:
        print "Caught exception: %s" % str(e)
        exit(1)

# Start program
if __name__ == "__main__":
    main()
