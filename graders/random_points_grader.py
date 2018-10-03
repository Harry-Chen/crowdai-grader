from graders.common_grader import CommonGrader
import random


class RandomPointsGrader(CommonGrader):

    def __init__(self, *args):
        super(RandomPointsGrader, self).__init__(*args)

    def grade(self):
        self.score = len(self.submission_content)
        self.score_secondary = random.uniform(0.0, 100.0)
