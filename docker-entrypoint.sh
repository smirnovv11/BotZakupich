#!/bin/sh
set -e

case "${RUN_MIGRATIONS:-false}" in
  true|1|yes|on)
    alembic upgrade head
    ;;
esac

exec "$@"
