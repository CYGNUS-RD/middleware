import os
import argparse
import logging
from rucio.client.client import Client
from rucio.common.exception import DuplicateRule

# Setup logging to file
logging.basicConfig(filename='replica_status.log',
                    level=logging.INFO,
                    format='%(asctime)s %(levelname)s: %(message)s')

def replicate_files(scope, prefix, source_rse, dest_rse, account, file_list):
    client = Client()
    print(scope, prefix, source_rse, dest_rse, account, file_list)
    try:
        with open(file_list, 'r') as f:
            filenames = [line.strip() for line in f if line.strip()]
    except Exception as e:
        print(f"[ERROR] Cannot read file list: {e}")
        logging.error(f"Cannot read file list {file_list}: {e}")
        return

    print(f"[INFO] Processing {len(filenames)} files from {file_list} with prefix '{prefix}' ...")
    logging.info(f"Processing {len(filenames)} files from {file_list} with prefix '{prefix}'")

    for filename in filenames:
        full_name = f"{prefix}/{filename}"
        did = [{'scope': scope, 'name': full_name}]

        try:
            # Add replication rule
            client.add_replication_rule(did, 1, dest_rse, account=account)
            msg = f"[OK] Rule added for {full_name} to {dest_rse}"
            print(msg)
            logging.info(msg)

        except DuplicateRule:
            msg = f"[SKIP] Rule already exists for {full_name} on {dest_rse}"
            print(msg)
            logging.info(msg)

        except Exception as e:
            msg = f"[ERROR] Failed to replicate {full_name}: {e}"
            print(msg)
            logging.error(msg)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Replicate files from source RSE to destination RSE based on a list.")
    parser.add_argument('--scope', required=True, help='Rucio scope, e.g., cygno-data')
    parser.add_argument('--prefix', required=True, help='Prefix/folder inside the scope, e.g., LNGS')
    parser.add_argument('--source_rse', required=True, help='Source RSE, e.g., T1_USERTAPE')
    parser.add_argument('--dest_rse', required=True, help='Destination RSE, e.g., CNAF_USERDISK')
    parser.add_argument('--account', required=True, help='Rucio account to use, e.g., rucio-daq')
    parser.add_argument('--file_list', required=True, help='Path to file containing list of filenames to replicate')

    args = parser.parse_args()
    replicate_files(args.scope, args.prefix, args.source_rse, args.dest_rse, args.account, args.file_list)
