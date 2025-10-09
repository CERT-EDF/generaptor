#!/usr/bin/env sh
set -e
# exec
exec generaptor \
    --cache /generaptor/cache \
    --config /generaptor/config \
    "$@"
