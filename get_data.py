import os,sys
import pandas as pd
from glob import glob
import numpy as np




__authors__ = ["harshavardhana.l@hpe.com"]
__date__ = '22042019'
__description__ = '''
    input: text files
    Output: csv file
    
    Description: Parse data from mulitple text files.
    Prerequisite: 
        - Anaconda 3.7 verions
        
    How to run:
        python get_data.py 
        
'''

def check_dir_exists(dir_name):
    if ( os.path.isdir("./input") is False):
        os.makedirs("input")
        print("input directory created")
        
        

def main():
    
    filenames = sorted(glob(os.path.join('input','*.txt')))
    full_data = []

    for fn in filenames:
        print("Processing file:{}".format(fn))
        df = pd.read_csv( fn, header=None)
    
        for index,line in enumerate(df[0].str.split('\t')):
            if line is not np.nan and len(line) > 1:
                full_data.append(line)
            
    df_1 = pd.DataFrame( full_data, columns=['hostname', 'domain','user_domain','group_name','user_name','fullname','description','enbled_disabled'] )
    df_1.to_csv('output_report.csv', sep=',')
        
    
if __name__ == '__main__':
    sys.exit( main() )
