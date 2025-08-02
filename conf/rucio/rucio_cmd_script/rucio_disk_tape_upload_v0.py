import os
from rucio.client.client import Client
from rucio.client.uploadclient import UploadClient
import argparse

# Prende il path da ENV o default
rucio_cfg = os.environ.get('RUCIO_CONFIG', '/home/.rucio.cfg')
os.environ['RUCIO_CONFIG'] = rucio_cfg

# Arg parser
parser = argparse.ArgumentParser()
parser.add_argument('--file', required=True)
parser.add_argument('--bucket', required=True)
parser.add_argument('--did_name', required=True)
parser.add_argument('--upload_rse', required=True)
parser.add_argument('--transfer_rse', required=True)
parser.add_argument('--account', required=True)
args = parser.parse_args()

# Upload
upload_client = UploadClient()
item = [{
    "path": args.file,
    "rse": args.upload_rse,
    "did_scope": args.bucket,
    "did_name": args.did_name
}]
upload_client.upload(item)

# Transfer
transfer_client = Client()
did = [{'scope': args.bucket, 'name': args.did_name}]
transfer_client.add_replication_rule(did, 1, args.transfer_rse, account=args.account)
