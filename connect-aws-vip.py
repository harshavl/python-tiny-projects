#!/usr/bin/env python3
'''
Connect to aws server via VIP access

'''
import argparse
import sys
import boto3
import requests
import getpass
import configparser
import base64
import logging
import json
import xml.etree.ElementTree as ET
import re
from bs4 import BeautifulSoup
from os.path import expanduser
from os import environ
from urllib.parse import urlparse, urlunparse
from datetime import datetime
from dateutil import tz
from botocore.exceptions import ClientError

sslverification = True
sessionDuration = 14400
sessionDurationIamMgr = 7200

adfsEndpoints = [
    {'region': 'us-east-2 (Ohio)', 'domain': 'hosstname.com'},
    {'region': 'eu-west-1 (Ireland)', 'domain': 'hostname.com'}


parser = argparse.ArgumentParser(
    usage='%(prog)s [options] [ --hostname]',
    description=' CLI Login to CloudIAM managed resources'
)
parser.add_argument('-a','--_endpoint', help='specify the ADFS Endpoint to authenticate to Ex. "hostname.com".' \
                                                 'Note this can also be set using environment variable AUTHENTICATION_URL')
parser.add_argument('-u','--username',
    help='Specify the user to login with. Note, this can also be set by environment variable: ',
    metavar='username@hostname.com',
    dest='username'
)

args = parser.parse_args()


def main():
    #logging.basicConfig(level=logging.DEBUG)
    print('\nDXC Federated SSO Login for AWS CLI\n')

    # Checks for fedsso url in argument and environment variable
    if args.adfs_endpoint is not None:
        print('Using Optional Argument --adfs_endpoint "{}" as ADFS Endpoint.'.format(args.adfs_endpoint))
        idpSsoUrl = getIdpSsoUrl(idpSsoUrl=args.adfs_endpoint)
    elif 'AUTHENTICATION_URL' in environ:
        idpSsoUrl = getIdpSsoUrl(idpSsoUrl=environ['AUTHENTICATION_URL'])
        print('Using Environment Variable AUTHENTICATION_URL="{}" as ADFS Endpoint.'.format(idpSsoUrl))
    else:
        idpSsoUrl = getIdpSsoUrl()

    #password = getpass.getpass()
	username = "username"
	password = "password"
	
    session = requests.Session()

    print('\nProcessing Web Request...\n')

    # Retrieve IDP SSO Form HTML & parse it.
    try:
        loginFormResponse = session.get(idpSsoUrl, verify=sslverification)
    # Catches error if passed adfs_endpoint parameter isn't valid
    except requests.exceptions.ConnectionError:
        print('>>> ERROR: Invalid URL "{}"'.format(idpSsoUrl))
        sys.exit(0)

    parsedLoginForm = BeautifulSoup(loginFormResponse.text, 'html.parser')

    # Generate loginData payload.
    loginData = getLoginData(parsedLoginForm, username, password)

    # Prepare URL for login form submission where loginData will be posted.
    loginFormSubmitUrl = getLoginFormSubmitUrl(parsedLoginForm, idpSsoUrl)

    # POST login data to login form submit URL.
    loginResponse = session.post(loginFormSubmitUrl, data=loginData, verify=sslverification)

    # If loginResponse does not contain "SAMLResponse" then try MFA.
    if not re.search('SAMLResponse', loginResponse.text):
        loginResponse = getMFALoginResponse(loginResponse, session)

    samlAssertion = getSAMLResponse(loginResponse)
    if (samlAssertion is None):
        print('>>> ERROR: Invalid Username, Password or Token.')
        sys.exit(0)

    awsroles = extractAWSRoles(samlAssertion)

    role_arn, principal_arn = getArnSelection(awsroles)
    calcSessionDuration = sessionDuration
    stsclient = boto3.client('sts')

    # 3600 seconds is the minimum allowed assumeRole duration
    # Start at max and try until we hit this min
    while calcSessionDuration >= 3600:
        try:
            stsToken = stsclient.assume_role_with_saml(RoleArn=role_arn, PrincipalArn=principal_arn, SAMLAssertion=samlAssertion, DurationSeconds=calcSessionDuration)
            break
        except ClientError as err:
            if "DurationSeconds exceeds" in err.response['Error']['Message']:
                calcSessionDuration = int(calcSessionDuration / 2)
                print("- Reducing session duration to {}".format(calcSessionDuration))
            else:
                print( err.response['Error']['Message'] )
                sys.exit(0)
        except Exception as err:
            print(err)
            sys.exit(0)

    updateAWSProfiles(stsToken, role_arn)

    print('\nUpdated credentials file, invoke the AWS CLI with the --profile & --region options.\n')
	copy_files_cloud()
	print("--END--")

#Functions
def getIdpSsoUrl(idpSsoUrl=None):
    idpSsoUrlTemplate = 'https://%s/adfs/ls/IdpInitiatedSignOn.aspx?loginToRp=urn:amazon:webservices'
    if idpSsoUrl:
        return idpSsoUrlTemplate % idpSsoUrl
    print('Available ADFS Endpoints: ')
    for idx in range (0 , len(adfsEndpoints)):
        print('\t' + str(idx+1) + ': ' + 'Region: ' + adfsEndpoints[idx]['region'] + ' ADFS Endpoint: ' + adfsEndpoints[idx]['adfs-domain'])
    adfsSelection = int(input("Select an ADFS Endpoint to connect [1]: ") or "1")
    idpSsoUrl = idpSsoUrlTemplate % adfsEndpoints[adfsSelection-1]['adfs-domain']
    return idpSsoUrl


def getLoginData(parsedLoginForm, username, password):
    loginData = {}
    for inputTag in parsedLoginForm.find_all(re.compile('(INPUT|input)')):
        tagName = inputTag.get('name','')
        tagValue = inputTag.get('value','')
        if "user" in tagName.lower():
            #Make an educated guess that this is the right field for the username
            loginData[tagName] = username
        elif "email" in tagName.lower():
            #Some IdPs also label the username field as 'email'
            loginData[tagName] = username
        elif "pass" in tagName.lower():
            #Make an educated guess that this is the right field for the password
            loginData[tagName] = password
        else:
            #Simply populate the parameter with the existing value (picks up hidden fields in the login form)
            loginData[tagName] = tagValue
    return loginData


def getLoginFormSubmitUrl(parsedLoginForm, idpSsoUrl):
    for formTag in parsedLoginForm.find_all(re.compile('(FORM|form)')):
        action = formTag.get('action')
        loginid = formTag.get('id')
        if (action and loginid == "loginForm"):
            parsedurl = urlparse(idpSsoUrl)
            loginFormSubmitUrl = parsedurl.scheme + "://" + parsedurl.netloc + action
    return loginFormSubmitUrl


def getMFALoginResponse(loginResponse, session):
    mfa_url = loginResponse.url

    parsedLoginForm = BeautifulSoup(loginResponse.text, "html.parser")
    loginData = {}

    for inputTag in parsedLoginForm.find_all(re.compile('(INPUT|input)')):
        tagName = inputTag.get('name','')
        tagValue = inputTag.get('value','')
        #Simply populate the parameter with the existing value (picks up hidden fields in the login form)
        loginData[tagName] = tagValue

    #token = str(input('For security reasons, we require additional information to verify your account\nMFA token: '))
	print("Finding the MFC Token ")
    os.startfile("C:\Program Files (x86)\Symantec\VIP Access Client\VIPUIManager.exe")
    time.sleep(1)
    pyautogui.click( 1250, 602)
    token = pyperclip.paste()
    print(f"MFC Token:{token}")
	
    loginData['security_code'] = str(token)
    loginData['AuthMethod'] = 'VIPAuthenticationProviderWindowsAccountName'
    # Picks up unnecessary 'UserName' input field in 2019 ADFS auth form, if sent with post response will result in http 500 error code
    if 'UserName' in loginData:
        del loginData['UserName']

    mfa_loginResponse = session.post(mfa_url, data=loginData, verify=sslverification)
    return mfa_loginResponse


def getSAMLResponse(loginResponse):
    parsedLoginResponse = BeautifulSoup(loginResponse.text, "html.parser")
    samlAssertion = None
    for inputTag in parsedLoginResponse.find_all('input'):
        if(inputTag.get('name') == 'SAMLResponse'):
            samlAssertion = inputTag.get('value')

    return samlAssertion

def extractAWSRoles(samlAssertion):
    awsroles = []
    root = ET.fromstring(base64.b64decode(samlAssertion))
    for saml2attribute in root.iter('{urn:oasis:names:tc:SAML:2.0:assertion}Attribute'):
        if (saml2attribute.get('Name') == 'https://aws.amazon.com/SAML/Attributes/Role'):
            for saml2attributevalue in saml2attribute.iter('{urn:oasis:names:tc:SAML:2.0:assertion}AttributeValue'):
                awsroles.append(saml2attributevalue.text)

    # Note the format of the attribute value should be role_arn,principal_arn but lots of blogs list it as principal_arn,role_arn
    # so let's reverse them if needed
    for awsrole in awsroles:
        chunks = awsrole.split(',')
        if 'saml-provider' in chunks[0]:
            newawsrole = chunks[1] + ',' + chunks[0]
            index = awsroles.index(awsrole)
            awsroles.insert(index, newawsrole)
            awsroles.remove(awsrole)
    awsroles.sort()
    return awsroles

def getArnSelection(awsroles):
    print("")
    if len(awsroles) > 1:
        i = 0
        print("Please choose the role you would like to assume:")
        for awsrole in awsroles:
            print('[', i, ']: ', awsrole.split(',')[0])
            i += 1
        print("Selection: ")
		
		'''
        try:
            selectedroleindex = input()
        except:
            sys.exit(0)
		'''
		print("Selected the role index as 12")
		selectedroleindex = 12

        # Basic sanity check of input
        if int(selectedroleindex) > (len(awsroles) - 1):
            print('You selected an invalid role index, please try again')
            sys.exit(0)

        role_arn = awsroles[int(selectedroleindex)].split(',')[0]
        principal_arn = awsroles[int(selectedroleindex)].split(',')[1]
    else:
        role_arn = awsroles[0].split(',')[0]
        principal_arn = awsroles[0].split(',')[1]

    return role_arn, principal_arn

def updateAWSProfiles(stsToken, role_arn):
    # print(stsToken)
    awsCredFile = '/.aws/credentials'
    # Read in the existing aws credentials file
    awsCreds = configparser.RawConfigParser(comment_prefixes='/', allow_no_value=True)
    awsCreds.read(expanduser("~") + awsCredFile)
    print("\nFound AWS profiles: " + json.dumps(awsCreds.sections()))
    #print("Enter profile name to add/update: ")
    #profileName = input()
	print("Profile name: SSOTest1 ")
	profileName = "SSOTest1"
    if not awsCreds.has_section(profileName):
        awsCreds.add_section(profileName)
    awsCreds.set(profileName, '#Role_ARN', role_arn)
    awsCreds.set(profileName, 'aws_access_key_id', stsToken["Credentials"]["AccessKeyId"])
    awsCreds.set(profileName, 'aws_secret_access_key', stsToken["Credentials"]["SecretAccessKey"])
    awsCreds.set(profileName, 'aws_session_token', stsToken["Credentials"]["SessionToken"])
    awsCreds.set(profileName, 'aws_session_token_expiration', (stsToken["Credentials"]["Expiration"]).astimezone(tz.tzlocal()).strftime('%Y-%m-%d %H:%M:%S (UTC%z)'))
    tz.tzlocal()

    # Write the updated awsCreds file
    with open((expanduser("~") + awsCredFile), 'w+') as configfile:
        awsCreds.write(configfile)

def copy_files_cloud():
    try:
        subprocess.call(r'xcopy /Y "C:\Users\username\aws\credentials" "C:\aws" ')
    except:
        print("ERROR: Failed to copying files to local path")    
    
    try:
        subprocess.call(r'net use v: /del', shell=True)
    except:
        pass

    try:
    # Connect to shared drive, use drive letter V
        subprocess.call(r'net use v: \\zc4w00871.itcs.houston.dxccorp.net\SPData\aws /user:ssz\x-username password', shell=True)
        subprocess.call(r'xcopy /Y "C:\Users\username\aws\credentials" "\\hostname.net\SPData\aws"', shell=True)
        subprocess.call(r'net use v: /del', shell=True)
    except:
        print("ERROR: Failed to copying file to  Cloud path")
		

main()