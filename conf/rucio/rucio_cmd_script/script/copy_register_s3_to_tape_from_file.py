#!/usr/bin/env python3
import os
import boto3
import argparse
import subprocess
import logging
from rucio.client.client import Client
from rucio.common.exception import FileAlreadyExists, DuplicateRule
from botocore.exceptions import ClientError, BotoCoreError

def get_s3_sts_client(endpoint_url, s3_token_file, verbose=False):
    with open(s3_token_file, "r") as f:
        IAM_TOKEN = f.read().strip()

    sts_client = boto3.client('sts', endpoint_url=endpoint_url, region_name='oidc')

    credentials = sts_client.assume_role_with_web_identity(
        RoleArn="arn:aws:iam::cygno:role/IAMaccess",
        RoleSessionName='Bob',
        DurationSeconds=3600,
        WebIdentityToken=IAM_TOKEN)

    if verbose:
        print(f"{credentials['Credentials']['AccessKeyId']=}\n{credentials['Credentials']['SecretAccessKey']=}")

    client = boto3.client('s3',
                          aws_access_key_id=credentials['Credentials']['AccessKeyId'],
                          aws_secret_access_key=credentials['Credentials']['SecretAccessKey'],
                          aws_session_token=credentials['Credentials']['SessionToken'],
                          endpoint_url=endpoint_url,
                          region_name='oidc')
    return client

def get_s3_client(endpoint_url, access_key, secret_key):
    session = boto3.session.Session(
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key
    )
    return session.client('s3', endpoint_url=endpoint_url)

def check_file_on_tape(tape_url):
    env = os.environ.copy()
    try:
        subprocess.check_output(["gfal-ls", tape_url], stderr=subprocess.STDOUT, env=env)
        return True
    except subprocess.CalledProcessError as e:
        output = e.output.decode().strip()
        logging.warning(f"[WARN] gfal-ls failed for {tape_url} – Output: {output}")
        return False

def upload_to_tape(local_file, tape_url):
    try:
        subprocess.check_call(["gfal-copy", local_file, tape_url])
        logging.info(f"[OK] Copied {local_file} to {tape_url}")
        return True
    except subprocess.CalledProcessError as e:
        logging.error(f"[ERROR] gfal-copy failed for {local_file}: {e}")
        return False

def register_in_rucio(scope, did_name, tape_rse, filesize, dry_run=False):
    client = Client()
    try:
        if not dry_run:
            client.add_replicas(rse=tape_rse, files=[{'scope': scope, 'name': did_name, 'bytes': filesize}], ignore_availability=True)
        logging.info(f"[OK] Registered {did_name} in Rucio at {tape_rse}")
    except FileAlreadyExists:
        logging.info(f"[INFO] Replica already registered: {did_name}")
    except Exception as e:
        logging.error(f"[ERROR] Registration failed for {did_name}: {e}")
        return False

    try:
        if not dry_run:
            client.add_replication_rule([{'scope': scope, 'name': did_name}], 1, tape_rse)
        logging.info(f"[OK] Replication rule added for {did_name}")
    except DuplicateRule:
        logging.info(f"[INFO] Rule already exists for {did_name}")
    except Exception as e:
        logging.error(f"[ERROR] Rule addition failed for {did_name}: {e}")
        return False
    return True

def refresh_token(token_file):
    try:
        with open(token_file, 'r') as f:
            token = f.read().strip()
        os.environ["BEARER_TOKEN"] = token
    except Exception as e:
        logging.error(f"[ERROR] Failed to read token file '{token_file}': {e}")
        raise

