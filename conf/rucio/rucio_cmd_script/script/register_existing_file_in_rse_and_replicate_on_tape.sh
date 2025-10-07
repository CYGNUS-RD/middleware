#!/bin/bash

# ========= CONFIGURAZIONE ============
SCOPE="cygno-data"
RSE_SOURCE="BACKBONE_USERDISK"
RSE_DEST="T1_USERTAPE"
FULL_PATH="$1"   # es: /data/MAN/run23063.mid.gz
ADD_TAPE_RULE=true   # true o false
# =====================================

if [[ -z "$FULL_PATH" ]]; then
    echo "Usage: $0 /path/to/file"
    exit 1
fi

if [[ ! -f "$FULL_PATH" ]]; then
    echo "ERROR: File not found: $FULL_PATH"
    exit 1
fi

# Estrarre nome relativo per Rucio (dopo MAN/)
NAME=$(basename "$FULL_PATH")
DIR=$(basename "$(dirname "$FULL_PATH")")
DID_NAME="${DIR}/${NAME}"

echo "[INFO] Registering file: $DID_NAME under scope $SCOPE"

# Calcolo adler32 e size
ADLER32=$(adler32sum "$FULL_PATH" | awk '{print $1}')
SIZE=$(stat -c%s "$FULL_PATH")

echo "[INFO] Size: $SIZE bytes"
echo "[INFO] Adler32: $ADLER32"

# 1. add-did
echo "[STEP] Registrazione DID nel catalogo..."
rucio add-did --scope "$SCOPE" --name "$DID_NAME" --type FILE --bytes "$SIZE" --adler32 "$ADLER32"
if [[ $? -ne 0 ]]; then
    echo "[WARN] add-did potrebbe già esistere. Continuo..."
fi

# 2. add-replica
echo "[STEP] Registrazione replica su $RSE_SOURCE..."
rucio add-replica --rse "$RSE_SOURCE" --scope "$SCOPE" --name "$DID_NAME" --bytes "$SIZE" --adler32 "$ADLER32"
if [[ $? -ne 0 ]]; then
    echo "[WARN] add-replica potrebbe già esistere. Continuo..."
fi

# 3. rule per BACKBONE_USERDISK
echo "[STEP] Aggiunta regola per $RSE_SOURCE..."
rucio rule add --copies 1 --rse-exp "$RSE_SOURCE" "${SCOPE}:${DID_NAME}"

# 4. (opzionale) Regola per TAPE
if [[ "$ADD_TAPE_RULE" = true ]]; then
    echo "[STEP] Aggiunta regola per $RSE_DEST (source: $RSE_SOURCE)..."
    rucio rule add --copies 1 --rse-exp "$RSE_DEST" --source-replica-exp "$RSE_SOURCE" "${SCOPE}:${DID_NAME}"
fi

# 5. Verifica finale
echo
echo "[INFO] Verifica finale:"
echo "--------------------------------"
rucio list-dids "${SCOPE}:${DID_NAME}" --filter type=FILE
echo
rucio replica list file "${SCOPE}:${DID_NAME}"
echo
rucio rule list --did "${SCOPE}:${DID_NAME}"
echo "--------------------------------"
echo "[DONE] File registrato e replica gestita con successo!"

