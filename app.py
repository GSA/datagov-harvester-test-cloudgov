from flask import Flask, render_template, request
from tasks import validate, test_add, extract, transform, load
from celery import Celery, chain
import os, datetime
import boto3
import ssl

app = Flask(__name__)

host = os.environ.get("REDIS_HOST")
pwd = os.environ.get("REDIS_PASSWORD")
port = os.environ.get("REDIS_PORT")

celery_app = Celery('tasks', broker=f'rediss://:{pwd}@{host}:{port}/0', backend=f'rediss://:{pwd}@{host}:{port}/0',
                        broker_use_ssl={"ssl_cert_reqs": ssl.CERT_NONE},
                        redis_backend_use_ssl={"ssl_cert_reqs": ssl.CERT_NONE})

@app.route('/')
def index():
    return render_template('form.html')


@app.route('/test_s3')
def test_s3():
    id = os.environ.get("AWS_ACCESS_KEY_ID")
    key = os.environ.get("AWS_SECRET_ACCESS_KEY")
    region = os.environ.get("AWS_DEFAULT_REGION")
    S3_BUCKET = os.environ.get("BUCKET_NAME")


    s3 = boto3.client('s3', 
                        aws_access_key_id=id, 
                        aws_secret_access_key=key, 
                        region_name=region
                        )
    
    # FILE_NAME = "test.txt"
    # text_to_upload = 'file with the content...\n'
    # text_to_upload += str(datetime.datetime.now())
    # with open(FILE_NAME, 'w') as f:
    #     f.write(text_to_upload)

    # with open(FILE_NAME, "rb") as f:
    #     s3.put_object(Body=f, Bucket=S3_BUCKET, Key=FILE_NAME) #, ContentMD5=md5)


    s3.put_object(Bucket=S3_BUCKET, Key='mytest.txt', Body='test s3 content here')
    return render_template('result.html', message='saved to S3')


@app.route('/submit', methods=['POST'])
def submit():
    if request.method == 'POST':
        input_data = request.form['input-data']
        print(input_data)
        try:
            print('before calling...')
            validate.delay(input_data).get(timeout=1)
            print('after calling...')
            # result = etl_chain(input_data)
            result = chain(extract.s(input_data), validate.s(), transform.s(), load.s()).apply_async()
        except ValueError as e:
            return render_template('form.html', message=str(e))
        
        id_message = "Task ID:   " + result.id
        return render_template('form.html', message=id_message)



@app.route('/start_task')
def call_method():
    # r = celery_app.send_task('tasks.test_add', kwargs={'x': 1, 'y': 2})
    r = test_add.delay(1, 2)
    return r.id


@app.route('/task_status/<task_id>')
def get_status(task_id):
    status = celery_app.AsyncResult(task_id, app=celery_app)
    return "Status of the Task " + str(status.state)


@app.route('/task_result/<task_id>')
def task_result(task_id):
    result = celery_app.AsyncResult(task_id).result
    return "Result of the Task " + str(result)



if __name__ == '__main__':
    app.run(debug=False)
