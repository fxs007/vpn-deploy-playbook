import os
import sys
import yaml


def main():

    if len(sys.argv) != 4:
        print "Invalid arguments count"
        exit(1)

    yaml_file=str(sys.argv[1])
    target_key=str(sys.argv[2])
    content=str(sys.argv[3])

    stream = file(yaml_file, 'r');
    data = yaml.load(stream)
    if os.path.isfile(content):
        with file(content) as f:
            s = f.read()
    else:
        s = content

    data.get('data')[target_key] = s
    output_yaml = yaml.dump(data, default_style='|')
    ff = open(yaml_file, 'w+')
    ff.write(output_yaml)

if __name__ == '__main__':
    main()
