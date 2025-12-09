
#!/usr/bin/env python3
import os
import re
import argparse
import logging
import subprocess
from rucio.client.client import Client
from rucio.common.exception import FileAlreadyExists, DuplicateRule

TAPE_BASE = "davs://xfer-archive.cr.cnaf.infn.it:8443/cygno"

def sh(cmd, env=None):
    out = subprocess.check_output(cmd, stderr=subprocess.STDOUT, env=env)
    return out.decode('utf-8', errors='replace')

def refresh_token(token_file):
    with open(token_file, 'r') as f:
        token = f.read().strip()
    os.environ['BEARER_TOKEN'] = token

def gfal_ls(path, token_file):
    # RIMOSSO "-1" perché non supportato nella tua versione
    refresh_token(token_file)
    txt = sh(["gfal-ls", path], env=os.environ.copy())
    lines = [l.strip() for l in txt.splitlines() if l.strip()]
    return lines

def gfal_stat(path, token_file):
    refresh_token(token_file)
    txt = sh(["gfal-stat", path], env=os.environ.copy())
    # Esempio riga: "Size: 1251135902    regular file"
    m = re.search(r"^\s*Size:\s*([0-9]+)", txt, re.MULTILINE)
    size = int(m.group(1)) if m else None
    return size, txt

def gfal_sum_adler32(path, token_file):
    refresh_token(token_file)
    try:
        txt = sh(["gfal-sum", path, "adler32"], env=os.environ.copy())
        # Può essere "adler32\t7331d30a  /path" oppure solo "7331d30a"
        m = re.search(r"\b([0-9a-fA-F]{8})\b", txt)
        return m.group(1).lower() if m else None
    except subprocess.CalledProcessError as e:
        logging.warning("[WARN] gfal-sum fallita su %s: %s", path, e.output.decode(errors='replace'))
        return None

def register_replica(scope, did_name, rse, size, adler32, dry_run=False):
    client = Client()
    files = [{'scope': scope, 'name': did_name, 'bytes': size}]
    if adler32:
        files[0]['adler32'] = adler32

    try:
        if not dry_run:
            client.add_replicas(rse=rse, files=files, ignore_availability=True)
        logging.info("[OK] Registrata replica %s su %s (size=%s, adler32=%s)",
                     did_name, rse, size, adler32 or "n/a")
    except FileAlreadyExists:
        logging.info("[INFO] Replica già registrata: %s", did_name)
    except Exception as e:
        logging.error("[ERROR] add_replicas fallita per %s: %s", did_name, e)
        return False

    try:
        if not dry_run:
            client.add_replication_rule([{'scope': scope, 'name': did_name}], 1, rse)
        logging.info("[OK] Regola di replica aggiunta per %s", did_name)
    except DuplicateRule:
        logging.info("[INFO] Regola già esistente per %s", did_name)
    except Exception as e:
        logging.error("[ERROR] add_replication_rule fallita per %s: %s", did_name, e)
        return False
    return True

def main():
    ap = argparse.ArgumentParser(description="Registra su Rucio i file già presenti su TAPE (gfal)")
    ap.add_argument("--scope", required=True)
    ap.add_argument("--prefix", required=True, help="prefisso (es. LNF oppure LNF/)")
    ap.add_argument("--source_rse", default="T1_USERTAPE")
    ap.add_argument("--rucio_config", default=os.path.expanduser("~/.rucio.cfg"))
    ap.add_argument("--tape_token_file", required=True, help="file con il BEARER_TOKEN per gfal")
    ap.add_argument("--log_file", default="register_existing_tape.log")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    logging.basicConfig(
        filename=args.log_file,
        level=logging.INFO,
        format='[%(asctime)s] %(levelname)s: %(message)s'
    )

    # Rucio config
    os.environ['RUCIO_CONFIG'] = args.rucio_config

    # Normalizza prefix: niente slash iniziale/finale ripetuti
    prefix = args.prefix.strip("/")
    tape_dir = f"{TAPE_BASE}/{args.scope}/{prefix}" if prefix else f"{TAPE_BASE}/{args.scope}"

    logging.info("[START] Scansione TAPE in: %s (scope=%s, rse=%s, dry-run=%s)",
                 tape_dir, args.scope, args.source_rse, args.dry_run)

    try:
        entries = gfal_ls(tape_dir, args.tape_token_file)
    except subprocess.CalledProcessError as e:
        logging.error("[FATAL] gfal-ls fallita su %s: %s", tape_dir, e.output.decode(errors='replace'))
        logging.info("[END] Processing complete.")
        return

    for name in entries:
        did_name = f"{prefix}/{name}" if prefix else name
        tape_url = f"{TAPE_BASE}/{args.scope}/{did_name}"
        try:
            size, _ = gfal_stat(tape_url, args.tape_token_file)
            if size is None:
                logging.error("[ERROR] Impossibile ricavare size da gfal-stat per %s", tape_url)
                continue

            adler = gfal_sum_adler32(tape_url, args.tape_token_file)
            ok = register_replica(args.scope, did_name, args.source_rse, size, adler, dry_run=args.dry_run)
            if not ok:
                logging.error("[ERROR] Registrazione fallita per %s", did_name)
        except subprocess.CalledProcessError as e:
            out = e.output.decode(errors='replace')
            logging.warning("[WARN] gfal-stat/sum fallita su %s: %s", tape_url, out)
        except Exception as e:
            logging.error("[ERROR] Eccezione su %s: %s", tape_url, e)

    logging.info("[END] Processing complete.")

if __name__ == "__main__":
    main()

