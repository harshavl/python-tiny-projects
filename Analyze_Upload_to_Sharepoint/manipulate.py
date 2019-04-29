from __future__ import print_function
import sys,os
import pandas as pd
import numpy as np
from tqdm import tqdm
import argparse,time
from datetime import date
import smtplib
from email.mime.text import MIMEText

from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

import multiprocessing as mp
 
import matplotlib.pyplot as plt
import seaborn as sns




__authors__ = 
__date__ = '1172018'
__description__ = '''
    input: weekly report excel file
    Output: output.csv
    
    Description: Weekly report statistics;
    
    Prerequisite: 
        - Anaconda installed in the local machine.

'''


def send_email(TO,FROM, attachments, subject, body_text, CC=[] ):
    HOST = "smtp.svcs.entsvcs.com"
    
    msg = MIMEMultipart()
    msg["From"] = ",".join( FROM )
    msg["To"] = ", ".join(TO)
    msg["Cc"] = ",".join(CC)
    msg["Subject"] = subject
   # msg['Date']    = formatdate(localtime=True)
    if body_text:
        msg.attach( MIMEText(body_text) )
 
    # attach a file
    for filename in attachments:
        
        part = MIMEBase('application', "octet-stream")
        part.set_payload( open(filename,"rb").read() )
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(filename))
        msg.attach(part)
 
    server = smtplib.SMTP(HOST)
    # server.login(username, password)  # optional
 
    try:
        failed = server.sendmail(FROM, TO, msg.as_string())
        server.close()
    except:
        print("Unable to send email. Error at:%r"%(subject))
        
        
def parallel(branch):
    branch_count = branch['Creation_Date'].count()
        
        #this should be list;
    to_list = branch['Mail ID'].unique()
 
    #to_list = [ 'harshavardhana.l@hpe.com' ]
    
    
    if branch_count:
        header.append(domain)
        
    if not branch_count:
        print("No data related to %r"%(domain) )
        continue
    
    if not len(to_list):
        print("Please check the input file. Empty mail-id at: %r"%(branch))
        continue
    
    #sla_count = branch [ branch['SLA Server'] == 'Y' ]
    try:
        sla_count = branch[ branch['SLA Server'].str.contains('Y', na=False) ] 
    except:
        print("Please check input file at 'SLA Server' column ")
        
    no_sla = sla_count['Creation_Date'].count() 
   
    # tickets > 70 ageing
    branch_gt_70 = branch[ branch['Ticket_Age'] >= 70 ]
    tickets_gt_70 = branch_gt_70['Creation_Date'].count() 
    
    if tickets_gt_70 >= 70:
        subject_70 = "Number of Vulnerabilities greater than 70 days %r: %r"%(domain,tickets_gt_70)
        send_email( to_list, from_addr , [file], subject_70, body_text, cc_list  )
        time.sleep(1)
        
        
    
    branch_lt_70 = branch[ branch['Ticket_Age'] <= 70 ]
    tickets_lt_70 = branch_lt_70['Creation_Date'].count() 
    
    branch_gt_200 = branch[ branch['Ticket_Age'] >= 200 ]
    tickets_gt_200 = branch_gt_200['Creation_Date'].count() 
    
    if tickets_gt_200 >= 200:
        subject_200 = "Number of Vulnerabilities greater than 70 days %r: %r"%(domain,tickets_gt_200)
        send_email( to_list, from_addr ,[file], subject_200, body_text, cc_list  )
        time.sleep(1)
        

    branch_gt_500 = branch[ branch['Ticket_Age'] >= 500 ]
    tickets_gt_500 = branch_gt_500['Creation_Date'].count() 
    
    #Exemption count
    exemption_count = branch[ branch['Comments'].str.contains('Exemption', na=False) ]
    branch_exemption_count = int( exemption_count['Creation_Date'].count() )
    subject_exemption_count = "Number of exemption count %r:%r"%(domain,branch_exemption_count)
    
    if branch_exemption_count:
        send_email( to_list, from_addr , [file], subject_exemption_count, body_text, cc_list )
        time.sleep(1)
    else:
        #send mail only to manager's
        send_email( managers_list, from_addr , [file], subject_exemption_count, body_text  )
        time.sleep(1)
            
        
    #Deferrals and sla is YES
    deferrals_sla = sla_count[ sla_count['Comments'].str.contains('Deferrals', na=False) ] 
    deferrals_sla_count = int(deferrals_sla['Creation_Date'].count())
    
    if deferrals_sla_count:
        subject_deferrals = "Count of Deferrals and SLA vulnerabilities %r: %r"%(domain,deferrals_sla_count)
        send_email( to_list, from_addr , [file], subject_deferrals, body_text, cc_list  )
        time.sleep(1)
    else:
        send_email( managers_list, from_addr ,[file], subject_deferrals, body_text  )
        time.sleep(1)
        
   

    #Deferrals total count
    deferrals_count = branch[ branch['Comments'].str.contains('Deferrals', na=False) ]
    branch_deferrals_count = int( deferrals_count['Creation_Date'].count() )
    
    if branch_deferrals_count:
        subject_def = "Count of deferrals %r:%r"%(domain,branch_deferrals_count)
        send_email( to_list, from_addr ,[file], subject_def, body_text, cc_list  )
        time.sleep(1)
    else:
        send_email( managers_list, from_addr ,[file], subject_def, body_text  )
        time.sleep(1)
        
    
    #Remediation planned
    remediation_planned = branch[ branch['Comments'].str.contains('Remediation planned', na=False) ]
    remediation_planned_count = int( remediation_planned['Creation_Date'].count())
    
    
    
    if remediation_planned_count:
        subject_def = "Count of remediation planned %r:%r"%(domain,remediation_planned_count)
        send_email( to_list, from_addr ,[file], subject_def, body_text, cc_list  )
        time.sleep(1)
    else:
        send_email( managers_list, from_addr ,[file], subject_def, body_text  )
        time.sleep(1)
        

     
    #New
    new = branch[ branch['Comments'].str.contains('New', na=False) ]
    new_count = int( new['Creation_Date'].count() )
    
    if new_count:
        subject_def = "Count of New %r:%r"%(domain,new_count )
        send_email( to_list, from_addr ,[file], subject_def, body_text, cc_list  )
        time.sleep(1)
    else:
        send_email( managers_list, from_addr ,[file], subject_def, body_text  )
        time.sleep(1)
        
    #Not Remediated
    not_remediated = branch[ branch['Comments'].str.contains('Not Remediated', na=False) ]
    not_remediated_count = not_remediated['Creation_Date'].count()
    
    if int(not_remediated_count):
        subject_def = "Count of Not Remediated %r:%r"%(domain,new_count )
        send_email( to_list, from_addr ,[file], subject_def, body_text, cc_list  )
        time.sleep(1)
    else:
        send_email( managers_list, from_addr ,[file], subject_def, body_text  )  
        time.sleep(1)
    
    dash_list.append( [ branch_count,no_sla,deferrals_sla_count, branch_exemption_count,  tickets_gt_70,  tickets_lt_70,tickets_gt_200,tickets_gt_500, branch_deferrals_count, remediation_planned_count, new_count, not_remediated_count ])

