#!/bin/python3
import re
import sys
import os


def upload_file(file_name, bucket='cygno-data', tag='LAB'):
    # https://boto3.amazonaws.com/v1/documentation/api/latest/guide/s3-uploading-files.html#uploading-files
    import boto3
#    from boto3sts import credentials as creds
    import logging
    #
#    endpoint='https://minio.cloud.infn.it/'
#    version='s3v4'
#    oidctoken = 'infncloud'
    #
 #   aws_session = creds.assumed_session(oidctoken)
 #   s3 = aws_session.client('s3', endpoint_url=endpoint, config=boto3.session.Config(signature_version=version),verify=True)

    sts_client = boto3.client('sts', endpoint_url="https://rgw.cloud.infn.it:443", region_name='')


    response = sts_client.assume_role_with_web_identity(
         RoleArn="arn:aws:iam:::role/IAMaccess",
         RoleSessionName='Bob',
         DurationSeconds=3600,
         WebIdentityToken = os.getenv('TOKEN'))

    s3 = boto3.client('s3',
         aws_access_key_id = response['Credentials']['AccessKeyId'],
         aws_secret_access_key = response['Credentials']['SecretAccessKey'],
         aws_session_token = response['Credentials']['SessionToken'],
         endpoint_url="https://rgw.cloud.infn.it:443")


    key = 'Data/'+tag+'/'

# Upload the file

    try:
        response = s3.upload_file(file_name, bucket, key+file_name)
        print ('Uploaded file: '+key+file_name)
    except ClientError as e:
        logging.error(e)
        return False
    return True

def main(file_name):

    upload_file(file_name, bucket='cygno-data', tag='LAB')

if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw|\.exe)?$', '', sys.argv[0])
    if len(sys.argv)==1:
        print ('Usage: <filename>')
        sys.exit(1)
    else:
        sys.exit(main(sys.argv[1]))
