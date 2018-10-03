from graders.random_points_grader import RandomPointsGrader

CROWDAI_API_EXTERNAL_GRADER_URL = 'https://crowdai.your-domain.org/api/external_graders'
CROWDAI_API_GRADERS = [
    {
        'name': 'Random Grader',
        'id': 'random_grader',
        'api_key': 'your_api_key',
        'class': RandomPointsGrader
    }
]

AWS_ACCESS_KEY_ID = 'REDACTED'
AWS_SECRET_ACCESS_KEY = 'REDACTED'
AWS_REGION = 'REDACTED'
AWS_S3_BUCKET_NAME = 'my_bucket'
