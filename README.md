# datagov-harvester-test-cloudgov

### local test
1. fill in the value in .env file for the S3 credentials
2. docker compose up
3. test process at localhost:5000 

### deploy to cloud.gov (development)

```
cf create-service aws-elasticache-redis redis-dev "etl-test-redis" --wait
cf create-service s3 basic-public "etl-test-s3"
cf push --var app_name='etl-test'
```

```
https://etl-test.app.cloud.gov/
check the status: https://etl-test.app.cloud.gov/task_status/<task_id>
check the reult:  https://etl-test.app.cloud.gov/task_result/<task_id>
```