#print("Before: %r"%(dash_list))
    index = ['Count Last Week Vulnerabilities','Count of SLA impacting Vulnerabilities','Count of SLA Deferral and SLA is YES','Count of Exempted vulnerabilities',  'Count Of >70 Day Vulnerabilities', 'Count Of < 70 Day Vulnerabilities', 'Count of > 200 days Vulnerabilities', 'Count of > 500 days Vulnerabilities', 'Count of Deferred Vulnerabilities', "Count of Remediation Planned", "Count of New",  "Count of Not Remediated"]
    new_list = np.transpose(dash_list)
	
    return new_list

def fun(df,file):
    domains = df['Implementer Group'].unique()
    
    #domains = df['Owner Group'].unique()
    
    header = []
    
    pbar = tqdm(domains)
    dash_list = list ()
    
    #For testing using to_list out from loop;
    #to_list = ['harshavardhana.l@hpe.com'  ]

    for domain in pbar:
        #print("insize %r"%(domain))
        
        pbar.set_description("Processing %s"%domain )
        branch = df[ df['Implementer Group'] == domain ]
        p = multiprocessing.Pool(5)
        p.map(parallel, brach)
        new_list = parallel(brach)
        
        print(new_list)
        sys.exit()
       
	
	


def main():
    
    parser = argparse.ArgumentParser(
            description=__description__,
            epilog="Developed by {} on {}".format(", ".join(__authors__), __date__)
            )
    parser.add_argument("FILE", help="file which has wmic output ")
    
    args = parser.parse_args()
    file = args.FILE
    
    global from_addr = ['harshavardhana.l@dxc.com' ]
    global managers_list = [ 'harshavardhana.l@dxc.com' ]
    global cc_list = [ 'harshavardhana.l@dxc.com' ]
    
    global body_text = "Hi,\rPlease edit the attached weekly report excel."
    
    df = pd.read_excel(file)

    pool = mp.Pool(processes=5)
    
    #results = [pool.apply(fun, args=(df,file,)) ]
    
    new_list = fun(df, file)
    
    print(results)
    sys.exit()

    try:
        db = pd.DataFrame(data= new_list, index=index, columns= header )
        filename = ".\\outputfolder\\" + "output_" + str(date.today() ) +".csv" 
        db.to_csv( filename, sep=',' )
        
        image_file = ".\\outputfolder\\" +  "weeklystastics_" + str(date.today() ) +".png"
        
        subject_weeklystatus="Weekly Vulnerabilities Statistics Report"
        body_weeklyreport = "Hi,\rPlease find the attached weekly vulnerabilities statistics reports."
        
        fig, ax = plt.subplots(figsize=(10,10))
        svm = sns.heatmap(db, annot=True, fmt="g", cmap='YlOrRd', linewidths=0.1, ax = ax  )
        fig = plt.gcf()
        plt.tight_layout()
        fig.savefig( image_file, bbox='tight')
        
        attachments = [ filename, image_file ]
        send_email( managers_list, from_addr, attachments,subject_weeklystatus, body_weeklyreport )
        time.sleep(1)
    
    except:
        print("Please check the input file")
    
    


    

    
    
    


if __name__ == '__main__':
    sys.exit( main() )
    
