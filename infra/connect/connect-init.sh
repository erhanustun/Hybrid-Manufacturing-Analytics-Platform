#!/bin/sh
set -eu

CONNECT_URL="${CONNECT_URL:-http://kafka-connect:8083}"
CONNECTOR_NAME="${CONNECTOR_NAME:-manufacturing-connector}"

# Debezium connector config (NO outer {"name":...} here; used by POST/PUT below)
CONFIG_JSON='{
  "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
  "database.hostname": "postgres",
  "database.port": "5432",
  "database.user": "debezium",
  "database.password": "debezium",
  "database.dbname": "manufacturing",
  "database.server.name": "mfg",
  "topic.prefix": "mfg",
  "table.include.list": "public.machine_events",
  "plugin.name": "pgoutput",
  "publication.name": "dbz_publication",
  "slot.name": "debezium_slot"
}'

log() { printf "%s\n" "$*"; }

# Basic HTTP helper: prints "code body"
http() {
  method="$1"
  url="$2"
  data="${3:-}"

  if [ -n "$data" ]; then
    code="$(curl -sS -o /tmp/resp.txt -w "%{http_code}" -X "$method" "$url" \
      -H "Content-Type: application/json" \
      -d "$data" || true)"
  else
    code="$(curl -sS -o /tmp/resp.txt -w "%{http_code}" -X "$method" "$url" || true)"
  fi

  body="$(cat /tmp/resp.txt 2>/dev/null || true)"
  printf "%s\n" "$code $body"
}

log "Waiting for Kafka Connect at $CONNECT_URL ..."
# Wait until /connectors responds with 200
while :; do
  out="$(http GET "$CONNECT_URL/connectors")"
  code="$(printf "%s" "$out" | awk '{print $1}')"
  if [ "$code" = "200" ]; then
    break
  fi
  log "  ...not ready yet (HTTP $code). Retrying in 2s."
  sleep 2
done

log "Kafka Connect is up."

# Check if connector exists
out="$(http GET "$CONNECT_URL/connectors/$CONNECTOR_NAME")"
code="$(printf "%s" "$out" | awk '{print $1}')"

if [ "$code" = "200" ]; then
  log "Connector exists. Updating config..."
  out2="$(http PUT "$CONNECT_URL/connectors/$CONNECTOR_NAME/config" "$CONFIG_JSON")"
  code2="$(printf "%s" "$out2" | awk '{print $1}')"
  if [ "$code2" != "200" ] && [ "$code2" != "201" ]; then
    log "ERROR: Failed to update connector (HTTP $code2)"
    log "Response: $(printf "%s" "$out2" | cut -d' ' -f2-)"
    exit 1
  fi
else
  log "Connector not found. Creating..."
  payload="{\"name\":\"$CONNECTOR_NAME\",\"config\":$CONFIG_JSON}"
  out2="$(http POST "$CONNECT_URL/connectors" "$payload")"
  code2="$(printf "%s" "$out2" | awk '{print $1}')"
  # 201 Created is typical; 409 if already exists (race), handle gracefully
  if [ "$code2" = "409" ]; then
    log "Connector already exists (409). Will proceed to status check."
  elif [ "$code2" != "200" ] && [ "$code2" != "201" ]; then
    log "ERROR: Failed to create connector (HTTP $code2)"
    log "Response: $(printf "%s" "$out2" | cut -d' ' -f2-)"
    exit 1
  fi
fi

# Wait until connector status is RUNNING
log "Waiting for connector status RUNNING ..."
tries=0
while :; do
  out3="$(http GET "$CONNECT_URL/connectors/$CONNECTOR_NAME/status")"
  code3="$(printf "%s" "$out3" | awk '{print $1}')"
  body3="$(printf "%s" "$out3" | cut -d' ' -f2-)"

  if [ "$code3" = "200" ]; then
    # crude but effective: look for '"state":"RUNNING"' in JSON
    if printf "%s" "$body3" | grep -q '"state"[[:space:]]*:[[:space:]]*"RUNNING"'; then
      break
    fi
  fi

  tries=$((tries + 1))
  if [ "$tries" -ge 60 ]; then
    log "ERROR: Connector did not reach RUNNING state within timeout."
    log "Last status (HTTP $code3): $body3"
    exit 1
  fi

  log "  ...not RUNNING yet (HTTP $code3). Retrying in 2s."
  sleep 2
done

log "Done. Connector is RUNNING."
