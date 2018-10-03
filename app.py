from flask import Flask, request

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/enqueue_grading_job', methods=['POST'])
def enqueue_grading_job() -> str:
    app.logger.info('Getting request' + request.form)
    return "Queued"


if __name__ == '__main__':
    app.run()
