import random
from graders.common_grader import CommonGrader

import traceback
import io
import numpy as np
import h5py
import scipy.stats
import pandas as pd

f_ans = h5py.File("static/ans.h5", "r")
e_ans = f_ans["GroundTruth"]["PETime"][:]
i_ans = f_ans["GroundTruth"]["EventID"][:]
c_ans = f_ans["GroundTruth"]["ChannelID"][:]
df_ans = pd.DataFrame({'PETime': e_ans, 'EventID': i_ans, 'ChannelID': c_ans})
d_ans = df_ans.groupby(['EventID', 'ChannelID']).groups

class WDistanceGrader(CommonGrader):

    def __init__(self, *args):
        super(WDistanceGrader, self).__init__(*args)

    def generate_success_message(self):
        if self.score == 0:
            return 'Well done!'
        else:
            return 'Try harder!'

    def grade(self):
        if self.submission_content is not None:
            self.app.logger.info('Starting to grade {}'.format(self.submission_id))
            try:
                b = io.BytesIO(self.submission_content)
                f_sub = h5py.File(b)
                if not "Answer" in f_sub:
                    self.grading_message = 'Bad submission: no Answer found'
                    self.grading_success = False
                    return
                if not "PETime" in f_sub["Answer"].dtype.fields:
                    self.grading_message = 'Bad submission: no PETime found in Answer table'
                    self.grading_success = False
                    return
                if not "EventID" in f_sub["Answer"].dtype.fields:
                    self.grading_message = 'Bad submission: no EventID found in Answer table'
                    self.grading_success = False
                    return
                if not "ChannelID" in f_sub["Answer"].dtype.fields:
                    self.grading_message = 'Bad submission: no ChannelID found in Answer table'
                    self.grading_success = False
                    return
                e_sub = f_sub["Answer"]["PETime"]
                i_sub = f_sub["Answer"]["EventID"]
                c_sub = f_sub["Answer"]["ChannelID"]
                w_sub = f_sub["Answer"]["Weight"]
                df_sub = pd.DataFrame({'PETime': e_sub, 'Weight': w_sub, 'EventID': i_sub, 'ChannelID': c_sub})
                d_sub = df_sub.groupby(['EventID', 'ChannelID']).groups

                dists = []
                for key in d_ans.keys():
                    if not key in d_sub.keys():
                        (event_id, channel_id) = key
                        self.grading_message = 'Submission fail to include answer for event {} channel {}'.format(event_id, channel_id)
                        self.grading_success = False
                        return
                    dist = scipy.stats.wasserstein_distance(d_ans[key], d_sub[key]['PETime'], v_weights=d_sub[key]['Weight'])
                    dists.append(dist)
                self.score = np.mean(dists)
                self.app.logger.info('Successfully graded {}'.format(self.submission_id))
                self.grading_success = True
            except Exception as e:
                traceback.print_exc()
                self.app.logger.error('Error grading {} with error: \n {}'.format(self.submission_id, repr(e)))
                self.grading_message = 'Bad submission'
                self.grading_success = False

