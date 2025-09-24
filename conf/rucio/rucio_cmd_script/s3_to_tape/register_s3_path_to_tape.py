#!/usr/bin/env python3
import os
import boto3
import argparse
import subprocess
from rucio.client.client import Client
from rucio.common.exception import DataIdentifierAlreadyExists, DuplicateRule, FileAlreadyExists

def my_creds(url, verbose):
    with open("/tmp/token", "r") as f:
        IAM_TOKEN = f.read().strip()
    sts_client = boto3.client('sts', endpoint_url=url, region_name='oidc')
    response = sts_client.assume_role_with_web_identity(
        RoleArn="arn:aws:iam::cygno:role/IAMaccess",
        RoleSessionName='Bob',
        DurationSeconds=3600,
        WebIdentityToken=IAM_TOKEN)
    if verbose:
        print(f"AccessKeyId={response['Credentials']['AccessKeyId']}")
    return response

def my_client(credentials, url, verbose):
    return boto3.client('s3',
        aws_access_key_id=credentials['Credentials']['AccessKeyId'],
        aws_secret_access_key=credentials['Credentials']['SecretAccessKey'],
        aws_session_token=credentials['Credentials']['SessionToken'],
        endpoint_url=url,
        region_name='oidc')

def list_s3_files(s3, bucket, prefix):
    paginator = s3.get_paginator('list_objects_v2')
    page_iterator = paginator.paginate(Bucket=bucket, Prefix=prefix)
    files = []
    for page in page_iterator:
        for obj in page.get('Contents', []):
            files.append(obj['Key'])
    return files

def download_file(s3, bucket, key, local_path):
    s3.download_file(bucket, key, local_path)

def upload_to_tape(local_file, tape_url):
    try:
        subprocess.check_call(["gfal-copy", local_file, tape_url])
        print(f"[OK] Copied {local_file} to {tape_url}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] gfal-copy failed for {local_file}: {e}")
        return False

def register_on_rucio(scope, name, tape_rse, local_file):
    client = Client()
    try:
        filesize = os.path.getsize(local_file)
        client.add_replicas(scope=scope,
                            rse=tape_rse,
                            files=[{'scope': scope, 'name': name, 'bytes': filesize}],
                            ignore_availability=True)
        print(f"[OK] Replica registered for {name} on {tape_rse}")
    except FileAlreadyExists:
        print(f"[INFO] Replica already exists for {name}")
    except Exception as e:
        print(f"[ERROR] Registration failed for {name}: {e}")
        return False

    try:
        client.add_replication_rule([{'scope': scope, 'name': name}], 1, tape_rse)
        print(f"[OK] Replication rule added for {name}")
    except DuplicateRule:
        print(f"[INFO] Replication rule already exists for {name}")
    except Exception as e:
        print(f"[ERROR] Rule addition failed for {name}: {e}")
        return False
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--bucket', required=True)
    parser.add_argument('--prefix', default='')
    parser.add_argument('--scope', required=True)
    parser.add_argument('--tape_rse', default='T1_USERTAPE')
    parser.add_argument('--temp_dir', default='/tmp')
    parser.add_argument('--verbose', action='store_true')
    args = parser.parse_args()

    S3_ENDPOINT = "https://swift.recas.ba.infn.it/"
    print("S3 endpoint:", S3_ENDPOINT)

    if S3_ENDPOINT == "https://swift.recas.ba.infn.it/":
        credentials = boto3.session.Session(
            aws_access_key_id=os.environ.get('BA_ACCESS_KEY_ID'),
            aws_secret_access_key=os.environ.get('BA_SECRET_ACCESS_KEY')
        )
        s3 = credentials.client('s3', endpoint_url=S3_ENDPOINT,
                                config=boto3.session.Config(signature_version='s3v4'), verify=True)
    else:
        creds = my_creds(S3_ENDPOINT, args.verbose)
        s3 = my_client(creds, S3_ENDPOINT, args.verbose)

    os.environ['RUCIO_CONFIG'] = '/app/.rucio.cfg'  # Path corretto nel container Docker

    files = list_s3_files(s3, args.bucket, args.prefix)
    print(f"Found {len(files)} files in S3 bucket '{args.bucket}' with prefix '{args.prefix}'")

    for key in files:
        local_file = os.path.join(args.temp_dir, os.path.basename(key))
        did_name = key
        tape_url = f"davs://xfer-archive.cr.cnaf.infn.it:8443/cygno/{did_name}"

        print(f"\nProcessing {key}")
        download_file(s3, args.bucket, key, local_file)
        if upload_to_tape(local_file, tape_url):
            register_on_rucio(args.scope, did_name, args.tape_rse, local_file)
        os.remove(local_file)
