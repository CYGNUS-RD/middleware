#!/bin/bash

# === CONFIGURAZIONE ===
#REMOTE="cygno_ba"
#BASE_PATH="cygno-analysis"

#!/bin/bash

# === INPUT UTENTE ===
read -rp "📡 Inserisci il nome del remote Rclone (es: cygno_ba): " REMOTE
if [[ -z "$REMOTE" ]]; then
    echo "❌ Errore: REMOTE non può essere vuoto."
    exit 1
fi

read -rp "📁 Inserisci il path di base nel remote (es: cygno-analysis): " BASE_PATH
if [[ -z "$BASE_PATH" ]]; then
    echo "❌ Errore: BASE_PATH non può essere vuoto."
    exit 1
fi

echo -e "\n✅ Configurazione:"
echo "   REMOTE     = $REMOTE"
echo "   BASE_PATH  = $BASE_PATH"
read -rp $'\n❓ Confermi di voler procedere con questi parametri? [y/N] ' CONFIRM

if [[ ! "$CONFIRM" =~ ^[Yy]$ ]]; then
    echo "⛔ Annullato dall'utente."
    exit 0
fi





THRESHOLD=$((10 * 1024 * 1024 * 1024))         # 10 GB
THRESHOLD=$((1 * 1024 * 1024 * 1024))         # 10 GB
SMALL_FILE_THRESHOLD=$((100 * 1024 * 1024))    # 100 MB
BATCH_TARGET_SIZE=$((250 * 1024 * 1024))       # 250 MB
TMP_DIR="/tmp/rclone_compress"
MIN_SIZE_CHECK=$((100 * 1024 * 1024))          # 100 MB per verifica finale
dry_run=false                                   # <== IMPOSTA SU false PER ESEGUIRE

set -o pipefail
set -e

declare -A visited_paths

mkdir -p "$TMP_DIR"

print_entry() {
    local path="$1"
    local type="$2"
    local size_bytes="$3"

    if [[ "$size_bytes" =~ ^[0-9]+$ ]]; then
        size_mb=$(awk "BEGIN { printf \"%.2f\", $size_bytes / (1024 * 1024) }")
        echo -e "${path}\t${type}\t${size_mb} MB"
    else
        echo -e "${path}\t${type}\tErrore"
    fi
}

normalize_path() {
    echo "$1" | sed -E 's:/+:/:g' | sed -E 's:/*$::'
}

compress_and_replace() {

    local remote_dir="$1"
    local local_copy="${TMP_DIR}/$(basename "$remote_dir")"

    echo "Copio in locale: $remote_dir → $local_copy"
    if ! $dry_run; then
       rclone copy --s3-no-check-bucket "${REMOTE}:${remote_dir}" "$local_copy" || { echo "❌ rclone copy fallito" >&2; return 1; }
    else
       mkdir -p "$local_copy" # se la directory e' vuota
    fi

    local archive_name="$(basename "$remote_dir").tar.gz"
    local archive_path="${TMP_DIR}/${archive_name}"
    echo "Creo archivio: $archive_path"
    if ! $dry_run; then
	tar -czf "$archive_path" -C "$local_copy/.." "$(basename "$local_copy")" || { echo "❌ tar fallito" >&2; return 1; }
    fi

    local remote_parent="$(dirname "$remote_dir")"

    echo "Carico archivio su: ${REMOTE}:${remote_parent}/$archive_name"
    if ! $dry_run; then
	rclone copy --s3-no-check-bucket "$archive_path" "${REMOTE}:${remote_parent}" || { echo "❌ rclone copy fallito" >&2; return 1; }
    fi

    echo "Rimuovo directory remota: ${REMOTE}:${remote_dir}"
    if ! $dry_run; then
    	rclone delete "${REMOTE}:${remote_dir}" || { echo "❌ rclone delete fallito" >&2; return 1; }
    	rclone rmdirs "${REMOTE}:${remote_dir}" || { echo "❌ rclone rmdirs fallito" >&2; return 1; }
    fi

    echo "Rimuovo temp local: $local_copy + $archive_path"
    if ! $dry_run; then
	rm -rf "$local_copy" "$archive_path" || { echo "❌ remove fallito" >&2; return 1; }
    fi
}

