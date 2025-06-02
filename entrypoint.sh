#!/usr/bin/env bash
set -e

# --------------------------------------------
# entrypoint.sh
#
# 1) Wait until Postgres is accepting connections
# 2) If no migrations folder exists, run `flask db init`
# 3) Run database migrations (flask db migrate & upgrade)
# 4) Start Flask
# --------------------------------------------

# Ensure DATABASE_URL is set
if [ -z "$DATABASE_URL" ]; then
  echo "ERROR: DATABASE_URL is not set"
  exit 1
fi

# Extract host and port from DATABASE_URL
DB_HOST=$(echo "$DATABASE_URL" | sed -E 's|.*@([^:/]+):([0-9]+).*|\1|')
DB_PORT=$(echo "$DATABASE_URL" | sed -E 's|.*@([^:/]+):([0-9]+).*|\2|')

echo "Waiting for Postgres at $DB_HOST:$DB_PORT…"
TRIES=0
until nc -z "$DB_HOST" "$DB_PORT"; do
  TRIES=$((TRIES+1))
  if [ "$TRIES" -ge 30 ]; then
    echo "ERROR: Could not connect to Postgres at $DB_HOST:$DB_PORT after $TRIES attempts"
    exit 1
  fi
  sleep 1
done

# If migrations folder doesn’t exist, initialize it
if [ ! -d "./migrations" ]; then
  echo "No migrations folder found—initializing Flask-Migrate (flask db init)…"
  flask db init
fi

echo "Applying migrations (flask db migrate + flask db upgrade)…"
# Create a migration script for any unapplied model changes
flask db migrate -m "auto-generated migration"

# Upgrade the database to the latest revision
flask db upgrade

echo "Migrations complete. Starting Flask…"
exec flask run --host=0.0.0.0 --port=5001
