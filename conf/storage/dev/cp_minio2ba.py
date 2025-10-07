#!/usr/bin/env python3
#
# G. Mazzitelli 2022
# versione DAQ LNGS/LNF per midas file2cloud 
# cheker and sql update Nov 22 
#

def kb2valueformat(val):
    import numpy as np
    if int(val/1024./1024/1024.)>0:
        return val/1024./1024./1024., "Gb"
    if int(val/1024./1024.)>0:
        return val/1024./1024., "Mb"
    if int(val/1024.)>0:
        return val/1024., "Kb"
    return val, "byte"

def download2file(url, fout, verbose):
    import requests
    r = requests.get(url)
    size = 0
    if verbose:
        print(url, fout)
    with open(fout, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024*1024*10): 
            size = size + len(chunk)
            if verbose:
                print(size)
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)
    return 


def main(filename, bucket_in, tag_in, bucket_out, tag_out, rm, verbose):

    import os
    import sys
    import numpy as np
    import cygno as cy
    import boto3
    from boto3.s3.transfer import TransferConfig

    BASE_URL = 'https://s3.cloud.infn.it/v1/AUTH_2ebf769785574195bde2ff418deac08a/'
    tmpout = '/tmp/tag_'+filename
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
    key=tag_out+"/"+filename

    if rm:
        try:
            response=s3.head_object(Bucket=bucket_out,Key=key)
            print("removing file: ", filename, bucket_out, key, "size:", response['ContentLength'])
            s3.delete_object(Bucket=bucket_out,Key=key)
        except Exception as e:
            print("ERROR: upload faliure: ", e)
            sys.exit(1)
    else:
        try:
            print("downloading file:", filename, bucket_in, tag_in)
            download2file(BASE_URL+bucket_in+"/"+tag_in+"/"+filename,tmpout, verbose)
            try:
                print("coping file:", filename, bucket_out, key)
                s3.upload_file(tmpout, Bucket=bucket_out, Key=key, Config=config)
                print("upload ok:", filename)
                cy.cmd.rm_file(tmpout)
            except Exception as e:
                print("ERROR: upload faliure: ", e)
                cy.cmd.rm_file(tmpout)
                sys.exit(1)

        except Exception as e:
            print("ERROR: Download faliure: ", e)
            sys.exit(1)
    sys.exit(0)

if __name__ == "__main__":
    from optparse import OptionParser
    #
    # deault parser value
    #
    BUCKET_IN   = 'cygno-data'
    BUCKET_OUT  = BUCKET_IN
    TAG_IN      = 'LNGS'
    TAG_OUT      = TAG_IN


    parser = OptionParser(usage='usage: %prog [-bin[{:s}] -tin[{:s}] -bout[{:s}] -tout[{:s}]]]\n'.format(BUCKET_IN, BUCKET_OUT, TAG_IN,TAG_OUT))
    parser.add_option('-b','--bucket_in', dest='bucket_in', type='string', default=BUCKET_IN, help='remote data bucket')
    parser.add_option('-t','--tag_in', dest='tag_in', type='string', default=TAG_IN, help='TAG/remote directory')
    parser.add_option('-o','--bucket_out', dest='bucket_out', type='string', default=BUCKET_OUT, help='remote data bucket')
    parser.add_option('-p','--tag_out', dest='tag_out', type='string', default=TAG_OUT, help='TAG/remote directory')
    parser.add_option('-r','--remove', dest='rm', action="store_true", default=False, help='remove file')
    parser.add_option('-v','--verbose', dest='verbose', action="store_true", default=False, help='verbose output')
    (options, args) = parser.parse_args()
    if options.verbose: 
        print ("options", options)
        print ("args", args)
    if len(args)>0:
        main(args[0], options.bucket_in, options.tag_in, options.bucket_out, options.tag_out, options.rm, options.verbose)
    else:
        print('missing filename')


