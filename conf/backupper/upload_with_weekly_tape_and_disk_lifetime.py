#!/usr/bin/env python3
import os
import sys
import argparse
from datetime import datetime
from zoneinfo import ZoneInfo

from rucio.client.client import Client
from rucio.client.uploadclient import UploadClient
from rucio.common.exception import DuplicateRule, NoFilesUploaded, RucioException

# RUCIO tool
# G. Mazzitelli 2025
# copia i file da DAQ (o comunque da locale) in CLOUD e li replica su TAPE
#
# MODIFICHE:
# 1) Tutti i file su CNAF_USERDISK hanno lifetime <= 30 giorni (default 30 o a parametro)
# 2) Solo in un certo giorno della settimana (default domenica, a parametro) si crea anche la rule su T1_USERTAPE
# 3) Se la rule su CNAF_USERDISK esiste già, la lifetime viene aggiornata (update_replication_rule)
#
#| Exit Code | Meaning                                            |
#| --------- | -------------------------------------------------- |
#| 0         | Upload ok (o già presente) + regole create/aggiornate |
#| 2         | Upload failed                                      |
#| 3         | Rule creation/update failed                         |
#| 4         | Client creation failed                             |

DOW_MAP = {
    "mon": 0, "monday": 0,
    "tue": 1, "tuesday": 1,
    "wed": 2, "wednesday": 2,
    "thu": 3, "thursday": 3,
    "fri": 4, "friday": 4,
    "sat": 5, "saturday": 5,
    "sun": 6, "sunday": 6,
}

def parse_weekday(s: str) -> int:
    key = s.strip().lower()
    if key not in DOW_MAP:
        raise ValueError(
            f"Invalid weekday '{s}'. Use: mon,tue,wed,thu,fri,sat,sun (or full names)."
        )
    return DOW_MAP[key]


