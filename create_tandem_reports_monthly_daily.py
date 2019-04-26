from __future__ import print_function
import argparse
import win32com.client
import sys,os,time
import datetime as dt
import pandas as pd
from dateutil.parser import parse
#from datetime import datetime
from dateutil.relativedelta import relativedelta
import warnings
#warnings.filterwarnings('error')


__authors__ = ["harshavardhana.l@hpe.com"]
__date__ = '15032019'
__description__ = '''
    input: outlook mail box
    Output: Avg data of CPU and Disk from mail box.
    
    Description: 
    
    
    Prerequisite: 
        - Anaconda installed in the local machine.
    How to run:
        python create_tandem_reports_monthly_daily.py <2019-01>
        

'''

def check_directoty_exists():
  
    if ( os.path.isdir("./outputfiles/") is False ):
        os.makedirs("outputfiles")
        print("./outputfiles folder created in the current directory")
    if (os.path.isdir("./supportfiles//") is False ):
        os.makedirs("supportfiles")
        print(" './supportfiles' folder created in the current diretory ")
    if (os.path.isdir("./outputfiles/cpu_per_day") is False):
        os.makedirs("./outputfiles/cpu_per_day")
        print("./outputfiles/cpu_per_day folder created")
    if (os.path.isdir("./outputfiles/cpu_per_hour") is False):
        os.makedirs("./outputfiles/cpu_per_hour")
        print("./outputfiles/cpu_per_hour folder created")
    if (os.path.isdir("./outputfiles/disk_per_day") is False ):
        os.makedirs("./outputfiles/disk_per_day")
        
        
        
def create_cpu_output(filename_hour,filename_day, mail_date, data_list, message_date):
    '''
    function: Calculate Mean per day and transfer to csv file
    input: List
    return: mean copied to csv file
    
    '''
    columns = [ 'id','time','unknown','busy','memcap','memfree','cpulength']
    
    df = pd.DataFrame(data_list, columns=columns)
    #convert list to dataframe
    df.to_excel("./supportfiles/cpu_temp.xlsx")
    try:
        df = pd.read_excel("./supportfiles/cpu_temp.xlsx")
    except:
        print("CPU file not exists")

    try:
        #df[[ 'id','unknown','busy','memcap','memfree','cpulength' ]] = df[[ 'id','unknown','busy','memcap','memfree','cpulength' ]].apply(pd.to_numeric)
        df_new = df[[ 'id','unknown','busy','memcap','memfree','cpulength' ]].apply( pd.to_numeric, errors='coerce' )
        df_new.fillna(0, inplace=True)
        
    except:
        print("ERROR:CPU data missing in the e-mail")
	
    df_new['time'] = df['time']
    df_new.index = df_new['time']
    del df_new['time']
    df_new.index = pd.to_datetime(df_new.index)
    
    #Parse data for CPU 0
    df_cpu_0 = df_new[df_new['unknown'] == 0 ]
    df_cpu_0_hour = df_cpu_0.resample('H').agg(['mean','max','min'])
    #df_cpu_0_hour = df_cpu_0_hour.drop('unknown', 1)
    df_cpu_0_day = df_cpu_0.resample('D').agg(['mean','max','min'])
    #df_cpu_0_day = df_cpu_0_day.drop('unknown', 1)
    
    df_cpu_0_hour.reset_index(inplace=True)
    df_cpu_0_memcap = df_cpu_0_hour['memcap']['mean']
    df_cpu_0_memfree = df_cpu_0_hour['memfree']['mean']
    diff_cpu0_memcap_memfree = df_cpu_0_memcap - df_cpu_0_memfree
    
    df_cpu_0_hour['difference_memcap_memfree_(MB)'] = diff_cpu0_memcap_memfree
    
    df_cpu_0_day.reset_index(inplace=True)
   
    df_cpu_0_day_memcap = df_cpu_0_day['memcap']['mean']
    
    df_cpu_0_day_memfree = df_cpu_0_day['memfree']['mean']
    
    diff_daycpu0_memcap_memfree = df_cpu_0_day_memcap - df_cpu_0_day_memfree
    df_cpu_0_day['difference_memecap_memfree_(MB)'] = diff_daycpu0_memcap_memfree
    
    #Parse data for cpu name 1
    df_cpu_1 = df_new[df_new['unknown'] == 1 ]
    df_cpu_1_hour = df_cpu_1.resample('H').agg(['mean','max','min'])
    #df_cpu_1_hour = df_cpu_1_hour.drop('unknown', 1)
    df_cpu_1_day = df_cpu_1.resample('D').agg(['mean','max','min'])
    #df_cpu_1_day = df_cpu_1_day.drop('unknown', 1)

    df_cpu_1_hour.reset_index(inplace=True)
    df_cpu_1_memcap = df_cpu_1_hour['memcap']['mean']
    df_cpu_1_memfree = df_cpu_1_hour['memfree']['mean']
    diff_cpu1_memcap_memfree = df_cpu_1_memcap - df_cpu_1_memfree
 
    df_cpu_1_hour['difference_memcap_memfree_(MB)'] = diff_cpu1_memcap_memfree
   
    df_cpu_1_day.reset_index(inplace=True)
    df_cpu_1_day_memcap = df_cpu_1_day['memcap']['mean']
    df_cpu_1_day_memfree = df_cpu_1_day['memfree']['mean']
    diff_daycpu1_memcap_memfree = df_cpu_1_day_memcap - df_cpu_1_day_memfree
    df_cpu_1_day['difference_memecap_memfree_(MB)'] = diff_daycpu1_memcap_memfree
    
    #Merge cpu_0 and cpu_1 for hour data
    result_hour = df_cpu_0_hour.append(df_cpu_1_hour)
    result_hour['id_name']= result_hour['id']['mean']
    result_hour['cpu_name'] = result_hour['unknown']['mean']
    result_hour = result_hour.drop( ['id','unknown'], axis=1 )
    result_hour['time'] = result_hour['time'].dt.hour
     
    #Merge cpu 0 and cpu 1 for day data
    result_day = df_cpu_0_day.append(df_cpu_1_day)
    result_day['id_name']= result_day['id']['mean']
    result_day['cpu_name'] = result_day['unknown']['mean']

    result_day = result_day.drop( ['id','unknown'], axis=1 )
    result_day['time'] = mail_date
    
    #check_dir_exists("\\outputfiles\\cpu_per_hour\\{}".format(mail_date)) 
    file_dir_hour="./outputfiles/cpu_per_hour/{}".format(mail_date)
    file_dir_day="./outputfiles/cpu_per_day/"
    
    if (os.path.isdir(file_dir_hour) is False):
        os.makedirs("./outputfiles/cpu_per_hour/{}".format(mail_date))

    filename_hour= file_dir_hour +"/"+ filename_hour
    filename_day = file_dir_day + "/" + filename_day
    result_hour.to_csv( filename_hour)

    if os.path.exists(filename_day):
        with open(filename_day, 'a') as f:
            result_day.to_csv(f, header=False )
    else:
        result_day.to_csv(filename_day)
    os.remove("./supportfiles/cpu_temp.xlsx")
    


