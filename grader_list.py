from graders.random_points_grader import RandomPointsGrader
from graders.text_length_grader import TextLengthGrader
from graders.w_distance_grader import WDistanceGrader

CROWDAI_API_EXTERNAL_GRADER_URL = 'https://data-contest.net9.org/api/external_graders'
CROWDAI_API_GRADERS = [
    {
        'name': 'W Distance Grader',
        'id': 'w_distance_grader',
        'api_key': 'testtest',
        'class': WDistanceGrader
    }
]


