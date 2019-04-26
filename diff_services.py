from __future__ import print_function
import pandas as pd
import sys
import argparse



__authors__ = ["harshavardhana.l@hpe.com"]
__date__ = '31/07/2018'
__description__ = '''

        
        Description: Make difference between the services before installed patches and after installed patches.
        Input file should be output of the below commands:
        ` wmic service list brief `
    
        input parameter: Two files hpsa generated csv file.
        Output: diff_before.csv diff_after.csv in current directory;
        
        Prerequisite: 
            - Anaconda installed in the local machine.
            
        How to run:
            python get_serverup.py <file_name_before> <file_name_after>
        
        For examples:
            python get_serverup_patchinfo.py file_before.csv file_after.csv
        

'''

def process_file(df, num_of_index):
    '''
    function: Parse proper info from csv file.
    input: dataframe, total no. of index
    return: list with all services info
    
    '''
    data_list = []

    for index in range(num_of_index):
        server_name = df['Server'][index]
        for row in df['Output'][index].split('\n'):

            if row:
                try:
                    service_name = row.strip().split()[1]
                    startMode = row.split()[3]
                    status = row.split()[4]
                    data_list.append([ server_name,service_name, startMode, status ] )
                except:
                    pass
                
    return data_list



def main():
    
    parser = argparse.ArgumentParser(
            description=__description__,
            epilog="Developed by {} on {}".format(", ".join(__authors__), __date__)
            )
    parser.add_argument("FILE_BEFORE", help="wmic service list brief output file ")
    parser.add_argument("FILE_AFTER", help="wmic service list brief output file" )
    
    args = parser.parse_args()
    file1 = args.FILE_BEFORE
    file2 = args.FILE_AFTER
    
    df1 = pd.read_csv(file1)
    df2 = pd.read_csv(file2)
    
    num_of_index1 = df1['Server'].count()
    num_of_index2 = df2['Server'].count()
    
    file1 = process_file( df1, num_of_index1 )
    file2 = process_file( df2, num_of_index2 )
    
    d1 = pd.DataFrame( file1 )
    d2 = pd.DataFrame( file2 )
    #remove unwanted header name  belongs to every hostname
    
    df_filter_1 = d1[~d1[2].isin(['StartMode'])] 
    df_filter_2 = d2[~d2[2].isin(['StartMode'])]
    
    #Before set difference
    ds1 = set([ tuple(line) for line in df_filter_1.values.tolist()])
    ds2 = set([ tuple(line) for line in df_filter_2.values.tolist()])
    
    #set differtence between d2 - d1
    d2_diff_d1 = pd.DataFrame(list(ds2.difference(ds1)))
    #Set difference between d1 - d2
    d1_diff_d2 = pd.DataFrame(list(ds1.difference(ds2)))
    
    d2_diff_d1.rename( columns= { 0:'hostname',1: 'service_name', 2: 'start_mode', 3:'status' }, inplace=True)

    d1_diff_d2.rename( columns= { 0:'hostname',1: 'service_name', 2: 'start_mode', 3:'status' }, inplace=True)
    
    #convert dataframe to csv output file
    d2_diff_d1.to_csv("diff_after.csv" )
    d1_diff_d2.to_csv("diff_before.csv")
    
    
    print("DONE")
    
    
    
    
if __name__ == '__main__':
    sys.exit( main() )