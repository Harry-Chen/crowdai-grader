from abc import abstractmethod
from flask import Flask
import config
import requests


class CommonGrader(object):

    app: Flask
    score: float = None
    score_secondary: float = None

    def __init__(self, api_key, file_key, submission_id, app, submission_content):
        self.app = app
        self.app.logger.debug('Initializing new {} with api_key {}, file_key {}, submission_id {}, submission_content {}'
                              .format(__name__, api_key, file_key, submission_id, submission_content))
        self.api_key = api_key
        self.file_key = file_key
        self.submission_id = submission_id
        self.submission_content = submission_content

        # TODO get file from S3

    @abstractmethod
    def grade(self):
        pass

    def submit(self):
        url = config.CROWDAI_API_EXTERNAL_GRADER_URL + '/' + self.submission_id
        self.app.logger.debug('Submitting to {} with score {} and secondary score {}'
                              .format(url, self.score, self.score_secondary))
        response = requests.put(url, data={
            'grading_status': 'graded',
            'score': '{:.3f}'.format(self.score),
            'score_secondary': '{:.3f}'.format(self.score_secondary),
        }, headers={
            'Authorization': 'Token token={}'.format(self.api_key)
        })
        self.app.logger.debug('Submission response: {}'.format(response.text))

