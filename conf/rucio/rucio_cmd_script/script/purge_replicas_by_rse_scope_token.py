def purge_replicas(rse, scope, prefix, dry_run=False, batch_size=256, hb_every=2000):
    client = Client()
    did_client = DIDClient()

    pattern = f"{prefix}%" if prefix else "%"

    logging.info(f"[INFO] Recupero DIDs in scope={scope}, prefix='{prefix}', pattern='{pattern}' ...")

    dids = []
    # Strategy A: generica
    try:
        a_iter = did_client.list_dids(scope=scope, filters={'name': pattern})
        a = [d if isinstance(d, str) else d.get('name') for d in a_iter]
        dids = [x for x in a if x]
        logging.info(f"[DBG] Strategy A -> {len(dids)} candidati")
    except Exception as e:
        logging.warning(f"[WARN] list_dids(A) fallita: {e}")

    # Strategy B: forza SOLO file (se supportato)
    if not dids:
        try:
            b_iter = did_client.list_dids(scope=scope, filters={'name': pattern, 'type': 'file'})
            b = [d if isinstance(d, str) else d.get('name') for d in b_iter]
            dids = [x for x in b if x]
            logging.info(f"[DBG] Strategy B (type=file) -> {len(dids)} candidati")
        except Exception as e:
            logging.info(f"[DBG] Strategy B non supportata qui: {e}")

    # Strategy C: espandi dataset/container in file
    if not dids:
        try:
            # prendi dataset, poi espandi
            ds_iter = did_client.list_dids(scope=scope, filters={'name': pattern, 'type': 'dataset'})
            datasets = [d if isinstance(d, str) else d.get('name') for d in ds_iter]
            datasets = [x for x in datasets if x]
            logging.info(f"[DBG] Strategy C: trovati {len(datasets)} dataset, espando in file...")
            file_names = []
            for i, ds in enumerate(datasets, 1):
                try:
                    for f in did_client.list_files(scope=scope, name=ds):
                        nm = f.get('name')
                        if nm:
                            file_names.append(nm)
                except Exception as e:
                    logging.warning(f"[WARN] list_files({ds}) fallita: {e}")
                if i % 100 == 0:
                    logging.info(f"[HB] Espansi {i}/{len(datasets)} dataset")
            dids = sorted(set(file_names))
            logging.info(f"[DBG] Strategy C -> {len(dids)} file totali espansi")
        except Exception as e:
            logging.warning(f"[WARN] Strategy C fallita: {e}")

    logging.info(f"[INFO] Trovati {len(dids)} DIDs (file) nello scope con prefix '{prefix}'.")

    # --- resto invariato ---
    batch = []
    processed = 0
    total = len(dids)

    for name in dids:
        batch.append({'scope': scope, 'name': name})
        processed += 1

        if len(batch) >= batch_size:
            _delete_batch(client, rse, batch, dry_run)
            batch = []

        if processed % hb_every == 0:
            logging.info(f"[HB] Progress: {processed}/{total}")

    if batch:
        _delete_batch(client, rse, batch, dry_run)

