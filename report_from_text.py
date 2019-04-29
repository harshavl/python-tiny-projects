import os,sys
import pandas as pd



__authors__ =
__date__ = '15042019'
__description__ = '''
    input: text files
    Output: csv file
    
    Description: Parse data from mulitple text files.
    Prerequisite: 
        - Anaconda 3.7 verions
        
    How to run:
        python report_from_text.py 
        

'''

def check_dir_exists(dir_name):
    if ( os.path.isdir("./input") is False):
        os.makedirs("input")
        print("input directory created")


def get_list( line, row_num ):
    try:
        data = line[row_num]
    except:
        data = "not_mentioned"
    return data


def main():
    
    path='./input'
    files = os.listdir(path)
    
    full_data = []
    
    for file in files:
        df = pd.read_fwf( os.path.join(path, file), header=None, sep='\t')
        
        for index,line in enumerate(df[0].str.split('\t')):
        #print(index,line)
    
            if index is 0:
                line_str = str(line) 
                hostname = line_str.split('-')[1] 
                script_date = line_str.split('-')[2] 
    
            try:
                print(line[0])
            except:
                continue
            if index:
                software_name = get_list(line, 0 )
                version = get_list( line, 1 )
                data = get_list( line, 2)
    
                full_data.append( [ software_name, version,data, hostname.strip(), script_date.strip() ] )
    
    df = pd.DataFrame( full_data, columns=['software_name', 'version', 'installed_date', 'hostname', 'report_created_date'])
    df.to_csv("report.csv")
    
    
    
    
if __name__ == '__main__':
    sys.exit( main() )