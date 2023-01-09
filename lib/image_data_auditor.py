"""
VOC xml annotation file example:

<annotation> 
  <folder>Train</folder> 
  <filename>01.png</filename>      
  <path>/path/Train/01.png</path> 
  <source>  
    <database>Unknown</database> 
  </source>
  <size>  
    <width>224</width>  
    <height>224</height>  
    <depth>3</depth>   
  </size> 
  <segmented>0</segmented> 
  <object>  
    <name>36</name>  
    <pose>Frontal</pose>  
    <truncated>0</truncated>  
    <difficult>0</difficult>  
    <occluded>0</occluded>  
    <bndbox>   
      <xmin>90</xmin>   
      <xmax>190</xmax>   
      <ymin>54</ymin>   
      <ymax>70</ymax>  
    </bndbox> 
  </object>
</annotation>
"""

import re
from pathlib import Path
import xml.etree.ElementTree as ET
from PIL import Image

from pprint import pprint as pp

def get_xml_size(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    width = int(root.find('size/width').text)
    height = int(root.find('size/height').text)
    return width,height

def update_xml(img_file, xml_file, size):
    width, height = size
    tree = ET.parse(xml_file)
    root = tree.getroot()


    root.find('folder').text      = str(img_file.parent)
    root.find('filename').text    = str(img_file.name)
    root.find('path').text        = str(img_file.resolve())
    root.find('size/width').text  = str(width)
    root.find('size/height').text = str(height)

    xml_str = ET.tostring(root, encoding='unicode')
    return xml_str

def get_img_size(img_file):
    im = Image.open(img_file)
    return im.size

def audit(images,
        annotations: str  = None,
        repair:      bool = False,
        pad:         bool = False,
        pad_size:    int  = 3,
    ) -> None:

    if annotations is None:
        annotations = images

    image_path = Path(images)
    annot_path = Path(annotations)

    annot_pat = re.compile(f'{annotations}/(.*?)(\d+).xml')
    image_pat = re.compile(f'{images}/(.*?)(\d+).jpg') # FIXME: accept png, etc
    for xml_file in annot_path.glob('*.xml'):
        #print('-----------------------------')
        m = re.match(annot_pat, str(xml_file))
        if m:
            name, number = m[1], m[2]
            img_file = Path(images, f'{name}{number}.jpg')
            if not img_file.exists():
                print(f'Warning: Image file {img_file} is missing')

            # ---------------------------------------------------------
            # Pad the xml and image file numbers with zeros
            if pad:
                # Pad the file number
                padded = f'{number:0>{pad_size}}'

                new_name = re.sub(f'{number}.xml', f'{padded}.xml',
                        str(xml_file))
                xml_file.rename(new_name)
                xml_file = Path(new_name)

                new_name = re.sub(f'{number}.jpg', f'{padded}.jpg',
                        str(img_file))
                img_file.rename(new_name)
                img_file = Path(new_name)

            # ---------------------------------------------------------
            if repair:
                # Make sure the width and height in the xml file are
                # correct
                img_size = get_img_size(img_file)
                xml_size = get_xml_size(xml_file)
                xml_str = update_xml(img_file, xml_file, img_size)
                Path(xml_file).write_text(xml_str)

            # ---------------------------------------------------------
            #  Check for consistency between the actual image size
            #  and the size specified in the xml file.
            img_size = get_img_size(img_file)
            xml_size = get_xml_size(xml_file)
            if xml_size != img_size:
                print('WARNING: source image size is wrong:')
                print('    xml file:', xml_file)
                print('    Size in xml file is:', xml_size)
                print('    Size of img file is:', img_size)
        else:
            raise Exception('No match for file:' + xml_file)

def init_args():
    import argparse

    parser = argparse.ArgumentParser(
        prog = "annotated image auditor",
        usage="%(prog)s [OPTIONS] DIRECTORY",
        description="Check annotated images and optionally fix any errots")

    parser.add_argument('images')

    parser.add_argument('--annotations')
    parser.add_argument('--repair',    action='store_true')
    parser.add_argument('--no-repair', action='store_false', dest='repair')
    parser.set_defaults(pad=True)

    parser.add_argument('--pad',    action='store_true')
    parser.add_argument('--no-pad', action='store_false', dest='pad')
    parser.set_defaults(pad=True)

    parser.add_argument('--pad-size', type=int, dest='pad_size', default=3)

    args = parser.parse_args()
    return args

def main():
    args = init_args()
    audit(args.images,
        annotations = args.annotations,
        repair = args.repair,
        pad = args.pad,
        pad_size = args.pad_size,
    )

    if args.annotations:
        target = args.annotations
    else:
        target = args.images
    print(f'Audited  files in directory {target}')

if __name__ == '__main__':
    main()
