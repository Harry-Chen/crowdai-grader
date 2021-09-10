from common_grader import CommonGrader

import io
import numpy as np
import h5py as h5

files = {}


def calc_score(truth, ans):
    n = len(truth)
    if len(ans) != n:
        raise ValueError("Answer table must have {} rows.".format(n))
    if not np.all(truth["SphereId"] == ans["SphereId"]):
        raise ValueError("Answer table should include all the SphereIds.")

    # only use the first ring for score display
    truth_beta = truth["beta"][0]
    ans_beta = ans["beta"][0]
    truth_beta_len = len(truth_beta)
    ans_beta_len = len(ans_beta)
    if truth_beta.dtype != ans_beta.dtype:
        raise TypeError("Answer β must have data type {}".format(truth_beta.dtype))

    # align coefficient order
    if truth_beta_len > ans_beta_len:
        ans_beta = np.zeros_like(truth_beta)
        ans_beta[:ans_beta_len] = ans["beta"][0]
    elif truth_beta_len < ans_beta_len:
        truth_beta = np.zeros_like(ans_beta)
        truth_beta[:truth_beta_len] = truth["beta"][0]

    # calculate L2 distance considering legendre normalization factor
    distance_squre_double = (truth_beta - ans_beta) ** 2 @ (1 / (4 * np.arange(1, len(truth_beta) + 1) + 1))

    return np.sqrt(distance_squre_double * 2)


class GhostHunter2021STDGrader(CommonGrader):

    def __init__(self, *kargs):
        super(GhostHunter2021STDGrader, self).__init__(*kargs)
        file_path = self.answer_file_path
        print("BEFORE")
        if files.__contains__(file_path):
            self.df_ans = files[file_path]
        else:
            with h5.File(file_path) as f_ans:
                if 'Answer' in f_ans:
                    self.df_ans = f_ans['Answer'][()]
            files[file_path] = self.df_ans
        print(type(self.df_ans))

    @staticmethod
    def check_column(row_name, fields):
        if row_name not in fields:
            raise ValueError('Bad submission: column {} not found in Answer table'.format(row_name))

    def do_grade(self):
        b = io.BytesIO(self.submission_content)
        with h5.File(b) as f_sub:
            if "Answer" not in f_sub:
                raise ValueError('Bad submission: no Answer table found')
            answer_fields = f_sub['Answer'].dtype.fields
            self.check_column('ShpereId', answer_fields)
            self.check_column('R', answer_fields)
            self.check_column('beta', answer_fields)

            return calc_score(self.df_ans, f_sub['Answer'][()]), None


if __name__ == "__main__":
    import argparse
    psr = argparse.ArgumentParser()
    psr.add_argument("-r", dest='ref', help="reference")
    psr.add_argument('ipt', help="input to be graded")
    args = psr.parse_args()

    with h5.File(args.ref, "r") as ref, h5.File(args.ipt, "r") as ipt:
        truth = ref["Truth"][()]
        answer = ipt["Answer"][()]
    print("Score: {}".format(calc_score(truth, answer)))
