#!/bin/bash

REMOTE="minio"
BASE_PATH="cygno-analysis"

THRESHOLD=$((10 * 1024 * 1024 * 1024))  # 10 GB
declare -A visited_paths  # per evitare loop

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
    # Elimina slash multipli e slash finali inutili
    echo "$1" | sed -E 's:/+:/:g' | sed -E 's:/*$::'
}

process_dir() {
    local current_path_raw="$1"
    local current_path
    current_path=$(normalize_path "$current_path_raw")

    # Evita di processare di nuovo la stessa path
    if [[ -n "${visited_paths[$current_path]+_}" ]]; then
        return
    fi
    visited_paths["$current_path"]=1

    # Stampa la size della directory corrente
    size_bytes=$(rclone size "${REMOTE}:${current_path}" --json | jq '.bytes')
    print_entry "${current_path}/" "DIR" "$size_bytes"

    # Non scendere se < 10GB
    if [[ ! "$size_bytes" =~ ^[0-9]+$ ]] || (( size_bytes < THRESHOLD )); then
        return
    fi

    # Elenca contenuto
    mapfile -t entries < <(rclone lsf "${REMOTE}:${current_path}" --format "p")

    for entry in "${entries[@]}"; do
        clean_entry="${entry%/}"

        # Escludi nomi che iniziano con .ipynb_
        if [[ "$clean_entry" == .ipynb_* ]]; then
            continue
        fi

        full_path="${current_path}/${clean_entry}"

        if [[ "$entry" == */ ]]; then
            # Directory → scendi se necessario
            process_dir "$full_path"
        else
            # File → ottieni size
            file_size=$(rclone lsjson "${REMOTE}:${current_path}" --files-only \
                | jq --arg name "$clean_entry" 'map(select(.Path==$name and (.Path | startswith(".ipynb_") | not))) | .[0].Size // empty')

            if [[ -n "$file_size" ]]; then
                print_entry "$full_path" "FILE" "$file_size"
            fi
        fi
    done
}

# Pulisce la path iniziale e avvia
BASE_PATH_CLEANED=$(normalize_path "$BASE_PATH")
root_bytes=$(rclone size "${REMOTE}:${BASE_PATH_CLEANED}" --json | jq '.bytes')
print_entry "${BASE_PATH_CLEANED}/" "DIR" "$root_bytes"

process_dir "$BASE_PATH_CLEANED"
