# local test
1. fill in the value in .env file for the S3 credentials
2. > docker compose up
3. test process at localhost:5000 

# deployment to cloud.gov

cf t -o sandbox-gsa

cf create-service aws-elasticache-redis redis-dev "etl-test-redis" --wait
cf create-service s3 basic-public "etl-test-s3"

# push to cloud.gov
cf push --var app_name='etl-test'