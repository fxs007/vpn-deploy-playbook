import os
import os.path
import ssl
import sys
import tarfile
import os
import xml.etree.ElementTree as ET

from threading import Timer

from pyVmomi import vim, vmodl
# from six.moves.urllib.request import Request, urlopen
from urllib2 import Request, urlopen

from model.file_handler import FileHandler

class OvfHandler(object):
    vmname = None
    def __init__(self, ovafile, vm_name=None):
        self.handle = self._create_file_handle(ovafile)
        self.tarfile = tarfile.open(fileobj=self.handle)
        ovffilename = list(filter(lambda x: x.endswith(".ovf"),
                                  self.tarfile.getnames()))[0]
        ovffile = self.tarfile.extractfile(ovffilename)
        ovfdesc = ovffile.read().decode()
        xml = ET.fromstring(ovfdesc)
        vmname_tag = xml.find(
            './/{http://schemas.dmtf.org/ovf/envelope/1}VirtualSystem/{http://schemas.dmtf.org/ovf/envelope/1}Name')
        if vm_name:
            vmname_tag.text = vm_name
            ET.tostring(xml, 'utf-8')
            self.vmname = vm_name
            self.descriptor = ET.tostring(xml, 'utf-8')
        else:
            self.vmname = vmname_tag.text
            self.descriptor = ovfdesc

    def _create_file_handle(self, entry):
        if os.path.exists(entry):
            return FileHandler(entry)
        else:
            raise Exception("file not found: %s" % entry)

    def get_descriptor(self):
        return self.descriptor

    def set_spec(self, spec):
        self.spec = spec

    def get_disk(self, fileItem, lease):
        ovffilename = list(filter(lambda x: x == fileItem.path,
                                  self.tarfile.getnames()))[0]
        return self.tarfile.extractfile(ovffilename)

    def get_device_url(self, fileItem, lease):
        for deviceUrl in lease.info.deviceUrl:
            if deviceUrl.importKey == fileItem.deviceId:
                return deviceUrl
        raise Exception("Failed to find deviceUrl for file %s" % fileItem.path)

    def upload_disks(self, lease, host):
        self.lease = lease
        try:
            self.start_timer()
            for fileItem in self.spec.fileItem:
                self.upload_disk(fileItem, lease, host)
            lease.Complete()
            print("Finished deploy successfully.")
            return 0
        except vmodl.MethodFault as e:
            print("Hit an error in upload: %s" % e)
            lease.Abort(e)
        except Exception as e:
            print("Lease: %s" % lease.info)
            print("Hit an error in upload: %s" % e)
            lease.Abort(vmodl.fault.SystemError(reason=str(e)))
            raise
        return 1

    def upload_disk(self, fileItem, lease, host):
        ovffile = self.get_disk(fileItem, lease)
        if ovffile is None:
            return
        deviceUrl = self.get_device_url(fileItem, lease)
        url = deviceUrl.url.replace('*', host)
        headers = {'Content-length': self.get_tarfile_size(ovffile)}
        if hasattr(ssl, '_create_unverified_context'):
            sslContext = ssl._create_unverified_context()
        else:
            sslContext = None
        req = Request(url, ovffile, headers)
        urlopen(req, context=sslContext)

    def start_timer(self):
        Timer(5, self.timer).start()

    def timer(self):
        try:
            prog = self.handle.progress()
            self.lease.Progress(prog)
            if self.lease.state not in [vim.HttpNfcLease.State.done,
                                        vim.HttpNfcLease.State.error]:
                self.start_timer()
            sys.stderr.write("Progress: %d%%\r" % prog)
        except:  # Any exception means we should stop updating progress.
            pass

    def get_tarfile_size(self, tarfile):
        if hasattr(tarfile, 'size'):
            return tarfile.size
        size = tarfile.seek(0, 2)
        tarfile.seek(0, 0)
        return size

