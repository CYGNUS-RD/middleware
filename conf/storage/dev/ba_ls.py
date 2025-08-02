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

    IsTruncated = True
    NextMarker  = ''

    try:
        while IsTruncated:
            response = s3.list_objects(Bucket=bucket.name, Marker=NextMarker)
            IsTruncated = response['IsTruncated']
            contents = response['Contents']
            for i, file in enumerate(contents):
               print('{:s} {:} {:.3f} GB'.format(file['Key'], file['LastModified'], file['Size']/(1024)**3))
            if IsTruncated:
                Marker      = response['Marker']
                NextMarker  = response['NextMarker']
    except Exception as e:
        print('empty bucket or error:', e)
# for volume in s3r.volumes.all():
#    print(volume.size, volume.state)
