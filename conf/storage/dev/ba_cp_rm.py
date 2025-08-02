#!/bin/python3
def main(filename, bucket, tag, rm, verbose):
    #
    import os
    import sys
    import numpy as np
    import cygno as cy
    import boto3
    from boto3.s3.transfer import TransferConfig

    aws_session = boto3.session.Session(
        aws_access_key_id=os.environ.get('BA_ACCESS_KEY_ID'),
        aws_secret_access_key=os.environ.get('BA_SECRET_ACCESS_KEY')
    )

    s3r = aws_session.resource('s3', endpoint_url="https://swift.recas.ba.infn.it/",
                              config=boto3.session.Config(signature_version='s3v4'),verify=True)

    s3 = aws_session.client('s3', endpoint_url="https://swift.recas.ba.infn.it/",
                            config=boto3.session.Config(signature_version='s3v4'),verify=True)

    GB = 1024 ** 3
    config = TransferConfig(multipart_threshold=5*GB)

    fout = filename.split('/')[-1]
    if tag:
        if tag[-1]!='/':
            tag=tag+'/'
        key=tag+fout
    else:
        key=fout

    if verbose:
        for bucket_r in s3r.buckets.all():
            print("-->",bucket_r.name)
    if rm:
        response=s3.head_object(Bucket=bucket,Key=key)
        print("removing file: ", filename, bucket, key, "size:", response['ContentLength'])
        s3.delete_object(Bucket=bucket,Key=key)
    else:
        print("coping file: ", filename, bucket, key)
        s3.upload_file(filename, Bucket=bucket, Key=key, Config=config)

if __name__ == "__main__":
    from optparse import OptionParser
    #
    # deault parser value
    #
    BUCKET      = 'cygno-data'
    TAG         = ''


    parser = OptionParser(usage='usage: %prog [-b [{:s}] -s[{:s}] -csv]\n'.format(BUCKET,TAG))
    parser.add_option('-b','--bucket', dest='bucket', type='string', default=BUCKET, help='remote data bucket')
    parser.add_option('-t','--tag', dest='tag', type='string', default=TAG, help='TAG/remote directory')
    parser.add_option('-r','--remove', dest='rm', action="store_true", default=False, help='remove file')
    parser.add_option('-v','--verbose', dest='verbose', action="store_true", default=False, help='verbose output')
    (options, args) = parser.parse_args()
    if options.verbose: 
        print ("options", options)
        print ("args", args)
    if len(args)>0:
        main(args[0], options.bucket, options.tag, options.rm, options.verbose)
    else:
        print('missing filename')
