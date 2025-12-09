#!/usr/bin/env python3
import boto3
from boto3sts import credentials as creds
import os
from optparse import OptionParser

urls = ["https://swift.recas.ba.infn.it/", "https://minio.cloud.infn.it/", "https://s3.cr.cnaf.infn.it:7480/" ]

parser = OptionParser(usage='usage: %prog\t endpont ')
parser.add_option('-s','--session', dest='session', type='string', default='dodas', help='shot name [dodas];');
parser.add_option('-v','--verbose', dest='verbose', action="store_true", default=False, help='verbose output;');
(options, args) = parser.parse_args()

print("ENDPOINTS")
for i, url in enumerate(urls):
    print("{:d}] {:s}".format(i, url))
S3_ENDPOINT = urls[int(input("ENDPOINT: 0..2? "))]

if (options.verbose):
   print("listening: ", S3_ENDPOINT)
   print("session: ", options.session)

if S3_ENDPOINT=="https://swift.recas.ba.infn.it/":
    aws_session = boto3.session.Session(
        aws_access_key_id=os.environ.get('BA_ACCESS_KEY_ID'),
        aws_secret_access_key=os.environ.get('BA_SECRET_ACCESS_KEY')
    )
else:
    aws_session = creds.assumed_session(str(options.session), S3_ENDPOINT)

s3r = aws_session.resource('s3', endpoint_url=S3_ENDPOINT,
                          config=boto3.session.Config(signature_version='s3v4'),
                           verify=True)

s3 = aws_session.client('s3', endpoint_url=S3_ENDPOINT,
                        config=boto3.session.Config(signature_version='s3v4'),
                        verify=True)



for bucket in s3r.buckets.all():
    print("-->",bucket.name)
    try:
        response = s3.list_objects(Bucket=bucket.name)['Contents']
        for i, file in enumerate(response):
            print('{:s} {:} {:.3f} GB'.format(file['Key'], file['LastModified'], file['Size']/(1024)**3))
    except:
        print('empty bucket or error')
