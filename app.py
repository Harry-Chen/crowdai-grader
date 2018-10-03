import urllib

from flask import Flask, request, make_response
from config import *
from graders.common_grader import CommonGrader
import _thread
import boto3

app = Flask(__name__)


s3 = boto3.resource('s3',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION)


@app.route('/enqueue_grading_job', methods=['POST'])
def enqueue_grading_job() -> str:

    r = request.form
    app.logger.info('Getting request' + str(request.form))
    submission_id = urllib.parse.unquote(r['data[][submission_id]'])
    grader_id = urllib.parse.unquote(r['grader_id'])
    file_key = urllib.parse.unquote(r['data[][file_key]'])
    submission_content = s3.Object('net9.org', file_key).get()['Body'].read()

    grader_result = list(filter(lambda g: g['id'] == grader_id, CROWDAI_API_GRADERS))

    if len(grader_result) == 0:
        app.logger.warning('No grader found, will return error')
        return make_response('No grader found', 400)
    else:
        g = grader_result[0]
        grader = g['class'](g['api_key'], file_key, submission_id, app, submission_content)
        _thread.start_new_thread(do_grade, (grader,))
        return make_response('Task successfully submitted', 200)


def do_grade(grader: CommonGrader):
    grader.grade()
    grader.submit()


if __name__ == '__main__':
    app.run()
