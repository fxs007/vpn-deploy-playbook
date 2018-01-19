import os
import sys
from model.yaml_provider import YamlProvider

def main():

    if len(sys.argv) > 3:
        print "Invalid arguments count"
        exit(1)

    yaml_file = str(sys.argv[1])
    output_file = str(sys.argv[2])

    parser = YamlProvider()
    parser.flatten_yaml(yaml_file, output_file)
if __name__ == '__main__':
    main()