from graders.random_points_grader import RandomPointsGrader

CROWDAI_API_EXTERNAL_GRADER_URL = 'https://crowdai.your-domain.org/api/external_graders'
CROWDAI_API_GRADERS = [
    {
        'name': 'A+B Random Grader',
        'id': 'a+b_grader',
        'api_key': 'your_api_key',
        'class': RandomPointsGrader
    }
]