def process_s3_files(endpoint, bucket, prefix, scope, tape_rse, temp_dir, token_file, dry_run=False, file_list=None):

    s3 = get_s3(endpoint)
    if file_list:
        with open(file_list, 'r') as fh:
            keys = [line.strip() for line in fh if line.strip()]
    else:
        keys = []
        paginator = s3.get_paginator('list_objects_v2')
        pages = paginator.paginate(Bucket=bucket, Prefix=prefix)
        for page in pages:
            for obj in page.get('Contents', []):
                keys.append(obj['Key'])

    for key in keys:
        s3 = get_s3(endpoint)
        try:
            head = s3.head_object(Bucket=bucket, Key=key)
            filesize = head['ContentLength']
        except Exception as e:
            logging.error(f"[ERROR] Cannot access object metadata for {key}: {e}")
            continue

        did_name = key
        tape_url = f"davs://xfer-archive.cr.cnaf.infn.it:8443/cygno/{scope}/{did_name}"
        local_file = os.path.join(temp_dir, os.path.basename(key))

        logging.info(f"[INFO] Processing {key} (size={filesize} bytes)")

        refresh_token(token_file)

        if check_file_on_tape(tape_url):
            logging.info(f"[INFO] File already exists on tape: {did_name} – skipping copy.")
        else:
            if dry_run:
                logging.info(f"[DRY-RUN] Would download and copy {key} to tape")
            else:
                try:
                    s3.download_file(bucket, key, local_file)
                except ClientError as ce:
                    code = ce.response.get('Error', {}).get('Code')
                    logging.warning(f"[SKIP] Download failed for {key} – Code: {code}")
                    continue
                except BotoCoreError as be:
                    logging.error(f"[ERROR] S3 client error for {key}: {be}")
                    continue

                if upload_to_tape(local_file, tape_url):
                    os.remove(local_file)
                else:
                    continue

        register_in_rucio(scope, did_name, tape_rse, filesize, dry_run=dry_run)

def get_s3(endpint):
    if not endpint:
        S3_ENDPOINT = "https://swift.recas.ba.infn.it/"
        access_key = os.environ.get('BA_ACCESS_KEY_ID')
        secret_key = os.environ.get('BA_SECRET_ACCESS_KEY')

        if not access_key or not secret_key:
            logging.error("[FATAL] Missing S3 credentials in environment.")
            exit(1)

        s3 = get_s3_client(S3_ENDPOINT, access_key, secret_key)
    else:
        S3_ENDPOINT = "https://minio.cloud.infn.it/"
        s3 = get_s3_sts_client(S3_ENDPOINT, args.s3_token_file)
    return(s3)
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--bucket', required=True)
    parser.add_argument('--prefix', help='Prefix on S3 to process (ignored if --file-list is used)')
    parser.add_argument('--file-list', help='Path to file containing list of S3 keys to process')
    parser.add_argument('--scope', required=True)
    parser.add_argument('--tape_token_file', default='./tape_token')
    parser.add_argument('--s3_token_file', default='./token')
    parser.add_argument('--tape_rse', default='T1_USERTAPE')
    parser.add_argument('--temp_dir', default='/tmp')
    parser.add_argument('--log_file', default='register_to_tape.log')
    parser.add_argument('--minio', action='store_true')
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()

    logging.basicConfig(
        filename=args.log_file,
        level=logging.INFO,
        format='[%(asctime)s] %(levelname)s: %(message)s'
    )
    logging.info(f"[START] Bucket: {args.bucket}, Scope: {args.scope}, Prefix: {args.prefix}, File list: {args.file_list}")

    os.environ['RUCIO_CONFIG'] = '/app/.rucio.cfg'

#    if not args.minio:
#        S3_ENDPOINT = "https://swift.recas.ba.infn.it/"
#        access_key = os.environ.get('BA_ACCESS_KEY_ID')
#        secret_key = os.environ.get('BA_SECRET_ACCESS_KEY')
#
#        if not access_key or not secret_key:
#            logging.error("[FATAL] Missing S3 credentials in environment.")
#            exit(1)
#
#        s3 = get_s3_client(S3_ENDPOINT, access_key, secret_key)
#    else:
#        S3_ENDPOINT = "https://minio.cloud.infn.it/"
#        s3 = get_s3_sts_client(S3_ENDPOINT, args.s3_token_file)

    s3 = get_s3(args.minio)
    try:
        process_s3_files(
            args.minio,
            bucket=args.bucket,
            prefix=args.prefix,
            scope=args.scope,
            tape_rse=args.tape_rse,
            temp_dir=args.temp_dir,
            token_file=args.tape_token_file,
            dry_run=args.dry_run,
            file_list=args.file_list
        )
    except Exception as e:
        logging.error(f"[FATAL] Processing failed: {e}")

    logging.info("[END] Processing complete.")
