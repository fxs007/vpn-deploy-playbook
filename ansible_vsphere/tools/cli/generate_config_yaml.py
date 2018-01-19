import os
import sys
from model.yaml_provider import YamlProvider

def main():

    if len(sys.argv) > 3 or len(sys.argv) < 2:
        print "Invalid arguments count"
        exit(1)

    config = str(sys.argv[1])
    parser = YamlProvider()


    if len(sys.argv) == 3:
        output_file = str(sys.argv[2])
        if not os.path.dirname(output_file):
            parser.parse_properties_str(config, output_file)
        else:
            parser.parse_properties_file(config, output_file)
    else:
        if not os.path.dirname(config):
            print parser.parse_properties_str(config)
        else:
            print parser.parse_properties_file(config)

if __name__ == '__main__':
    main()