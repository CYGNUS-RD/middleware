#!/usr/bin/python3
import boto3
import zlib

from rucio.client.client import Client
from rucio.client.didclient import DIDClient
import os

rucio_client = Client()
did_client = DIDClient ()

rucio_client.whoami()

SCOPE='cygno-data'
DIR='LNF'

ACCOUNT='mazzitel'
DISK_RSE='BACKBONE_USERDISK'
TAPE_RSE='T1_USERTAPE'

dataset_name='LNF'
dataset_did = [{'scope':SCOPE,'name':dataset_name}]
try:
	did_client.add_dataset(SCOPE, dataset_name)
except Exception as e:
	print(e)

# This function instead of the rucio built-in rucio.common.utils.adler32, since the last one works on file, while data are stored in RAM.
def get_size_and_adler (data):
	size_in_bytes=data['ContentLength']

	contents = data['Body'].read()
	adler=zlib.adler32(contents, 1)
	# backflip on 32bit
	if adler < 0:
		adler = adler + 2 ** 32
	
	return size_in_bytes, str('%08x' % adler)

# Connect to S3 storage
# Prerequisite: having IAM token as env var, see https://confluence.infn.it/display/INFNCLOUD/How+to+test+Grid+storage+access+with+gfal+using+token
 
# Create STS client.
# Security Token Service (STS) enables you to request temporary, limited-privilege credentials for users.
sts_client = boto3.client('sts',
        endpoint_url="https://minio.cloud.infn.it:443",
        region_name=''
        )

# Get credentials from token via the STS
response = sts_client.assume_role_with_web_identity(
        RoleArn="arn:aws:iam:::role/IAMaccess",
        RoleSessionName='Bob',
        DurationSeconds=3600,
        WebIdentityToken = os.getenv('TOKEN')
            )
 
# Create S3 low-level client with the credentials
s3_client = boto3.client('s3',
        aws_access_key_id = response['Credentials']['AccessKeyId'],
        aws_secret_access_key = response['Credentials']['SecretAccessKey'],
        aws_session_token = response['Credentials']['SessionToken'],
        endpoint_url="https://minio.cloud.infn.it:443",
        region_name=''
)

# Get the paginator for list_objects_v2
s3_paginator = s3_client.get_paginator('list_objects_v2')

# Set the S3 Bucket to the paginator
s3_page_iterator = s3_paginator.paginate(
    Bucket=SCOPE,
    Prefix=DIR
)
s3_paginator = s3_client.get_paginator('list_objects_v2')

# Get files from the bucket subdirectory
for s3_page_response in s3_page_iterator:
	for s3_object in s3_page_response['Contents']:        

		name=s3_object['Key']

		did = [{'scope':SCOPE,'name':name}]
		print(did)

		data = s3_client.get_object(Bucket=SCOPE, Key=name)
		size_in_bytes, adler32 = get_size_and_adler (data)
		
		try:
			rucio_client.add_replica(DISK_RSE, SCOPE, name, size_in_bytes, adler32)
		except Exception as e:
			print(e)

		try:
			did_client.attach_dids (SCOPE, dataset_name, did)
		except Exception as e:
			print(e)
			continue
		
try: 
	rucio_client.close(SCOPE, dataset_name)
	rucio_client.add_replication_rule(dataset_did, 1, DISK_RSE, account=ACCOUNT)
	rucio_client.add_replication_rule(dataset_did, 1, TAPE_RSE, account=ACCOUNT, ask_approval=True)
except Exception as e:
	print(e)
