import urllib

from flask import Flask, request, jsonify
from config import *
from grader_list import *
import _thread

import logging
from logging.handlers import RotatingFileHandler
import sys

app = Flask(__name__)
handler = logging.StreamHandler(sys.stderr)
handler.setLevel(logging.INFO)
app.logger.addHandler(handler)
handler = RotatingFileHandler(LOG_FILE, maxBytes=LOG_BYTES_PER_FILE, backupCount=10)
handler.setLevel(logging.INFO)
app.logger.addHandler(handler)
app.logger.setLevel(logging.INFO)

@app.route('/enqueue_grading_job', methods=['POST'])
def enqueue_grading_job() -> str:

    r = request.form
    app.logger.info('Getting request' + str(request.form))
    submission_id = urllib.parse.unquote(r['data[][submission_id]'])
    grader_id = urllib.parse.unquote(r['grader_id'])
    file_key = urllib.parse.unquote(r['data[][file_key]'])

    grader_result = list(filter(lambda g: g['id'] == grader_id, CROWDAI_API_GRADERS))

    if len(grader_result) == 0:
        app.logger.warning('No grader found, will return error')
        return jsonify({'message': 'No grader found'}), 400
    else:
        g = grader_result[0]
        grader = g['class'](g['api_key'], file_key, submission_id, app)
        _thread.start_new_thread(do_grade, (grader,))
        return jsonify({'message': 'Task successfully submitted'}), 200


def do_grade(grader):
    grader.fetch_submission()
    grader.grade()
    grader.submit_grade()


if __name__ == '__main__':
    app.run(port=10000)

