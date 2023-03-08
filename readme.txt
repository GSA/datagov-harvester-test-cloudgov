# create two services
cf t -o sandbox-gsa

cf create-service aws-elasticache-redis redis-dev "etl-test-redis" --wait
cf create-service s3 basic-sandbox "etl-test-s3"

cf create-service aws-elasticache-redis redis-3node "etl-test-redis" --wait
cf create-service s3 basic-public-sandbox "etl-test-s3"


# push to cloud.gov
cf push --var app_name='etl-test'