def create_disk_output( file_day,mail_date, output_list ):
    columns = ['id','time','volume','capacity','free']
    df = pd.DataFrame(output_list, columns=columns)
    df.to_excel("./supportfiles/disk_temp.xlsx")
    try:
        df = pd.read_excel("./supportfiles/disk_temp.xlsx" )
    except:
        print("disk temp file not exists")
    
    df['time'] = pd.to_datetime(df['time'])
    df.index = df['time']
    del df['time']

    try:
        df = df[['id','capacity','free'] ].apply(pd.to_numeric, errors='coerce')
        df.fillna(0, inplace=True)
    except:
        print("ERROR: Data Missing in the Disk e-mail. Please validate")

    df['total_used_memory_MB'] = df['capacity'] * ( ( 100 - df['free'] ) / 100)

    df = df.resample('H').agg(['mean', 'max'])
    df['id_num'] = df['id']['mean']

    df = df.drop(['id'], axis=1 )
    df.reset_index(inplace=True)
    df['time']=df['time'].dt.hour
    df['date'] = mail_date
    
    file="./outputfiles/disk_per_day/{}".format(file_day)
    
    if os.path.exists(file):
        with open(file, 'a') as f:
            df.to_csv(f, header=False )
    else:
        df.to_csv(file)
    os.remove("./supportfiles/disk_temp.xlsx")
    
    

