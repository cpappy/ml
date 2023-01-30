import re

def _read_edit_specs(edit_spec_file):
    edit_specs = {}
    with open(edit_spec_file) as f:
        for spec in f.read().split('\n'):
            spec = re.sub('\s*#.*', '', spec)
            if spec:
                m = re.match('([^:]*)\s*/\s*(.*)', spec)
                if m:
                    keys = re.sub('\s*', '', m[1]).split('/')
                    m = re.match('(.*?)\s*:\s*(.*)', m[2].strip())
                    if m:
                        name, value = m[1], m[2]
                        keys.append(name)
                        edit_specs['/'.join(keys)] = value
                        continue
                raise Exception(f'Invalid edit spec:\n{spec}')
    return edit_specs

def _edit(edit_specs, lines):
    path = []
    for i, line in enumerate(lines):
        # ----- Comment or blank line
        if re.match('^\s*$', line) or re.match('^\s*#.*$', line):
            continue

        # ----- Line like "   name {"
        m = re.search('^\s*(.*?)\s+{\s*$', line)
        if m:
            path.append(m[1])
            continue

        # ----- Line with a closing "}"
        m = re.match('^\s*}\s*$', line)
        if m:
            path.pop()
            continue

        # ----- Line like "name: value"
        m = re.match('^\s*([_a-zA-Z0-9]+\s*):(.*)$', line)
        if m:
            token, the_rest = m[1], m[2]
            m = re.search('(#.*)', the_rest)
            comments = ' ' + m[1] if m else ''
            key = '/'.join(path + [token])
            value = edit_specs.get(key)
            if value:
                print('\nLine', i)
                edited = f'{token}: {value}{comments}'
                print('changed:', lines[i].lstrip())
                print('to:     ', edited)
                lines[i] = edited
                del(edit_specs[key])
        else:
            raise Exception(f'Unrecognized line:\n{line}')

def _insert(key, value, lines):
    parts = key.split('/')
    match = '/'.join(parts[0:-1])
    name = parts[-1]

    path = []
    for i, line in enumerate(lines):
        # ----- Comment or blank line
        if re.match('^\s*$', line) or re.match('^\s*#.*$', line):
            continue

        # ----- Line like "   name {"
        m = re.search('^\s*(.*?)\s+{\s*$', line)
        if m:
            path.append(m[1])
            if match == '/'.join(path):
                newline = f'{name}: {value}'
                print(f'\nLine {i+1}')
                print('Added:  ', newline)
                lines.insert(i+1, newline)
            continue

        # ----- Line with a closing "}"
        m = re.match('^\s*}\s*$', line)
        if m:
            path.pop()

def edit_pipeline_config(edit_spec_file, input_file, output_file):
    edit_specs = _read_edit_specs(args.edit_spec_file)

    # Read the the file to me edited.
    with open(args.input_file) as f:
        lines = [line.rstrip() for line in f]

    _edit(edit_specs, lines)

    for key, value in edit_specs.items():
        _insert(key, value, lines)

    with open(args.output_file, 'w') as f:
        for line in lines:
            f.write(line + '\n')

    print('\nCreated edited file:', args.output_file)

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        prog = "TnsorFlow pipeline config editor",
        usage = "%(prog)s EDIT-SPEC-FILE IMPUT-CONFIG-FILE PUTPUT-CONFIG-FILE",
        description = ("Apply edits definted in  EDIT-SPEC-FILE to IMPUT-CONFIG-FILE" 
                       " and create PUTPUT-CONFIG-FILE")
    )
    parser.add_argument('edit_spec_file')
    parser.add_argument('input_file')
    parser.add_argument('output_file')

    args = parser.parse_args()

    edit_pipeline_config(args.edit_spec_file, args.input_file, args.output_file)
