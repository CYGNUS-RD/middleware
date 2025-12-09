import os
import sys
import argparse
from rucio.client.client import Client
from rucio.client.uploadclient import UploadClient
from rucio.common.exception import DataIdentifierAlreadyExists, FileAlreadyExists, DuplicateRule, NoFilesUploaded, RucioException

# RUCIO tool
# G. Mazzitelli 2025
# copia i file da DAQ (o comunque da locale) in CLOUD e li replica su TAPE
# usage
#                          "--bucket", bucket,
#                          "--did_name", key+filename,
#                          "--upload_rse", "CNAF_USERDISK",
#                          "--transfer_rse", "T1_USERTAPE",
#                          "--account", "rucio-daq"
#| Exit Code | Meaning                                            |
#| --------- | -------------------------------------------------- |
#| 0         | Upload and replica created (or both already exist) |
#| 1         | File already uploaded, replica just created        |
#| 2         | Upload failed                                      |
#| 3         | Upload done, replica failed                        |
#| 4         | Client creation failed                             |

# Config file path from ENV or default
rucio_cfg = os.environ.get('RUCIO_CONFIG', '/home/.rucio.cfg')
os.environ['RUCIO_CONFIG'] = rucio_cfg


# Parse arguments
parser = argparse.ArgumentParser()
parser.add_argument('--file', required=True, help="File to upload")
parser.add_argument('--bucket', required=True, help="Bucket/scope")
parser.add_argument('--did_name', required=True, help="DID name")
parser.add_argument('--upload_rse', required=True, help="Upload RSE")
parser.add_argument('--transfer_rse', required=True, help="Transfer RSE")
parser.add_argument('--account', required=True, help="Rucio account")
args = parser.parse_args()

# Initialize clients
try:
     upload_client = UploadClient()
     transfer_client = Client()
except Exception as e:
    print(f"[ERROR] Client creation failed: {str(e)}")
    sys.exit(4)

# Define upload item
item = [{
    "path": args.file,
    "rse": args.upload_rse,
    "did_scope": args.bucket,
    "did_name": args.did_name
}]

# Track status
upload_done = False
replica_done = False

try:
    print(f"[INFO] Uploading file: {args.file}")
    upload_client.upload(item)
    upload_done = True
    print("[SUCCESS] Upload completed.")
except NoFilesUploaded:
    print(f"[WARNING] File '{args.file}' is already uploaded.")
except Exception as e:
    print(f"[ERROR] Upload failed: {str(e)}")
    sys.exit(2)

# Try to add replication rule
did = [{'scope': args.bucket, 'name': args.did_name}]
try:
    print(f"[INFO] Adding replication rule to {args.transfer_rse}")
    transfer_client.add_replication_rule(did, 1, args.transfer_rse, account=args.account)
    replica_done = True
    print("[SUCCESS] Replica created.")
except DuplicateRule:
    print(f"[WARNING] Replica already exists on {args.transfer_rse}.")
    replica_done = True
except Exception as e:
    print(f"[ERROR] Replica creation failed: {str(e)}")
    sys.exit(3)

# Exit status logic
if upload_done and replica_done:
    sys.exit(0)
elif not upload_done and replica_done:
    sys.exit(1)
else:
    sys.exit(2)