def main():
    
    parser = argparse.ArgumentParser(
            description=__description__,
            epilog="Developed by {} on {}".format(", ".join(__authors__), __date__)
            )
    parser.add_argument("DATE", help="message date 2019-01 ")
    
    args = parser.parse_args()
    get_date = args.DATE
    
    current_date = parse(get_date)
    last_month = current_date - relativedelta(months=1)
    last_month = format(last_month, '%Y-%m')

    #check supporting directory are available
    check_directoty_exists()

    outlook = win32com.client.Dispatch("Outlook.Application").GetNameSpace("MAPI")
    #folder = outlook.Folders("cba_capacity_mgmt@dxc.com")
    #inbox = folder.Folders("Inbox")
    inbox = outlook.GetDefaultFolder(6)
    messages = inbox.Items
    messages.Sort("[ReceivedTime]", True)

    #all definations
    cpu_tan7 = []
    cpu_tan8 = []
    disk_tanp7 = []
    disk_tand8 = []
    disk_tand7 = []
    cpu_tanp8 = []
    cpu_tand7 = []
    disk_tanp8 = []

    today = dt.datetime.today().strftime('%m'+'_'+'%Y')


    for message in messages:
        #print(message.subject)
        if get_date in str(message.ReceivedTime):
            message_date = message.ReceivedTime
            data = message.Body.split("*****")[0]
            data_list = data.split('\n')

            if "TANP7 CPU"  in message.Subject: 
                print(message.Subject)
                date_time=str(message.ReceivedTime)
                date_time = date_time.split()[0]

                for line in data_list:
                    line = line.split()
                    if line:
                        cpu_tan7.append(line)

                if cpu_tan7:
                    file_hour="tanp7_cpu_per_hour_{}.csv".format(date_time)
                    file_day = "tanp7_cpu_per_day_{}.csv".format(today)
                    create_cpu_output(file_hour,file_day,date_time, cpu_tan7, message_date)

            elif "TANP8 CPU" in message.Subject:
                print(message.Subject)
                date_time=str(message.ReceivedTime)
                date_time = date_time.split()[0]

                for line in data_list:
                    line = line.split()
                    if line:
                        cpu_tanp8.append(line)
                if cpu_tanp8:
                    file_hour="tanp8_cpu_per_hour_{}.csv".format(date_time)
                    file_day="tanp8_cpu_per_day_{}.csv".format(today)
                    create_cpu_output( file_hour,file_day,date_time, cpu_tanp8, message_date )

            elif "TAND7 CPU" in message.Subject:
                 print(message.Subject)
                 date_time=str(message.ReceivedTime)
                 date_time = date_time.split()[0]
                 for line in data_list:
                     line = line.split()
                     if line:
                         cpu_tand7.append(line)

                 if cpu_tand7:
                    file_hour="tand7_cpu_per_hour_{}.csv".format(date_time)
                    file_day="tand7_cpu_per_day_{}.csv".format(today)
                    create_cpu_output( file_hour,file_day,date_time,cpu_tand7, message_date )


            elif "TAND8 CPU" in message.Subject:
                print(message.Subject)

                date_time=str(message.ReceivedTime)
                date_time = date_time.split()[0]


                for line in data_list:
                    line = line.split()
                    if line:
                        cpu_tan8.append(line)

                if cpu_tan8:
                    file_hour="tand8_cpu_per_hour_{}.csv".format(date_time)
                    file_day="tand8_cpu_per_day_{}.csv".format(today)
                    create_cpu_output(file_hour,file_day,date_time, cpu_tan8, message_date)

            elif "TANP7 Disc" in message.Subject:
                print(message.Subject)
                date_time=str(message.ReceivedTime)
                date_time = date_time.split()[0]
                for line in data_list:
                    line = line.split()
                    if line:
                        disk_tanp7.append(line)

                if disk_tanp7:
                    #file_hour="tanp7_cpu_per_hour_{}.csv".format(date_time)
                    file_day="tanp7_disk_per_day_{}.csv".format(today)
                    create_disk_output(file_day,date_time,disk_tanp7)

            elif "TAND8 Disc" in message.Subject:
                print(message.Subject)
                date_time=str(message.ReceivedTime)
                date_time = date_time.split()[0]

                for line in data_list:
                    line = line.split()
                    if line:
                        disk_tand8.append(line)
                if disk_tand8:
                    #file_hour="tand8_cpu_per_hour_{}.csv".format(date_time)
                    file_day="tand8_disk_per_day_{}.csv".format(today)
                    create_disk_output(file_day,date_time,disk_tand8 )

            elif "TAND7 Disc" in message.Subject:
                date_time=str(message.ReceivedTime)
                date_time = date_time.split()[0]

                for line in data_list:
                    line = line.split()
                    if line:
                        disk_tand7.append(line)

                if disk_tand7:
                    #file_hour="tand7_cpu_per_hour_{}.csv".format(date_time)
                    file_day="tand7_disk_per_day_{}.csv".format(today)
                    create_disk_output(file_day,date_time, disk_tand7)

            elif "TANP8 Disc" in message.Subject:
                date_time=str(message.ReceivedTime)
                date_time = date_time.split()[0]

                for line in data_list:
                    line = line.split()
                    if line:
                        disk_tanp8.append(line)

                if disk_tanp8:
                    #file_hour="tanp8_cpu_per_hour_{}.csv".format(date_time)
                    file_day="tanp8_disk_per_day_{}.csv".format(today)
                    create_disk_output(file_day,date_time,disk_tanp8 )



        if last_month in str(message.ReceivedTime):
            #print("stop searching")
            #print(last_month)
            break
    
if __name__ == '__main__':
    sys.exit( main() )
    