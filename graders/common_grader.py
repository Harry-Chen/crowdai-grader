from abc import abstractmethod
from flask import Flask
import config
import requests
import boto3

s3 = boto3.resource('s3',
                    aws_access_key_id=config.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY,
                    region_name=config.AWS_REGION)


class CommonGrader(object):

    app: Flask = None
    score: float = None
    score_secondary: float = None
    submission_content: str = None
    grading_message: str = None
    grading_success: bool = False

    def __init__(self, api_key, file_key, submission_id, app):
        self.app = app
        self.app.logger.debug('Initializing new {} with api_key {}, file_key {}, submission_id {}'
                              .format(__name__, api_key, file_key, submission_id))
        self.api_key = api_key
        self.file_key = file_key
        self.submission_id = submission_id

    def fetch_submission(self):
        try:
            self.submission_content = s3.Object(Bucket=config.AWS_S3_BUCKET_NAME, Key=self.file_key).get()['Body']\
                .read().decode('utf-8')
        except Exception as e:
            self.grading_message = 'Error fetching submission'
            self.app.logger.error('Error occurred when fetching submission: {}'.format(str(e)))

    @abstractmethod
    def grade(self):
        pass

    def submit(self):
        url = config.CROWDAI_API_EXTERNAL_GRADER_URL + '/' + self.submission_id

        if self.grading_success:
            self.app.logger.debug('Submitting to {} with score {} and secondary score {}'
                                  .format(url, self.score, self.score_secondary))
            data = {
                'grading_status': 'graded',
                'score': '{:.3f}'.format(self.score),
            }
            if self.score_secondary is not None:
                data['score_secondary'] = '{:.3f}'.format(self.score_secondary)

        else:
            self.app.logger.debug('Submitting to {} with failure message {}'
                                  .format(url, self.grading_message))
            data = {
                'grading_status': 'failed',
                'grading_message': self.grading_message
            }

        response = requests.put(url, data=data, headers={
            'Authorization': 'Token token={}'.format(self.api_key)
        })
        self.app.logger.debug('Submission response: {}'.format(response.text))

