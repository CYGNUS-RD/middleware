#!/usr/bin/env python3
#
# G. Mazzitelli 2023

def main():
    import boto3
    from boto3sts import credentials as creds
    from optparse import OptionParser
    import sys

    version  ='s3v4'
    endpoint ='https://minio.cloud.infn.it/'

    SESSION  ='infncloud-iam'
    BUCKET   = 'cygno-data'
    TAG      = 'EVENTS' 

    parser = OptionParser(usage='usage: %prog ')
    parser.add_option('-t','--tag', dest='tag', type='string', default=TAG, help='Deafult TAG {:s}'.format(TAG))
    parser.add_option('-s','--session', dest='session', type='string', default=SESSION, help='session {:s}'.format(SESSION))
    parser.add_option('-b','--bucket', dest='bucket', type='string', default=BUCKET, help='bucket {:s}'.format(BUCKET))
    parser.add_option('-v','--verbose', dest='verbose', action="store_true", default=False, help='verbose output')
    (options, args) = parser.parse_args()
    tag     = options.tag
    session = options.session
    bucket  = options.bucket
    verbose = options.verbose
    if tag=="LNGS" or tag=="LNF":
        print("you are removing a dangerous tag "+tag)
        sys.exit(1)

    # Make sure you provide / in the end
    key = tag+'/'

    session = creds.assumed_session(session, endpoint=endpoint, verify=True)
    s3 = session.client('s3', endpoint_url=endpoint, config=boto3.session.Config(signature_version='s3v4'),
                                                    verify=True)
    
    
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
