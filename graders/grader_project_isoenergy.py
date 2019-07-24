from graders.common_grader import CommonGrader
# from common_grader import CommonGrader

import traceback
import io
import numpy as np
import h5py
import scipy
from time import time
from setproctitle import setproctitle,getproctitle

import sys, os, itertools as it
import json

files = {}

def calcDistanceDic(df_ans, df_sub):
    # df_ans is dictionary of the group of '/'
    # wDist = 0
    # L2Dist = 0

    length = len(df_ans.keys())
    assert len(df_sub.keys())==length, 'The number of answer is wrong'
    
    L1DistStore = np.zeros(length)
    L2DistStore = np.zeros(length)
    
    for i,s in enumerate(df_ans.keys()):
        e_ans = s][:]
        assert (s in df_sub.keys()), 'Answer must include INDEX {}'.format(s)
        e_sub = df_sub[
        assert (e_sub.shape == (201,201)), 'INDEX {} shape must be (201,201)'.format(s)
        L1DistStore[i] = np.sum(np.abs(e_ans-e_sub)) # scipy.stats.wasserstein_distance()
        L2DistStore[i] = np.linalg.norm(e_ans-e_sub)
    
    return np.mean(L2DistStore), np.mean(L1DistStore)


class IsoenergyGrader(CommonGrader):
    
    def __init__(self, *args):
        super(IsoenergyGrader, self).__init__(*args)
        file_path = self.answer_file_path
        self.df_ans = {}
        if files.__contains__(file_path):
            self.df_ans = files[file_path]
        else:
            with h5py.File(file_path) as f_ans:
                for s in f_ans.keys():
                    self.df_ans[s] = f_ans[s]['isoE'][:]
            files[file_path] = self.df_ans


    def generate_success_message(self):
        seconds = self.stop_time - self.start_time
        return 'Successfully graded your submission in {:.3f} seconds.'.format(seconds)


    def grade(self):
        if self.submission_content == None:
            return
        r, w = os.pipe()
        child_pid = os.fork()

        if child_pid != 0:
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
            os.waitpid(child_pid, 0)
            msg_pipe.close()
            self.app.logger.info('Child process for submission {} exits'.format(self.submission_id))
        else:
            os.close(r)
            msg_pipe = os.fdopen(w, 'w')
            self.app.logger.info('Forked child starting to grade submission {}'.format(self.submission_id))
            setproctitle('crowdAI grader for submission {} (isoenergy)'.format(self.submission.id))
            try:
                b = io.BytesIO(self.submission_content)
                df_sub = {}
                with h5py.File(b) as f_sub:
                    for s in f_sub.keys():
                        df_sub[s] = f_sub[s]['isoE'][:]
                
                (self.score,self.score_secondary) = calcDistanceDic(self.df_ans, df_sub)
                self.app.logger.info('Successfully graded {}'.format(self.submission_id))
                self.grading_success = True
            
            except AssertionError as e:
                self.grading_message = str(e)
                self.grading_success = False
            except Exception as e:
                traceback.print_exc()
                self.app.logger.error('Error grading {}:\n {}'.format(self.submission_id, repr(e)))
                self.grading_message = 'Error grading your submission: {}'.format(str(e))
                self.grading_success = False
            finally:
                self.app.logger.info('Forked child done grading submission {}'.format(self.submission_id))
                msg_pipe.write(json.dumps({'grading_success': self.grading_success, 'grading_message': str(self.grading_message), 'score': str(self.score), 'score_secondary': str(self.score_secondary)}))
                msg_pipe.close()
                sys.exit()


if __name__=="__main__":
    import argparse
    psr = argparse.ArgumentParser()
    psr.add_argument("-r", dest='ref', help="reference")
    psr.add_argument('ipt', help="input to be graded")
    args =psr.parse_args()
    df_ansDic={}
    df_subDic={}
    
    with h5py.File(args.ref) as ref, h5py.File(args.ipt) as ipt:
        df_ans = ref['/']
        df_sub = ipt['/']
    
        for s in df_ans.keys():
            df_ansDic[s] = df_ans[s]['isoE'][:]
        for s in df_sub.keys():
            df_subDic[s] = df_sub[s]['isoE'][:]
    
    print("L2 Dist: {};L1 Dist: {}".format(*calcDistanceDic(df_ansDic, df_subDic)))

