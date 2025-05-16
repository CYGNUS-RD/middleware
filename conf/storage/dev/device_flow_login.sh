#!/bin/bash

# === CONFIGURAZIONE ===
IAM_CLIENT_ID="${IAM_CLIENT_ID}"    # esportalo prima di lanciare
IAM_CLIENT_SECRET="${IAM_CLIENT_SECRET}"  # opzionale
IAM_SCOPE="${IAM_SCOPE}"
IAM_AUTH_URL="https://iam-cygno.cloud.cnaf.infn.it"

DEVICE_ENDPOINT="${IAM_AUTH_URL}/devicecode"
TOKEN_ENDPOINT="${IAM_AUTH_URL}/token"

# === Richiedi il device code ===
echo "==> Richiedo device code da IAM..."

response=$(curl -s -X POST "$DEVICE_ENDPOINT" \
  -d client_id="$IAM_CLIENT_ID" \
  -d scope="$IAM_SCOPE")

echo "Risposta device code:"
echo "$response" | jq

device_code=$(echo "$response" | jq -r .device_code)
user_code=$(echo "$response" | jq -r .user_code)
verification_uri=$(echo "$response" | jq -r .verification_uri)
expires_in=$(echo "$response" | jq -r .expires_in)
interval=$(echo "$response" | jq -r .interval)

if [[ "$device_code" == "null" || -z "$device_code" ]]; then
  echo "❌ Errore: device code non ottenuto. Controlla client ID."
  exit 1
fi

# Se interval è assente, default a 5 secondi
if [[ "$interval" == "null" || -z "$interval" ]]; then
  interval=5
fi

# === Istruzioni per l'utente ===
echo ""
echo "🔗 Per favore, apri il seguente link nel browser e inserisci il codice:"
echo "   URL: $verification_uri"
echo "   CODE: $user_code"
echo ""
echo "Hai $expires_in secondi per completare la procedura..."
echo ""

# === Polling per ottenere access token ===
echo "==> Avvio polling ogni $interval secondi..."

while true; do
  sleep $interval

  if [[ -z "$IAM_CLIENT_SECRET" ]]; then
    # client_secret non presente
    token_response=$(curl -s -X POST "$TOKEN_ENDPOINT" \
      -d grant_type=urn:ietf:params:oauth:grant-type:device_code \
      -d device_code="$device_code" \
      -d audience=object \
      -d client_id="$IAM_CLIENT_ID")
  else
    # client_secret presente
    token_response=$(curl -s -X POST "$TOKEN_ENDPOINT" \
      -d grant_type=urn:ietf:params:oauth:grant-type:device_code \
      -d device_code="$device_code" \
      -d audience=object \
      -d client_id="$IAM_CLIENT_ID" \
      -d client_secret="$IAM_CLIENT_SECRET")
  fi

  error=$(echo "$token_response" | jq -r .error)

  if [[ "$error" == "authorization_pending" ]]; then
    echo "⏳ In attesa di autorizzazione..."
    continue
  elif [[ "$error" == "expired_token" ]]; then
    echo "❌ Device code scaduto. Riprova da capo."
    exit 1
  elif [[ "$error" != "null" ]]; then
    echo "❌ Altro errore: $error"
    echo "$token_response"
    exit 1
  else
    # Token ottenuto!
    echo "✅ Token ottenuto!"
    echo "$token_response" | jq

    ACCESS_TOKEN=$(echo "$token_response" | jq -r .access_token)
    REFRESH_TOKEN=$(echo "$token_response" | jq -r .refresh_token)

    echo "$ACCESS_TOKEN" > access_token.txt
    echo "$REFRESH_TOKEN" > refresh_token.txt

    echo ""
    echo "🔐 Access token salvato in access_token.txt"
    echo "🔁 Refresh token salvato in refresh_token.txt"
    exit 0
  fi
done
