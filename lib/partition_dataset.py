import warnings
from pathlib import Path
from shutil import copy
import random

def ditribute(source, targets, weights, order, copy_xml):
    total_weight = sum(weights)
    images = list(source.glob('*.jpg'))  # FIXME more img formats
    if order == 'random':
        random.shuffle(images)
    elif order == 'sorted':
        images = sorted(images)
        
    image_count = len(images)
    target_count = len(targets)

    print('----------------------------------')
    print(f'From: {str(source):13}  |  count: {image_count}')
    i1 = 0
    for i, target, weight in zip(range(target_count), targets, weights):
        n = round(weight/total_weight*image_count)
        i2 = i1 + n
        if i == len(weights):
            subset = images[i1:]
        else:
            subset = images[i1:i2]
        print(f'  To: {str(target):13}  |  count: {len(subset)}')
        i1 = i2
        for file in subset:
            copy(file, target)
            if copy_xml:
                xml_file = Path(file.parent, f'{file.stem}.xml')
                if xml_file.exists():
                    copy(xml_file, target)

def partition_dataset(
        sources,
        targets,
        ratios,
        copy_xml=True,
        data='data',
        order='random'
    ):

    if not len(targets) == len(ratios):
        raise Exception('The targets and ratios lists must be of equal length')
    data = Path(data)
    sources = [Path(data, x) for x in sources]
    targets = [Path(data, x) for x in targets]
    [d.mkdir() for d in targets if not d.exists()]
    for source in sources:
        ditribute(source, targets, ratios, order, copy_xml)

def init_args():
    import argparse

    parser = argparse.ArgumentParser(
            description="Distrubute image files to muliple directories")
    parser.add_argument('-s', '--sources',
            required = True,
            type=str,
            nargs = '+',
            help='List of one or more source img file directories')
    parser.add_argument('-t', '--targets',
            required = True,
            type=str,
            nargs = '+',
            help='List of one or more directories to receive files')
    parser.add_argument('-w', '--weights',
            required = True,
            type=int,
            nargs = '+',
            help='List of weigts corresponding to the --target directories')
    parser.add_argument('-o', '--order',
            type = str,
            choices = ["random", "sorted"],
            help='Defines how files are selected from the --source directories')
    parser.add_argument( '-c', '--copy-xml',
            action='store_true',
            dest = "copy_xml",
            help='Copies xml files to the --target directories')

    args = parser.parse_args()
    return args


if __name__ == '__main__':
    args = init_args()
    partition_dataset(
        args.sources,
        args.targets,
        args.weights,
        order = args.order,
        copy_xml = args.copy_xml
    )
