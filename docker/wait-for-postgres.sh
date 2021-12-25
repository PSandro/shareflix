#!/usr/bin/env bash
set -e
cmd="$@"
# TODO: make docker parameter for user
until psql -c '\q'; do
  echo >&2 "Postgres is unavailable - sleeping"
  sleep 1
done
echo >&2 "Postgres is up - executing command"
exec $cmd
