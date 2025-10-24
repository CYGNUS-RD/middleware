#!/usr/bin/env python3
#
import boto3
from boto3sts import credentials as creds

aws_session = creds.assumed_session("infncloud-wlcg")
s3 = aws_session.client('s3', endpoint_url="https://minio.cloud.infn.it/", config=boto3.session.Config(signature_version='s3v4'),verify=True)
print(s3.list_objects(Bucket='cygno-data')['Contents'])

