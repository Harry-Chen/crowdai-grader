import random
from graders.common_grader import CommonGrader


class RandomPointsGrader(CommonGrader):

    def __init__(self, *args):
        super(RandomPointsGrader, self).__init__(*args)

    def grade(self):
        if self.submission_content is not None:
            length = len(self.submission_content)
            if length <= 1000:
                self.score = length
                self.score_secondary = random.uniform(0.0, 100.0)
                self.grading_success = True
            else:
                self.grading_message = 'Submission with {} bytes is too long!'.format(length)
        else:
            self.grading_message = 'Empty submission'
