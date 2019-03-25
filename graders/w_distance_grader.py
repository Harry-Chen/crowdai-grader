from graders.common_grader import CommonGrader

import traceback
import io
import numpy as np
import h5py
import pandas as pd
import scipy.stats
from time import time
from setproctitle import setproctitle, getproctitle

import sys
import os
import tempfile
import json

# cache hdf5 results
files = {}


def wpdistance(ansg, subg):
    '''
    do the actual grade

    return the mean Wasserstain and Poisson distances.
    '''
    dists = pois = 0

    gl = ansg.ngroups
    assert subg.ngroups >= gl, 'Number of answers in the submission is less than {}.'.format(gl)

    si = iter(subg)
    for a in ansg:
        try:
            while True:
                s = next(si)
                if s[0] == a[0]:
                    break
        except StopIteration:
            raise KeyError(a[0]) from None
        wl = s[1]['Weight'].values
        dists += scipy.stats.wasserstein_distance(a[1]['PETime'].values, 
                s[1]['PETime'].values, v_weights=wl)
        Q = len(a[1]); q = np.sum(wl)
        pois += np.abs(Q - q) * scipy.stats.poisson.pmf(Q, Q)
    return dists/gl, pois/gl

class WDistanceGrader(CommonGrader):

    def __init__(self, *args):
        super(WDistanceGrader, self).__init__(*args)
        file_path = self.answer_file_path
        if files.__contains__(file_path):
            self.ansg = files[file_path]
        else:
            df_ans = pd.read_hdf(file_path, "GroundTruth")
            self.ansg = df_ans.groupby(['EventID', 'ChannelID'], as_index=True)

            files[file_path] = self.ansg

    def generate_success_message(self):
        seconds = self.stop_time - self.start_time
        return 'Successfully graded your submission in {:.3f} seconds.'.format(seconds)

    def check_column(self, row_name, fields):
        if row_name not in fields:
            raise ValueError('Bad submission: column {} not found in Answer table'.format(row_name))

    def grade(self):
        
        if self.submission_content == None:
            return

        r, w = os.pipe()
        child_pid = os.fork()

        if child_pid != 0:
            # parent process
            setproctitle('crowdAI grader')
            os.close(w)
            msg_pipe = os.fdopen(r)
            self.start_time = time()
            message = json.loads(msg_pipe.read())
            self.app.logger.info('Got message from child: {}'.format(message))
            self.stop_time = time()
            
            self.grading_success = message['grading_success']
            if not self.grading_success:
                self.grading_message = message['grading_message']
            else:
                self.score = float(message['score'])
                self.score_secondary = float(message['score_secondary'])
            
            os.waitpid(child_pid, 0) # wait for child to finish
            msg_pipe.close()
            self.app.logger.info('Child process for submission {} exits'.format(self.submission_id))
        else:
            # child process
            os.close(r)
            msg_pipe = os.fdopen(w, 'w')
            self.app.logger.info('Forked child starting to grade submission {}'.format(self.submission_id))
            setproctitle('crowdAI grader for submission {}'.format(self.submission_id))
            try:
                b = io.BytesIO(self.submission_content)
                f_sub = h5py.File(b)
                # check for data structure in hdf5 file
                if "Answer" not in f_sub:
                    raise ValueError('Bad submission: no Answer table found')
                answer_fields = f_sub['Answer'].dtype.fields
                self.check_column('PETime', answer_fields)
                self.check_column('EventID', answer_fields)
                self.check_column('ChannelID', answer_fields)
                self.check_column('Weight', answer_fields)

                
                df_sub = pd.DataFrame.from_records(f_sub['Answer'][()])
                subg = df_sub.groupby(['EventID', 'ChannelID'], as_index=True)

                (self.score, self.score_secondary) = wpdistance(self.ansg, subg)

                self.app.logger.info('Successfully graded {}'.format(self.submission_id))
                self.grading_success = True

            # oooooooops!
            except KeyError as e:
                self.grading_message = 'Submission fail to include answer for event {} channel {}'.format(*e.args[0])
                self.grading_success = False
            except (AssertionError, ValueError) as e:
                self.grading_message = e
                self.grading_success = False
            except Exception as e:
                traceback.print_exc()
                self.app.logger.error('Error grading {}: \n {}'.format(self.submission_id, repr(e)))
                self.grading_message = 'Error grading your submission: {}'.format(str(e))
                self.grading_success = False

            finally:
                # write result to parent process, then exit
                self.app.logger.info('Forked child done grading submission {}'.format(self.submission_id))
                msg_pipe.write(json.dumps({'grading_success': self.grading_success, 'grading_message': str(self.grading_message), 'score': str(self.score), 'score_secondary': str(self.score_secondary)}))
                msg_pipe.close()
                sys.exit()

if __name__=="__main__":
    import argparse
    psr = argparse.ArgumentParser()
    psr.add_argument("-r", dest='ref', help="reference")
    psr.add_argument('ipt', help="input to be graded")
    args = psr.parse_args()

    df_ans = pd.read_hdf(args.ref, "GroundTruth")
    df_sub = pd.read_hdf(args.ipt, "Answer")

    ansg = df_ans.groupby(['EventID', 'ChannelID'], as_index=True)
    subg = df_sub.groupby(['EventID', 'ChannelID'], as_index=True)

    print("W Dist: {}, P Dist: {}".format(*wpdistance(ansg, subg)))
