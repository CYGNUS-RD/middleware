#!/usr/bin/env python3
#
# G. Mazzitelli 2023


def s3_session(tfile='/tmp/token', verbose=False):
    import os
    import sys
    client_id     = os.environ['IAM_CLIENT_ID']
    client_secret = os.environ['IAM_CLIENT_SECRET']
    endpoint_url  = os.environ['ENDPOINT_URL']
    
    with open(tfile) as file:
        token = file.readline().strip('\n')
    session_token = token
    if (verbose): print("TOKEN > ",tfile, token)
    s3 = get_s3_sts(client_id, client_secret, endpoint_url, session_token)

    return s3

def get_s3_sts(client_id, client_secret, endpoint_url, session_token):
    # Specify the session token, access key, and secret key received from the STS
    import boto3
    sts_client = boto3.client('sts',
            endpoint_url = endpoint_url,
            region_name  = ''
            )

    response_sts = sts_client.assume_role_with_web_identity(
            RoleArn          = "arn:aws:iam:::role/S3AccessIAM200",
            RoleSessionName  = 'cygno',
            DurationSeconds  = 3600,
            WebIdentityToken = session_token # qua ci va il token IAM
            )

    s3 = boto3.client('s3',
            aws_access_key_id     = response_sts['Credentials']['AccessKeyId'],
            aws_secret_access_key = response_sts['Credentials']['SecretAccessKey'],
            aws_session_token     = response_sts['Credentials']['SessionToken'],
            endpoint_url          = endpoint_url,
            region_name           = '')
    return s3

def main():
    import boto3
    from boto3sts import credentials as creds
    from optparse import OptionParser
    import sys

    version  ='s3v4'
    endpoint ='https://minio.cloud.infn.it/'

    BUCKET   = 'cygno-data'
    TAG      = 'EVENTS' 

    parser = OptionParser(usage='usage: %prog ')
    parser.add_option('-t','--tag', dest='tag', type='string', default=TAG, help='Deafult TAG {:s}'.format(TAG))
    parser.add_option('-b','--bucket', dest='bucket', type='string', default=BUCKET, help='bucket {:s}'.format(BUCKET))
    parser.add_option('-v','--verbose', dest='verbose', action="store_true", default=False, help='verbose output')
    (options, args) = parser.parse_args()
    tag     = options.tag
    bucket  = options.bucket
    verbose = options.verbose
    if tag=="LNGS" or tag=="LNF":
        print("you are removing a dangerous tag "+tag)
        sys.exit(1)

    # Make sure you provide / in the end
    key = tag+'/'

    s3 = s3_session()
    
    response = s3.list_objects(Bucket=bucket, Prefix=key, Delimiter='/')
    contents = response['Contents']
    if verbose: print(contents)
    for i, file in enumerate(contents):
        try:
            if verbose: print("{0:20s} {1:s}".format(str(file['LastModified']).split(".")[0].split("+")[0], file['Key']))
            response = s3.delete_object(Bucket=bucket,Key=file['Key'])
            print ('removed key: {:s}'.format(file['Key']))
        except: 
            print("Error removing key: {:s}".format(file['Key']))
    print("ALL DONE")
    sys.exit(0)

if __name__ == "__main__":
    main()
