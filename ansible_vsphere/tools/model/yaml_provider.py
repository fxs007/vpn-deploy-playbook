from yaml import Loader, Dumper
import yaml
import os
import json

class YamlProvider(object):

    key_delimiter = None

    def __init__(self, delimiter = '|'):
        self.key_delimiter = delimiter

    def parse_properties_str(self, properties_str, output=None):
        content = [x.strip() for x in properties_str]
        yaml_str = self._process(content)
        if not output is None:
            self._out_yaml_file(yaml_str, output)
        else:
            return yaml_str

    def parse_properties_file(self, properties_file, output=None):

        if not os.path.isfile(properties_file):
            raise IOError("file not found %s " % properties_file)
            exit(1)
        with open(properties_file) as f:
            content = f.readlines()
        yaml_str = self._process(content)
        if not output is None:
            self._out_yaml_file(yaml_str, output)
        else:
            return yaml_str

    def flatten_yaml(self, yaml_file, output_file):
        dirname = os.path.dirname(output_file)
        if not os.path.isdir(dirname):
            raise IOError("directory not found: %s" % dirname)
            exit(1)

        if not os.path.isfile(yaml_file):
            raise IOError("file not found %s " % yaml_file)
            exit(1)

        stream = file(yaml_file, 'r');
        data = yaml.load(stream)
        result = []
        for k, v in data.iteritems():
            if type(v) is not dict:
                result.append(self._build_key_value(k, v))
            key = self._build_key(k)
            self._build(result, key, v)

        writer = open(output_file, 'w+')
        for r in result:
            writer.write(r + '\n')

    def _build(self, result, key, v):
        if type(v) is dict:
            for kk, vv in v.iteritems():
                cur = self._build_key(key + str(kk))
                val = self._build(result, cur, vv)
                if val is not None:
                    result.append(val)
        else:
            key = key[:-2]
            return self._build_key_value(key, v)

    def _build_key(self, s):
        return str(s) + '__'

    def _build_key_value(self, k, v):
        if v is None:
            v = ""
        ret = '"' + str(v) + '"'
        return str(k) + '=' + ret


    def _out_yaml_file(self, yaml_str, output_file):
        dirname = os.path.dirname(output_file)
        if not os.path.isdir(dirname):
            raise IOError("directory not found: %s" % dirname)
        ff = open(output_file, 'w+')
        ff.write(yaml_str)

    def _process_line(self, data, line):
        kvs = [x.strip() for x in line.split('=')]
        keys = [x.strip() for x in kvs[0].split('__')]
        d = data
        leaf = {}
        leaf_key = ""
        for k in keys:
            if not d.has_key(k):
                d[k] = {}
            leaf = d
            leaf_key = k
            d = d[k]
        leaf[leaf_key] = kvs[1]

    def _process(self, strs):
        data = {}
        content = [x.strip() for x in strs]
        for l in content:
            self._process_line(data, l)
        # print data
        return yaml.dump(data, default_flow_style=False).replace('\'','')
