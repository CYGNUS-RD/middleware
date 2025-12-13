#!/usr/bin/env python3
#
# G. Mazzitelli 2025
#
# versione riveduta e coretta per cnaf storage
#
def my_creds(url, tokenfile, verbose):
    import boto3
    with open(tokenfile,"r") as f:
        IAM_TOKEN = f.read().strip()
    if (verbose): print("TOKEN > ",tokenfile, IAM_TOKEN)
    sts_client = boto3.client('sts',
                              endpoint_url=url,
                              region_name='oidc')

    response = sts_client.assume_role_with_web_identity(
            RoleArn="arn:aws:iam::cygno:role/IAMaccess",
            RoleSessionName='Bob',
            DurationSeconds=3600,
            WebIdentityToken=IAM_TOKEN)


    if verbose: 
        print(f"{response['Credentials']['AccessKeyId']=}\n{response['Credentials']['SecretAccessKey']=}")
    return response

def my_client(credentials, url, verbose):
    import boto3
    client = boto3.client('s3',
                            aws_access_key_id = credentials['Credentials']['AccessKeyId'],
                            aws_secret_access_key = credentials['Credentials']['SecretAccessKey'],
                            aws_session_token = credentials['Credentials']['SessionToken'],
                            endpoint_url=url,
                            region_name='oidc')
    return client


def main(file2backup, endpoint_url, bucket, tag, tokenfile, verbose=False):
    import os
    import sys
    from botocore.client import Config
    from boto3.s3.transfer import TransferConfig

    credentials = my_creds(endpoint_url, tokenfile, verbose)
    s3 = my_client(credentials, endpoint_url, verbose)

    GB = 1024 ** 3
    config = TransferConfig(multipart_threshold=5*GB)

    filename = file2backup.split('/')[-1]

    try:
        s3.upload_file(file2backup, Bucket=bucket, Key=tag+'/'+filename, Config=config)
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
    ENDPOINT_URL= 'https://s3.cr.cnaf.infn.it:7480/'
    TOKENFILE       = '/tmp/token'


    parser = OptionParser(usage='usage: %prog client_id client_secret ]\n')
    parser.add_option('-b','--bucket', dest='bucket', type='string', default=BUCKET, help='data bucket')
    parser.add_option('-t','--tag', dest='tag', type='string', default=TAG, help='data tag')
    parser.add_option('-e','--endpint', dest='endpoint_url', type='string', default=ENDPOINT_URL, help='endpoint')
    parser.add_option('-f','--file', dest='tokenfile', type='string', default=TOKENFILE, help='token file')
    parser.add_option('-v','--verbose', dest='verbose', action="store_true", default=False, help='verbose output')
    (options, args) = parser.parse_args()
    if options.verbose: 
        print ("options", options)
        print ("args", args)
    if len(args) < 1:
        print(args, len(args))
        parser.error("incorrect number of arguments")
    main(file2backup=args[0], endpoint_url=options.endpoint_url, 
         bucket=options.bucket, tag=options.tag, tokenfile=options.tokenfile, verbose=options.verbose)
