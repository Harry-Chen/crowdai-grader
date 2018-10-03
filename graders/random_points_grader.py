from graders.common_grader import CommonGrader
import random


class RandomPointsGrader(CommonGrader):

    def __init__(self, *args):
        super(RandomPointsGrader, self).__init__(*args)

    def grade(self):
        self.score = random.uniform(0.0, 100.0)
        self.score_secondary = random.uniform(0.0, 100.0)
