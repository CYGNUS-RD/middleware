#!/usr/bin/env python3
import argparse, sys, logging
from itertools import islice
from rucio.client import Client
from rucio.client.ruleclient import RuleClient
from rucio.client.didclient import DIDClient
from rucio.common.exception import RucioException

LOG = logging.getLogger("purge-rules")

def chunked(it, n):
    it = iter(it)
    while True:
        batch = list(islice(it, n))
        if not batch: break
        yield batch

def main():
    ap = argparse.ArgumentParser("Purge delle regole per RSE e scope (opz. prefix)")
    ap.add_argument("--rse", required=True)
    ap.add_argument("--scope", required=True)
    ap.add_argument("--prefix", default="")
    ap.add_argument("--chunk", type=int, default=200)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO,
                        format="[%(asctime)s] %(levelname)s: %(message)s")

    client = Client()
    rulec  = RuleClient()
    didc   = DIDClient()

    name_pat = f"{args.prefix}*" if args.prefix else "*"

    LOG.info("[START] rse_expr=%s scope=%s name~='%s' dry=%s",
         args.rse, args.scope, name_pat, getattr(args, "dry_run", None))

    total = deleted = 0

    # 1) enumeriamo i DIDs (file/dataset/containers a scelta; qui tutto)

# fare la lista dei dids dinamicamente
    name_pattern = f"{args.prefix}*" if args.prefix else "*"

    dids = didc.list_dids(
        scope=args.scope,
        filters={"name": name_pattern, "type": "file"},  # <-- usa il filtro
        long=False
    )

# fare la ista su file e prenderla da li.
# rucio list-dids ${SCOPE}:"${PREFIX}" --filter type=FILE | awk -F'|' 'NR>3 && NF>=2 { s=$2; gsub(/^[ \t]+|[ \t]+$/,"",s); if(s!="") print s }' > /tmp/files.txt

#    with open("/tmp/files.txt") as fh:
#        def did_lines():
#            for line in fh:
#                did = line.strip()
#                if did and ":" in did:
#                    yield did.split(":", 1)[1]  # solo name
#
#    dids = []
#    with open("/tmp/files.txt") as fh:
#        for line in fh:
#            did = line.strip()
#            if did and ":" in did:
#               scope, name = did.split(":", 1)
#            dids.append({"scope": scope, "name": name})


    for batch in chunked(dids, args.chunk):
        # 2) recupera le regole per ognuno dei DIDs
        for name in batch:
            try:
                # filtra per rse_expression e DID
                rules = rulec.list_replication_rules(filters={
                    "rse_expression": args.rse,
                    "scope": args.scope,
                    "name": name,
                })
                rules = list(rules)
            except Exception as e:
                LOG.error(f"[WARN] list_replication_rules failed for {args.scope}:{name}: {e}")
                continue

            if not rules:
                continue

            for ru in rules:
                rid = ru.get("id")
                total += 1
                if args.dry_run:
                    LOG.info(f"[DRY-RUN] cancellerei rule {rid} on {args.rse} for {args.scope}:{name}")
                    continue
                try:
                    rulec.delete_replication_rule(rid)
                    deleted += 1
                    LOG.info(f"[OK] deleted rule {rid} ({args.scope}:{name})")
                except RucioException as e:
                    LOG.error(f"[ERROR] delete rule {rid}: {e}")
                except Exception as e:
                    LOG.error(f"[ERROR] unexpected on {rid}: {e}")

    LOG.info(f"[END] regole trovate: {total} – cancellate: {deleted} – dry-run={args.dry_run}")

if __name__ == "__main__":
    main()
