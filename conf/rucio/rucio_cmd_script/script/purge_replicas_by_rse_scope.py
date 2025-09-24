#!/usr/bin/env python3
# purge_replicas_by_scope_rse.py
#
# Elenca tutti i FILE (DID) di uno scope (con eventuale prefix) che hanno
# una replica su un RSE specifico e ne cancella l’esistenza su quell’RSE.
#
# NOTA: usa rse_expression=<RSE> in list_replicas (correzione al posto di rses=).

import os
import sys
import argparse
import logging
from itertools import islice

from rucio.client.didclient import DIDClient
from rucio.client.replicaclient import ReplicaClient
from rucio.client.client import Client
from rucio.common.exception import DataIdentifierNotFound, RucioException

LOG = logging.getLogger("purge")

def chunked(iterable, size):
    it = iter(iterable)
    while True:
        batch = list(islice(it, size))
        if not batch:
            break
        yield batch

def main():
    parser = argparse.ArgumentParser(description="Cancella repliche su un RSE per tutti i file in uno scope (opz. prefix).")
    parser.add_argument("--rse", required=True, help="RSE di cui rimuovere le repliche (es. T1_USERTAPE)")
    parser.add_argument("--scope", required=True, help="Scope (es. cygno-data)")
    parser.add_argument("--prefix", default="", help="Prefisso dei nomi (p.es. 'LNF/' ; vuoto per tutto lo scope)")
    parser.add_argument("--rucio_config", default=None, help="Path a file .rucio.cfg (opzionale)")
    parser.add_argument("--dry-run", action="store_true", help="Mostra cosa verrebbe cancellato, senza cancellare")
    parser.add_argument("--chunk", type=int, default=500, help="Dimensione batch per le chiamate (default: 500)")
    parser.add_argument("--log-file", default="purge_replicas.log", help="File di log")
    parser.add_argument("-v", "--verbose", action="store_true", help="Log più verboso")
    args = parser.parse_args()

    logging.basicConfig(
        filename=args.log_file,
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="[%(asctime)s] %(levelname)s: %(message)s"
    )

    if args.rucio_config:
        os.environ["RUCIO_CONFIG"] = args.rucio_config

    rse = args.rse
    scope = args.scope
    prefix = args.prefix

    LOG.info(f"[START] RSE={rse}, scope={scope}, prefix='{prefix}', dry-run={args.dry_run}")

    did_client = DIDClient()
    replica_client = ReplicaClient()
    core_client = Client()

    # 1) Lista DIDs (solo FILE) nello scope con l'eventuale prefisso.
    try:
        filters = {"type": "file"}
        # Il filtro per nome è espresso come pattern (glob)
        name_pattern = f"{prefix}*" if prefix else "*"
        dids_iter = did_client.list_dids(scope=scope, filters={"name": name_pattern, "type": "file"}, long=False)
        did_names = list(dids_iter)
        LOG.info(f"[INFO] Trovati {len(did_names)} DIDs nello scope con prefix.")
    except DataIdentifierNotFound:
        LOG.error("[FATAL] Scope o prefisso non trovati.")
        sys.exit(1)
    except Exception as e:
        LOG.error(f"[FATAL] Errore durante list_dids: {e}")
        sys.exit(1)

    to_delete_total = 0
    deleted_total = 0

    # 2) Per chunk, trova le repliche presenti su quell'RSE e prepara la lista da cancellare
    for names_chunk in chunked(did_names, args.chunk):
        dids_chunk = [{"scope": scope, "name": n} for n in names_chunk]

        try:
            # >>> Correzione qui: rse_expression=rse (NON 'rses')
            replicas = list(replica_client.list_replicas(
                dids=dids_chunk,
                rse_expression=rse,
                all_states=True  # include AVAILABLE/UNAVAILABLE/…
            ))
        except Exception:
            LOG.error("Errore in list_replicas. Controlla i log.")
            sys.exit(1)

        files_on_rse = []
        for rep in replicas:
            states = rep.get("states") or {}
            # Se l'RSE compare negli stati, consideriamo la replica da cancellare
            if rse in states:
                files_on_rse.append({"scope": rep["scope"], "name": rep["name"]})

        if not files_on_rse:
            continue

        to_delete_total += len(files_on_rse)

        if args.dry_run:
            for f in files_on_rse:
                LOG.info(f"[DRY-RUN] Cancellerei replica su {rse}: {f['scope']}:{f['name']}")
            continue

        # 3) Cancellazione delle repliche su quell'RSE
        try:
            core_client.delete_replicas(rse=rse, files=files_on_rse)
            deleted_total += len(files_on_rse)
            for f in files_on_rse:
                LOG.info(f"[OK] Cancellata replica su {rse}: {f['scope']}:{f['name']}")
        except RucioException as e:
            LOG.error(f"[ERROR] delete_replicas fallita per un batch ({len(files_on_rse)} files): {e}")
        except Exception as e:
            LOG.error(f"[ERROR] delete_replicas – eccezione inattesa: {e}")

    LOG.info(f"[END] Totale trovate su {rse}: {to_delete_total} – Cancellate: {deleted_total} – dry-run={args.dry_run}")

if __name__ == "__main__":
    main()

