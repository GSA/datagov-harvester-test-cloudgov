from flask import Flask, render_template, request
from tasks import validate, test_add, extract, transform, load
from celery import Celery, chain
import os
import boto3

app = Flask(__name__)

host = os.environ.get("REDIS_HOST")
pwd = os.environ.get("REDIS_PASSWORD")
port = os.environ.get("REDIS_PORT")

celery_app = Celery('tasks', broker=f'redis://:{pwd}@{host}:{port}/0', backend=f'redis://:{pwd}@{host}:{port}/0')

@app.route('/')
def index():
    return render_template('form.html')


@app.route('/test_s3')
def test_s3():
    id = os.environ.get("AWS_ACCESS_KEY_ID")
    key = os.environ.get("AWS_SECRET_ACCESS_KEY")
    region = os.environ.get("AWS_DEFAULT_REGION")
    bucket_name = os.environ.get("BUCKET_NAME")

    s3 = boto3.client('s3', 
                        aws_access_key_id=id, 
                        aws_secret_access_key=key, 
                        region_name=region
                        )

    s3.put_object(Bucket=bucket_name, Key='mytest.txt', Body='test s3 content here')
    return render_template('result.html', message='saved to S3')


@app.route('/submit', methods=['POST'])
def submit():
    if request.method == 'POST':
        input_data = request.form['input-data']
        try:
            validate.delay(input_data).get(timeout=1)
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
