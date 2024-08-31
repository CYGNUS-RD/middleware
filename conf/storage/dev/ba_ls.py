#!/bin/python3
import boto3
import pandas as pd
import os

aws_session = boto3.session.Session(
        aws_access_key_id=os.environ.get('BA_ACCESS_KEY_ID'),
        aws_secret_access_key=os.environ.get('BA_SECRET_ACCESS_KEY')
    )

s3r = aws_session.resource('s3', endpoint_url="https://swift.recas.ba.infn.it/",
                              config=boto3.session.Config(signature_version='s3v4'),verify=True)
s3 = aws_session.client('s3', endpoint_url="https://swift.recas.ba.infn.it/",
                            config=boto3.session.Config(signature_version='s3v4'),verify=True)

for bucket in s3r.buckets.all():
    print("-->",bucket.name)
    try:
        response = s3.list_objects(Bucket=bucket.name)['Contents']
        #print(response)
        for i, file in enumerate(response):
            print(file['Key'], file['LastModified'], file['Size'])
    except:
        print('empty bucket or error')