create_tar_batch() {
    local remote_dir="$1"
    shift
    local files=("$@")

    local timestamp=$(date +%s)
    local archive_name="smallfiles_${timestamp}_$RANDOM.tar.gz"
    local archive_path="${TMP_DIR}/${archive_name}"
    local stage_dir="${TMP_DIR}/batch_${timestamp}_$RANDOM"

    mkdir -p "$stage_dir"
    echo "📁 Creo batch da ${#files[@]} file → $archive_name"

    for file_rel in "${files[@]}"; do
        local src="${REMOTE}:${remote_dir}/${file_rel}"
        local dest="${stage_dir}/${file_rel}"
        mkdir -p "$(dirname "$dest")"
        echo "  Copio: $src → $dest"
        if ! $dry_run; then
	    rclone copyto --log-level=ERROR  --s3-no-check-bucket "$src" "$dest" || { echo "❌ rclone copyto fallito" >&2; return 1; }
        fi
    done

    echo "Creo archivio: $archive_path"
    if ! $dry_run; then
	tar -czf "$archive_path" -C "$stage_dir" . || { echo "❌ tar fallito" >&2; return 1; }
    fi
    echo "Carico archivio: $archive_name → ${REMOTE}:${remote_dir}"
    if ! $dry_run; then
	rclone copy --s3-no-check-bucket "$archive_path" "${REMOTE}:${remote_dir}" || { echo "❌ rclone copy fallito" >&2; return 1; }
    fi
    echo "Rimuovo file originali dal remote:"
    for file_rel in "${files[@]}"; do
        echo "   ❌ ${REMOTE}:${remote_dir}/${file_rel}"
        if ! $dry_run; then
		rclone delete "${REMOTE}:${remote_dir}/${file_rel}" || { echo "❌ rclone delete fallito" >&2; return 1; }
	fi
    done

    echo "Rimuovo temporanei locali"
    if ! $dry_run; then
	rm -rf "$stage_dir" "$archive_path" || { echo "❌ rm fallito" >&2; return 1; }
    fi
}

pack_small_files_in_dir() {
    local remote_dir="$1"
    echo "Analisi file piccoli in $remote_dir"

    batch=()
    batch_size=0
    batch_index=1

    rclone lsjson "${REMOTE}:${remote_dir}" --files-only | \
    jq -c --argjson limit "$SMALL_FILE_THRESHOLD" \
        '.[] | select(.Size < $limit and (.Path | startswith(".ipynb_") | not))' |
    while read -r entry; do
        file_path=$(echo "$entry" | jq -r '.Path')
        size=$(echo "$entry" | jq -r '.Size')

        echo "➕ Aggiunto al batch: $file_path ($((size / 1024)) KB)"
        batch+=("$file_path")
        ((batch_size += size))

        if (( batch_size >= BATCH_TARGET_SIZE )); then
            echo "📦 [Batch $batch_index] Raggiunti $((batch_size / (1024 * 1024))) MB → Creo archivio"
            create_tar_batch "$remote_dir" "${batch[@]}"
            batch=()
            batch_size=0
            ((batch_index++))
        fi
    done

    if (( ${#batch[@]} > 0 )); then
        echo "📦 [Batch $batch_index] Ultimo batch da $((batch_size / (1024 * 1024))) MB → Creo archivio"
        create_tar_batch "$remote_dir" "${batch[@]}"
    fi
}



process_dir() {
    local current_path_raw="$1"
    local current_path
    current_path=$(normalize_path "$current_path_raw")

    if [[ -n "${visited_paths[$current_path]+_}" ]]; then
        return
    fi
    visited_paths["$current_path"]=1

    size_bytes=$(rclone size "${REMOTE}:${current_path}" --json | jq '.bytes')
    print_entry "${current_path}/" "DIR" "$size_bytes"

    if [[ ! "$size_bytes" =~ ^[0-9]+$ ]]; then
        return
    fi

    if (( size_bytes < THRESHOLD )); then
        compress_and_replace "$current_path"
        return
    else
        pack_small_files_in_dir "$current_path"
    fi

    mapfile -t entries < <(rclone lsf "${REMOTE}:${current_path}" --format "p")

    for entry in "${entries[@]}"; do
        clean_entry="${entry%/}"

        if [[ "$clean_entry" == .ipynb_* ]]; then
            continue
        fi

        full_path="${current_path}/${clean_entry}"

        if [[ "$entry" == */ ]]; then
            process_dir "$full_path"
        else
            file_size=$(rclone lsjson "${REMOTE}:${current_path}" --files-only \
                | jq --arg name "$clean_entry" 'map(select(.Path==$name and (.Path | startswith(".ipynb_") | not))) | .[0].Size // empty')

            if [[ -n "$file_size" ]]; then
                print_entry "$full_path" "FILE" "$file_size"
            fi
        fi
    done
}

verify_no_small_leftovers() {
    local path="$1"
    echo "🔍 Verifica finale: cerco file o directory < 100MB non compressi..."

    rclone lsjson "${REMOTE}:${path}" --recursive | jq -c '.[]' | while read -r entry; do
        name=$(echo "$entry" | jq -r '.Path')
        size=$(echo "$entry" | jq -r '.Size // 0')
        is_dir=$(echo "$entry" | jq -r '.IsDir')

        if [[ "$name" == .ipynb_* ]]; then
            continue
        fi
        if [[ "$name" == *.tar.gz ]]; then
            continue
        fi
        if (( size < MIN_SIZE_CHECK )); then
            echo "⚠️  WARNING: Piccolo file/directory residuo < 100MB → $name (${size} bytes)"
        fi
    done

    echo "✅ Verifica completata."
}

# === AVVIO ===
BASE_PATH_CLEANED=$(normalize_path "$BASE_PATH")
root_bytes=$(rclone size "${REMOTE}:${BASE_PATH_CLEANED}" --json | jq '.bytes')
print_entry "${BASE_PATH_CLEANED}/" "DIR" "$root_bytes"

process_dir "$BASE_PATH_CLEANED"

verify_no_small_leftovers "$BASE_PATH_CLEANED"
