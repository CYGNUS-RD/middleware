#!/bin/bash

REMOTE="cygno_ba"
REMOTE_PATH="cygno-analysis"
MIN_BYTES=$((100 * 1024 * 1024))  # 100MB

echo "== Scansione file < 100MB in ${REMOTE}:${REMOTE_PATH} =="

rclone lsjson "${REMOTE}:${REMOTE_PATH}" --recursive --files-only --fast-list \
| jq -r '.[] | select(.Size? != null) | select(.Size < '"$MIN_BYTES"') | "\(.Size)\t\(.Path)"' \
| awk -F'\t' '{
    size=$1; path=$2;
    path_lc = tolower(path);
    if (path_lc ~ /\.(tar(\.gz|\.bz2|\.xz)?|tgz|tbz2|txz|zip|7z|rar)$/) next;
    print size "\t" path;
}' \
| tee /tmp/small_files_found.txt

echo
echo "=== Fine ==="
wc -l /tmp/small_files_found.txt
