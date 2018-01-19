import sys
from pyVmomi import vim, vmodl
from model.vmmanager import VMManager

def main():

    print "arg count: %s" % len(sys.argv)
    if len(sys.argv) != 7 and len(sys.argv) != 8:
        print "invalid arguments, arg count: %s" % len(sys.argv)
        exit(1)

    vmmanager = VMManager()
    vip = str(sys.argv[1])
    vuser = str(sys.argv[2])
    vpwd = str(sys.argv[3])
    dc = str(sys.argv[4])
    r_type = str(sys.argv[5]) # valid values: ds, dc, host, net
    r_name = str(sys.argv[6])
    if len(sys.argv) == 8:
        r_arg = str(sys.argv[7])
    else:
        r_arg = None

    try:
        vmmanager.connect(vip, vuser, vpwd)
        dc_obj = vmmanager.get_dc(dc)
        if not dc_obj:
            print "Invalid datacenter name [%s]" % r_name
            exit(1)
        if r_type == 'ds':
            ds_obj = vmmanager.get_ds(dc_obj, r_name)
            if not ds_obj:
                print "Invalid datastore name [%s]" % r_name
                exit(1)
        elif r_type == 'host':
            obj_host = vmmanager.get_host(r_name)
            if not obj_host:
                print "Invalid host name [%s]" % r_name
                exit(1)
        elif r_type == 'net':
            # r_arg is the specific host name
            if r_arg is None:
                print "Invalid network name [%s]" % r_name
                exit(1)
            obj_host = vmmanager.get_network_by_host(r_arg, r_name)
            if not obj_host:
                print "Invalid network name [%s]" % r_name
                exit(1)
        else:
            print "Invalid arguments: only ds, dc, host and net are supported to query"
        print "Valid VMWare resource: [type=%s, name=%s]" % (r_type, r_name)
    except Exception as e:
        print "Caught exception: %s" % str(e)
        exit(1)
    except:
        print "Unexpected error: %s" % sys.exc_info()[0]

# Start program
if __name__ == "__main__":
    main()
