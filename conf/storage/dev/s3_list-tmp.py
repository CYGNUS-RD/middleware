#!/usr/bin/env python3
import boto3
from botocore.client import Config
from boto3.s3.transfer import TransferConfig
import os

from optparse import OptionParser

urls = ["https://swift.recas.ba.infn.it/", "https://minio.cloud.infn.it/", "https://s3.cr.cnaf.infn.it:7480/" ]

parser = OptionParser(usage='usage: %prog\t endpont ')
parser.add_option('-v','--verbose', dest='verbose', action="store_true", default=False, help='verbose output;');
(options, args) = parser.parse_args()
verbose = options.verbose

print("ENDPOINTS")
for i, url in enumerate(urls):
    print("{:d}] {:s}".format(i, url))
S3_ENDPOINT = urls[int(input("ENDPOINT: 0..2? "))]

print("listening: ", S3_ENDPOINT)

def my_creds(url, verbose):

    with open("/tmp/token","r") as f:
        IAM_TOKEN = f.read().strip()
    
    sts_client = boto3.client('sts',
                              endpoint_url=url,
                              region_name='oidc')
    
    
    
    response = sts_client.assume_role_with_web_identity(
            RoleArn="arn:aws:iam::cygno:role/IAMaccess",
            RoleSessionName='Bob',
            DurationSeconds=3600,
            WebIdentityToken=IAM_TOKEN)
    

    if verbose: 
        print(f"{response['Credentials']['AccessKeyId']=}\n{response['Credentials']['SecretAccessKey']=}\n{response['Credentials']['SessionToken']=}")
    return response

def my_client(credentials, url, verbose):
#    config = Config(signature_version='s3v4', s3={'addressing_style': 'path'})
#    config = Config(signature_version='s3v4')
    client = boto3.client('s3',
                            aws_access_key_id = credentials['Credentials']['AccessKeyId'],
                            aws_secret_access_key = credentials['Credentials']['SecretAccessKey'],
                            aws_session_token = credentials['Credentials']['SessionToken'],
                            endpoint_url=url,
                            region_name='oidc')
    return client

if S3_ENDPOINT=="https://swift.recas.ba.infn.it/":
    credentials = boto3.session.Session(
        aws_access_key_id=os.environ.get('BA_ACCESS_KEY_ID'),
        aws_secret_access_key=os.environ.get('BA_SECRET_ACCESS_KEY')
    )
    s3 = credentials.client('s3', endpoint_url=urls[0],
                            config=boto3.session.Config(signature_version='s3v4'),verify=True)
else:
    credentials = my_creds(S3_ENDPOINT, verbose)
    s3 = my_client(credentials, S3_ENDPOINT, verbose)


obs = s3.list_objects_v2(Bucket='cygno-analysis')['Contents']

for i, file in enumerate(obs):
    print('{:s} {:} {:.3f} GB'.format(file['Key'], file['LastModified'], file['Size']/(1024)**3))
