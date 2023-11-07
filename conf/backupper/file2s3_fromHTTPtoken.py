#!/usr/bin/env python3
#
# G. Mazzitelli 2023
#

def get_s3_client(client_id, client_secret, endpoint_url, session_token):
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

def main(file2backup, client_id, client_secret, endpoint_url, bucket, tag, tfile, verbose=False):
    import os
    import sys
    # client_id     = os.environ['IAM_CLIENT_ID']
    # client_secret = os.environ['IAM_CLIENT_SECRET']
    # endpoint_url  = os.environ['ENDPOINT_URL']
    # file2backup   = os.environ['FILE2BACKUP']
    # bucket        = os.environ['BUCKET']
    # tag           = os.environ['TAG']
    
    with open(tfile) as file:
        token = file.readline().strip('\n')
    session_token= token
    if (verbose): print("TOKEN > ",tfile, token)
    s3 = get_s3_client(client_id, client_secret, endpoint_url, session_token)
    filename = file2backup.split('/')[-1]
    try:
        s3.upload_file(file2backup, Bucket=bucket, Key=tag+'/'+filename)
    except Exception as e:
        print('ERROR file: {:s} --> '.format(file2backup), e)
        sys.exit(-1)
    
    sys.exit(0)
    
if __name__ == "__main__":
    from optparse import OptionParser
    #
    # deault parser value
    #
    TAG         = 'BCK'
    BUCKET      = 'cygno-data'
    ENDPOINT_URL= 'https://minio.cloud.infn.it/'
    TFILE       = '/tmp/token'


    parser = OptionParser(usage='usage: %prog client_id client_secret ]\n')
    parser.add_option('-b','--bucket', dest='bucket', type='string', default=BUCKET, help='data bucket')
    parser.add_option('-t','--tag', dest='tag', type='string', default=TAG, help='data tag')
    parser.add_option('-e','--endpint', dest='endpoint_url', type='string', default=ENDPOINT_URL, help='endpoint')
    parser.add_option('-f','--file', dest='tfile', type='string', default=TFILE, help='token file')
    parser.add_option('-v','--verbose', dest='verbose', action="store_true", default=False, help='verbose output')
    (options, args) = parser.parse_args()
    if options.verbose: 
        print ("options", options)
        print ("args", args)
    if len(args) < 3:
        print(args, len(args))
        parser.error("incorrect number of arguments")
    main(file2backup=args[0], client_id=args[1], client_secret=args[2], endpoint_url=options.endpoint_url, 
         bucket=options.bucket, tag=options.tag, tfile=options.tfile, verbose=options.verbose)