from common_grader import CommonGrader

import io
import numpy as np
import h5py
from sklearn.metrics import roc_auc_score

files = {}

def calcAUCScore(df_ans, df_sub):
    N = len(df_ans)
    if not N == len(df_sub):
        raise ValueError("Answer table must have {} rows.".format(N))
    if not np.all(df_ans["EventID"] == df_sub["EventID"]):
        raise ValueError("Answer table include all the EventIDs.")

    return roc_auc_score(df_ans["Alpha"], df_sub["Alpha"]), None

class GhostHunter2020AUCGrader(CommonGrader):
    
    def __init__(self, *kargs):
        super(GhostHunter2020AUCGrader, self).__init__(*kargs)
        file_path = self.answer_file_path
        if files.__contains__(file_path):
            self.df_ans = files[file_path]
        else:
            with h5py.File(file_path) as f_ans:
                self.df_ans = f_ans['ParticleTruth'][()]
            files[file_path] = self.df_ans
        print(type(self.df_ans))

    @staticmethod
    def check_column(row_name, fields):
        if row_name not in fields:
            raise ValueError('Bad submission: column {} not found in Answer table'.format(row_name))

    def do_grade(self):
        b = io.BytesIO(self.submission_content)
        with h5py.File(b) as f_sub:
            if "Answer" not in f_sub:
                raise ValueError('Bad submission: no Answer table found')
            answer_fields = f_sub['Answer'].dtype.fields
            self.check_column('EventID', answer_fields)
            self.check_column('Alpha', answer_fields)

            return calcAUCScore(self.df_ans, f_sub['Answer'][()])

if __name__ == "__main__":
    import argparse
    psr = argparse.ArgumentParser()
    psr.add_argument("-r", dest='ref', help="reference")
    psr.add_argument('ipt', help="input to be graded")
    args = psr.parse_args()
    
    with h5py.File(args.ref) as ref, h5py.File(args.ipt) as ipt:
        df_ans = ref["ParticleTruth"][()]
        df_sub = ipt["Answer"][()]
    print("AUC Score: {}".format(calcAUCScore(df_ans, df_sub)))
