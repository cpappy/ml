import re

class ConfigEditor():
    def __init__(self, spec_file):
        specs = {}
        with open(spec_file) as f:
            lines = f.read().split('\n')
            for line in lines:
                line = re.sub('\s*#.*', '', line)
                if line:
                    key, value = re.split('\s*=\s*', line)
                    key = key.strip()
                    key = re.sub('\s*/\s*', '/', key)
                    specs[key] = value
        self.specs = specs

    def edit(self, input_file, output_file):

        # Read the file to be edited, input_file
        with open(input_file) as f:
            lines = [line.rstrip() for line in f]

        # Edit each line and write to the output file
        with open(output_file, 'w') as f:
            path = []
            for line in lines:

                # Comment or blank line
                if re.match('^\s*$', line) or re.match('^\s*#.*$', line):
                    f.write(f'{line}\n')
                    continue

                # Line like "name [:] {"
                m = re.search('^\s*(.*?)\s+{\s*$', line)
                if m:
                    token = m[1]
                    name  = re.sub('\s*:\s*', '', token)
                    path.append(name)
                    f.write(f'{line}\n')
                    continue

                m = re.match('^\s*}\s*$', line)
                # Line with a closing "}"
                if m:
                    token = path.pop()
                    f.write(f'{line}\n')
                    continue

                # Line like "name: value"
                m = re.match('^(\s*)([_a-zA-Z0-9]+\s*):(.*)$', line)
                if m:
                    space, token, the_rest = m[1], m[2], m[3]
                    m = re.search('(#.*)', the_rest)
                    if m:
                        comments = m[1]
                    else:
                        comments = ""
                    key = '/'.join(path + [token])
                    value = self.specs.get(key)
                    if value:
                        f.write(f'{space}{token}: {value} {comments}\n')
                    else:
                        f.write(f'{line}\n')
                    continue

                else:
                    raise Exception(f'Unrecognized line:\n{line}')

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        prog = "TnsorFlow pipeline config editor",
        usage = "%(prog)s EDIT-SPEC IMPUT-CONFIG PUTPUT-CONFIG",
        description = ("Apply edits in EDIT-SPEC to IMPUT-CONFIG" 
                       " and create PUTPUT-CONFIG")
    )
    parser.add_argument('edit_file')
    parser.add_argument('input_file')
    parser.add_argument('output_file')

    args = parser.parse_args()

    editor = ConfigEditor(args.edit_file)
    editor.edit(args.input_file, args.output_file)

    print(f'Created file {args.output_file}')

