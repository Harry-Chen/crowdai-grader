import random
from graders.common_grader import CommonGrader

import io
import numpy as np
import h5py
import scipy.stats
import pandas as pd

f_ans = h5py.File("../static/ans.h5", "r")
e_ans = f_ans["GroundTruth/PETime"][:]
i_ans = f_ans["GroundTruth/EventID"][:]
c_ans = f_ans["GroundTruth/ChannelID"][:]
df_ans = pd.DataFrame({'PETime': e_ans, 'EventID': i_ans, 'ChannelID': c_ans})
d_ans = df_ans.groupby(['EventID', 'ChannelID']).groups

class WDistanceGrader(CommonGrader):

    def __init__(self, *args):
        super(WDistanceGrader, self).__init__(*args)

    def grade(self):
        if self.submission_content is not None:
            try:
                b = io.BytesIO(self.submission_content)
                f_sub = h5py.File(b)
                e_sub = f_sub["GroundTruth/PETime"][:]
                i_sub = f_sub["GroundTruth/EventID"][:]
                c_sub = f_sub["GroundTruth/ChannelID"][:]
                df_sub = pd.DataFrame({'PETime': e_sub, 'EventID': i_sub, 'ChannelID': c_sub})
                d_sub = df_sub.groupby(['EventID', 'ChannelID']).groups

                dists = []
                for key in d_ans.keys():
                    if not key in d_sub.keys():
                        self.grading_message = 'Submission fail to include {}'.format(key)
                        self.grading_success = False
                        return
                    dist = scipy.stats.wasserstein_distance(d_ans[key], d_sub[key])
                    dists.append(dist)
                self.score = np.mean(dists)
                self.grading_success = True
            except Exception as e:
                import traceback
                traceback.print_exc()
                self.grading_message = 'Bad submission'
                self.grading_success = False