def main():
    # Config file path from ENV or default
    rucio_cfg = os.environ.get("RUCIO_CONFIG", "/home/.rucio.cfg")
    os.environ["RUCIO_CONFIG"] = rucio_cfg

    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", required=True, help="File to upload")
    parser.add_argument("--bucket", default="cygno-data", help="Bucket/scope")
    parser.add_argument("--did_name", required=True, help="DID name")
    parser.add_argument("--upload_rse", default="CNAF_USERDISK", help="Upload RSE (default: CNAF_USERDISK)")
    parser.add_argument("--transfer_rse", default="T1_USERTAPE", help="Transfer RSE (default: T1_USERTAPE)")
    parser.add_argument("--account", required=True, help="Rucio account")

    # NEW: disk lifetime in days (default 30), enforce max 30 (configurable)
    parser.add_argument(
        "--disk-lifetime-days",
        type=int,
        default=30,
        help="Lifetime for CNAF_USERDISK rule in days (default: 30)"
    )
    parser.add_argument(
        "--max-disk-lifetime-days",
        type=int,
        default=30,
        help="Hard cap for disk lifetime in days (default: 30). "
             "If disk-lifetime-days > cap, it will be reduced to cap."
    )

    # NEW: weekday trigger for tape replication (default Sunday)
    parser.add_argument(
        "--tape-weekday",
        default="sunday",
        help="Create tape rule only on this weekday (default: sunday). "
             "Values: mon,tue,wed,thu,fri,sat,sun (or full names)."
    )

    # NEW: timezone used to compute weekday (default Europe/Rome)
    parser.add_argument(
        "--timezone",
        default="Europe/Rome",
        help="Timezone used to decide weekday (default: Europe/Rome)"
    )

    # optional verbose
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")

    args = parser.parse_args()

    def info(msg: str):
        if args.verbose:
            print(f"[INFO] {msg}")

    def warn(msg: str):
        print(f"[WARNING] {msg}")

    def err(msg: str):
        print(f"[ERROR] {msg}", file=sys.stderr)

    # Enforce disk lifetime <= max
    disk_days = args.disk_lifetime_days
    cap_days = args.max_disk_lifetime_days

    if disk_days > cap_days:
        info(f"disk-lifetime-days={disk_days} > cap={cap_days}. Capping to {cap_days}.")
        disk_days = cap_days
    if disk_days < 1:
        info(f"disk-lifetime-days={disk_days} < 1. Setting to 1.")
        disk_days = 1

    disk_lifetime_seconds = disk_days * 86400

    try:
        tape_dow = parse_weekday(args.tape_weekday)
    except ValueError as e:
        err(str(e))
        sys.exit(4)

    try:
        tz = ZoneInfo(args.timezone)
    except Exception as e:
        err(f"Invalid timezone '{args.timezone}': {e}")
        sys.exit(4)

    today_dow = datetime.now(tz).weekday()  # Mon=0 ... Sun=6 in chosen timezone
    do_tape = (today_dow == tape_dow)

    info(f"RUCIO_CONFIG={rucio_cfg}")
    info(f"DID={args.bucket}:{args.did_name}")
    info(f"Upload RSE={args.upload_rse}")
    info(f"Disk lifetime={disk_days} days ({disk_lifetime_seconds} seconds), cap={cap_days} days")
    info(f"Tape weekday trigger={args.tape_weekday} (today weekday={today_dow} in {args.timezone}), will_create_tape_rule={do_tape}")

    # Initialize clients
    try:
        upload_client = UploadClient()
        transfer_client = Client()
    except Exception as e:
        err(f"Client creation failed: {str(e)}")
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

    # Upload
    try:
        info(f"Uploading file: {args.file}")
        upload_client.upload(item)
        upload_done = True
        info("Upload completed.")
    except NoFilesUploaded:
        warn(f"File '{args.file}' is already uploaded.")
        upload_done = True
    except Exception as e:
        err(f"Upload failed: {str(e)}")
        sys.exit(2)

    did = [{"scope": args.bucket, "name": args.did_name}]

    # Helper: ensure disk rule lifetime by updating the existing rule
    def ensure_disk_rule_lifetime(rule_rse: str, lifetime_seconds: int) -> None:
        """
        Find the disk rule for this DID/account and set lifetime.
        Works even if the rule was created by UploadClient (DuplicateRule case).
        """
        rules = transfer_client.list_replication_rules(filters={
            "account": args.account,
            "scope": args.bucket,
            "name": args.did_name
        })

        for r in rules:
            if r.get("rse_expression") == rule_rse and int(r.get("copies", 0)) == 1:
                rid = r["id"]
                transfer_client.update_replication_rule(rid, {"lifetime": lifetime_seconds})
                info(f"Updated DISK rule lifetime: rule_id={rid}, lifetime={lifetime_seconds}s")
                return

        raise RuntimeError(f"Cannot find DISK rule on {rule_rse} to update lifetime.")

    # 1) Ensure DISK rule exists (create if missing)
    try:
        info(f"Ensuring DISK rule exists on {args.upload_rse}")
        transfer_client.add_replication_rule(did, 1, args.upload_rse, account=args.account)
        info("Disk rule created.")
    except DuplicateRule:
        info(f"Disk rule already exists on {args.upload_rse}.")
    except Exception as e:
        err(f"Disk rule creation failed: {str(e)}")
        sys.exit(3)

    # 2) Always enforce DISK rule lifetime (this guarantees EXPIRES is set)
    try:
        info(f"Enforcing DISK rule lifetime={disk_lifetime_seconds}s on {args.upload_rse}")
        ensure_disk_rule_lifetime(args.upload_rse, disk_lifetime_seconds)
    except Exception as e:
        err(f"Failed to set disk rule lifetime: {e}")
        sys.exit(3)

    # 3) Tape rule only on selected weekday
    if do_tape:
        try:
            info(f"Adding replication rule to {args.transfer_rse} (weekday trigger matched)")
            transfer_client.add_replication_rule(did, 1, args.transfer_rse, account=args.account)
            info("Tape rule created.")
        except DuplicateRule:
            warn(f"Replica already exists on {args.transfer_rse}.")
        except Exception as e:
            err(f"Replica creation failed: {str(e)}")
            sys.exit(3)
    else:
        info("Tape rule NOT created (weekday trigger not matched).")

    # Exit logic: success if upload ok and rules ok
    if upload_done:
        sys.exit(0)
    else:
        # in pratica non si arriva qui, perché upload fallito esce prima con 2
        sys.exit(2)


if __name__ == "__main__":
    main()
