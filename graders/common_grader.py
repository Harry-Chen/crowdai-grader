from abc import abstractmethod

from botocore.config import Config
from flask import Flask
import config
import grader_list
import requests
import boto3

s3 = boto3.resource('s3',
                    config=Config(connect_timeout=5, retries={'max_attempts': 5}, signature_version='s3v4'),
                    aws_access_key_id=config.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY,
                    #region_name=config.AWS_REGION,
                    endpoint_url=config.AWS_ENDPOINT)


class CommonGrader(object):

    app: Flask = None
    score: float = None
    score_secondary: float = None
    submission_content: bytes = None
    grading_message: str = None
    grading_success: bool = False
    answer_file_path: str = None

    def __init__(self, answer_file_path, api_key, file_key, submission_id, app):
        self.app = app
        self.app.logger.info('Initializing new {} with api_key {}, file_key {}, submission_id {}'
                              .format(__name__, api_key, file_key, submission_id))
        self.api_key = api_key
        self.file_key = file_key
        self.submission_id = submission_id
        self.answer_file_path = answer_file_path

    def fetch_submission(self):
        try:
            self.app.logger.info('{}: Fetching file {} from S3'.format(self.submission_id, self.file_key))
            self.submission_content = s3.Object(config.AWS_S3_BUCKET_NAME, self.file_key).get()['Body'].read()
            self.app.logger.info('{}: Read submission content of length {}'.format(self.submission_id, len(self.submission_content)))
            data = {
                'grading_status': 'initiated',
                'grading_message': 'Grading you submission...'
            }
            self.post_grade(data)
        except Exception as e:
            error_message = 'Error occurred when fetching submission: {}'.format(str(e))
            self.app.logger.info('{}: Error occurred when fetching submision: {}'.format(self.submission_id, str(e)))
            self.grading_message = error_message
            self.app.logger.error(error_message)

    @abstractmethod
    def grade(self):
        pass

    @abstractmethod
    def generate_success_message(self):
        return ''


    def submit_grade(self):
        
        if self.grading_success:
            self.app.logger.info('{}: Submitting with score {} and secondary score {}'
                                  .format(self.submission_id, self.score, self.score_secondary))
            data = {
                'grading_status': 'graded',
                'grading_message': self.generate_success_message(),
                'score': '{:.3f}'.format(self.score)
            }
            if self.score_secondary is not None:
                data['score_secondary'] = '{:.3f}'.format(self.score_secondary)

        else:
            self.app.logger.info('{}: Submitting with failure message: {}'
                                  .format(self.submission_id, self.grading_message))
            data = {
                'grading_status': 'failed',
                'grading_message': self.grading_message
            }
        self.post_grade(data)


    def post_grade(self, data):

        url = grader_list.CROWDAI_API_EXTERNAL_GRADER_URL + '/' + self.submission_id

        response = requests.put(url, data=data, headers={
            'Authorization': 'Token token={}'.format(self.api_key)
        })
        self.app.logger.info('Server response: {}'.format(response.text))


