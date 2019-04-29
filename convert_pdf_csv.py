from __future__ import print_function
from tabula import convert_into
import os,sys
from tqdm import tqdm


__authors__ = 
__date__ = '19032019'
__description__ = '''
    input: pdf files
    Output: csv files
    
    Description: Parse tables from pdf files and convert to csv files.
    Prerequisite: 
        - Python version:
            3.7.1 (default, Dec 10 2018, 22:54:23) [MSC v.1915 64 bit (AMD64)]
        - Java version:
            java version "1.8.0_202"
        - Java(TM) SE Runtime Environment (build 1.8.0_202-b08)
        - Java HotSpot(TM) 64-Bit Server VM (build 25.202-b08, mixed mode)
            tabula-py version: 1.3.1
        - platform: Windows-10-10.0.17134-SP0
        
    How to run:
        python convert_pdf_csv.py 
        

'''

def check_dir_exists(dir_name):
    if ( os.path.isdir("./input") is False):
        os.makedirs("input")
        print("input directory created")
    if (os.path.isdir("./output") is False ):
        os.makedirs("output")
        print("output directory created")
        
def replace_filenames():
    path = './input'
    files = os.listdir(path)
    for file in files:
        file_new = file.replace(' ','')
        os.rename(os.path.join(path, file), os.path.join(path, file_new))
        


def main():
    
    for file in tqdm(os.listdir("./input")):
        input_file="./input/{}".format(file)
    
        output_dir = "./output/{}".format(file)
        file_out= output_dir.replace('pdf','csv')
        print("Processing:",file_out)
        convert_into(input_file, file_out, output_format='csv', multiple_tables=True, pages='all' )
        
        



if __name__ == '__main__':
    sys.exit( main() )