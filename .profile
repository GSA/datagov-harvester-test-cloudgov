#!/bin/bash

set -o errexit
set -o pipefail

APP_NAME='etl-test'

function vcap_get_service () {
  local path name
  name="$1"
  path="$2"
  service_name=${APP_NAME}-${name}
  echo $VCAP_SERVICES | jq --raw-output --arg service_name "$service_name" ".[][] | select(.name == \$service_name) | $path"
}

export REDIS_HOST=$(vcap_get_service redis .credentials.host)
export REDIS_PASSWORD=$(vcap_get_service redis .credentials.password)
export REDIS_PORT=$(vcap_get_service redis .credentials.port)

export AWS_ACCESS_KEY_ID=$(vcap_get_service s3 .credentials.access_key_id)
export AWS_SECRET_ACCESS_KEY=$(vcap_get_service s3 .credentials.secret_access_key)
export AWS_DEFAULT_REGION=$(vcap_get_service s3 .credentials.region)
export BUCKET_NAME=$(vcap_get_service s3 .credentials.bucket)
