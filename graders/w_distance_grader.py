import random
from graders.common_grader import CommonGrader

import traceback
import io
import numpy as np
import h5py
import scipy.stats
import pandas as pd

# cache hdf5 results
files = {}

class WDistanceGrader(CommonGrader):

    def __init__(self, *args):
        super(WDistanceGrader, self).__init__(*args)
        file_path = self.answer_file_path
        if files.__contains__(file_path):
            self.df_ans = files[file_path].df_ans
            self.d_ans = files[file_path].d_ans
        else:
            f_ans = h5py.File(file_path, "r")
            e_ans = f_ans["GroundTruth"]["PETime"][:]
            i_ans = f_ans["GroundTruth"]["EventID"][:]
            c_ans = f_ans["GroundTruth"]["ChannelID"][:]
            self.df_ans = pd.DataFrame({'PETime': e_ans, 'EventID': i_ans, 'ChannelID': c_ans})
            self.d_ans = self.df_ans.groupby(['EventID', 'ChannelID']).groups
            files[file_path] = {}
            files[file_path]['df_ans'] = self.df_ans
            files[file_path]['d_ans'] = self.d_ans

    def generate_success_message(self):
        if self.score == 0:
            return 'You must be heroxbd!'
        else:
            return 'Successfully graded.'

    def check_column(self, row_name, fields):
        if not row_name in fields:
            self.grading_message = 'Bad submission: column {} not found in Answer table'.format(row_name)
            self.grading_success = False
            return False
        else:
            return True

    def grade(self):
        if self.submission_content is not None:
            self.app.logger.info('Starting to grade {}'.format(self.submission_id))
            try:
                b = io.BytesIO(self.submission_content)
                f_sub = h5py.File(b)
                
                # check for data structure in hdf5 file
                if not "Answer" in f_sub:
                    self.grading_message = 'Bad submission: no Answer table found'
                    self.grading_success = False
                    return
                answer_fields = f_sub['Answer'].dtype.fields;
                if not self.check_column('PETime', answer_fields):
                    return
                if not self.check_column('EventID', answer_fields):
                    return
                if not self.check_column('ChannelID', answer_fields):
                    return
                if not self.check_column('Weight', answer_fields):
                    return
                
                # read submission data
                e_sub = f_sub["Answer"]["PETime"]
                i_sub = f_sub["Answer"]["EventID"]
                c_sub = f_sub["Answer"]["ChannelID"]
                w_sub = f_sub["Answer"]["Weight"]
                
                df_sub = pd.DataFrame({'PETime': e_sub, 'Weight': w_sub, 'EventID': i_sub, 'ChannelID': c_sub})
                d_sub = df_sub.groupby(['EventID', 'ChannelID']).groups

                # do the actual grade
                dists = []
                pois = []
                for key in self.d_ans.keys():
                    if not key in d_sub.keys():
                        (event_id, channel_id) = key
                        self.grading_message = 'Submission fail to include answer for event {} channel {}'.format(event_id, channel_id)
                        self.grading_success = False
                        return
                    dist = scipy.stats.wasserstein_distance(self.df_ans['PETime'][self.d_ans[key]], df_sub['PETime'][d_sub[key]], v_weights=df_sub['Weight'][d_sub[key]])
                    dists.append(dist)
                    Q = len(self.df_ans['PETime'][self.d_ans[key]])
                    q = np.sum(df_sub['Weight'][d_sub[key]])
                    I = (Q + q) / 2
                    poi = np.abs(Q - q) * np.exp(-I) / np.math.factorial(Q) * (I ** Q)
                    pois.append(poi)
                self.score = np.mean(dists)
                self.secondary_score = np.mean(pois)
                self.app.logger.info('Successfully graded {}'.format(self.submission_id))
                self.grading_success = True

            # oooooooops!
            except Exception as e:
                traceback.print_exc()
                self.app.logger.error('Error grading {} with error: \n {}'.format(self.submission_id, repr(e)))
                self.grading_message = 'Error grading your submission: {}'.format(repr(e))
                self.grading_success = False

