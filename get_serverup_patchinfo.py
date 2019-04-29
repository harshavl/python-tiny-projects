from __future__ import print_function
import pandas as pd
import time,sys
import argparse
import datetime as DT


__authors__ = 
__date__ = '26/07/2018'
__description__ = '''
    input parameter: hpsa generated text file and date
    Output: output.csv
    
    Description: Get the previous ( parameter passed) installed patch name, date, server up time and hostname;
    input file should be output of below commands:
        
        systeminfo | find "System Boot Time:"
        wmic qfe | findstr "http"

    
    Prerequisite: 
        - Anaconda installed in the local machine.
        
    How to run:
        python get_serverup.py <file_name> <date>
    
    For examples:
        python get_serverup_patchinfo.py 07/16/2018
        

'''

def hex_to_datetime(hex_num):
    '''
        function: convert hex date format to readable format.
        input: hex date
        output: readable format
    '''
    num = int( hex_num, 16 )
    timestamp = num / pow( 10, 8 )
    time_tuple = time.gmtime(timestamp)
    return time.strftime("%m/%d/%y ", time_tuple)



def convertfile_to_properformat(file_name):
    '''
        function: Convert file to proper format;
        file_name: hpsa generated file.
        return: updated new file.
    '''
    
    with open(file_name, 'r' ) as file:
        filedata = file.read()
    #replace target string
    filedata = filedata.replace('Success', 'Success\n')
    # Write the file out again
    with open('file.txt', 'w') as file:
      file.write(filedata)


def generate_outputfile(parse_date):
    '''
    function: Generate output csv file with previous patch installed info.
    input: previous date
    output: output csv file
    
    '''
    with open('file.txt', 'r') as f: 
        data_list = []
        
        for line in f:
            #get system boot time
            if "System Boot Time" in line:
                system_boot = line.replace("System Boot Time:", "").strip()
     
            if line.startswith("http"):
                
                patch = line.split('\n')[0]
                patch_name = patch.rstrip().split(' ')[0]
                all_date = patch.rstrip().split(' ')[-1]
                host = patch.rstrip().split(' ', 1)[1]
                host_name = host.lstrip().split(' ')[0]
                
                if not '/' in all_date:
                    date_time = hex_to_datetime(all_date)
                else:
                    date_time = all_date
                    
                data_list.append([date_time, host_name, patch_name,  system_boot] )
                
        df = pd.DataFrame( data_list, columns=['date', 'hostname', 'patch_name','server_time'] )
        df['date'] = pd.to_datetime(df['date'])
        df.index = df['date']
        del df['date']
        
        df[parse_date].to_csv('output.csv')
    
    



def main():
    
    parser = argparse.ArgumentParser(
            description=__description__,
            epilog="Developed by {} on {}".format(", ".join(__authors__), __date__)
            )
    parser.add_argument("FILE", help="wmic qfe | findstr http output file ")
    parser.add_argument("DATE", help="previous date format" )
    
    args = parser.parse_args()
    file = args.FILE
    date_format = args.DATE
    
    today = DT.date.today()
    week_ago = today - DT.timedelta(days= int(date_format))
    date_format_str = week_ago.strftime("%Y/%m/%d") 

    
    print("Please wait processing file")
    convertfile_to_properformat(file)
    generate_outputfile( date_format_str )
    
    print("DONE")
    
    
    
if __name__ == '__main__':
    sys.exit( main() )
    
    
    