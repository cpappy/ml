from pathlib import Path
from glob import glob
import csv
import pandas as pd
from xml.etree import ElementTree

class Parser():
    def __init__(self, path):
        path = Path(path)

        rows = [['filename', 'width', 'height', 'class',
                'xmin', 'ymin', 'xmax', 'ymax']]
        for file in path.glob('*.xml'):
            root = ElementTree.parse(file).getroot()
            for member in root.findall('object'):
                row = (
                        root.find('path').text,
                        int(root.find('size')[0].text),
                        int(root.find('size')[1].text),
                        member[0].text,
                        int(member[4][0].text),
                        int(member[4][1].text),
                        int(member[4][2].text),
                        int(member[4][3].text)
                    )
                rows.append(row)
        self.rows = rows

    def write_csv(self, path):
        with open(Path(path), 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(self.rows)

    def get_df(self):
        df = pd.DataFrame(self.rows)
        return df

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        prog = "xml annotation parser",
        usage="%(prog)s [OPTIONS] DIRECTORY",
        description="Parse annotation xml files and create a csv file",
    )
    parser.add_argument('xml_dir')
    parser.add_argument('csv_path')

    args = parser.parse_args()

    p = Parser(args.xml_dir)
    p.write_csv(args.csv_path)

    print(f'Created csv file: {args.csv_path}')
