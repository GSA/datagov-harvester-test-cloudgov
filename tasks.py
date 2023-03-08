from celery import Celery, chain
from time import sleep
import boto3
import datetime, os
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

id = os.environ.get("AWS_ACCESS_KEY_ID")
key = os.environ.get("AWS_SECRET_ACCESS_KEY")
region = os.environ.get("AWS_DEFAULT_REGION")
bucket_name = os.environ.get("BUCKET_NAME")

host = os.environ.get("REDIS_HOST")
pwd = os.environ.get("REDIS_PASSWORD")
port = os.environ.get("REDIS_PORT")

s3 = boto3.client('s3', 
                      aws_access_key_id=id, 
                      aws_secret_access_key=key, 
                      region_name=region
                      )

celery = Celery('tasks', broker=f'redis://:{pwd}@{host}:{port}/0', backend=f'redis://:{pwd}@{host}:{port}/0')


@celery.task
def test_add(x, y):
    sleep(10)
    return x + y


@celery.task
def extract(data):
    key = 'input-'+ datetime.datetime.now().strftime('%Y-%m-%d-%H:%M:%S') + '.json'
    s3.put_object(Bucket=bucket_name, Key=key, Body=f'input content here: {data}')
    logger.info('extract, sleeping 10 seconds...')
    sleep(10)
    return data + '(extract) '

@celery.task
def validate(data):
    if data.startswith('data'):
        return data + '(validate) ' 
    else:
        raise ValueError(f'Invalid input data, please start with "data"')

@celery.task
def transform(data):
    logger.info('transform, sleeping 10 seconds...')
    sleep(10)
    return data.upper() + '(TRANSFORM) '

@celery.task
def load(data):
    key = 'output-'+ datetime.datetime.now().strftime('%Y-%m-%d-%H:%M:%S') + '.json'
    result = f"Final data: {data}(LOAD)"
    s3.put_object(Bucket=bucket_name, Key=key, Body=result)
    logger.info('load, sleeping 10 seconds...')
    sleep(10)
    return result


