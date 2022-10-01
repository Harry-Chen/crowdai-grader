from common_grader import CommonGrader

import io
import numpy as np
import h5py as h5
import scipy.optimize as opt

files = {}


def calc_score_impl(truth_e, ans_e):
    temp = (ans_e - truth_e) / np.sqrt(truth_e)
    return np.sqrt(np.mean(temp**2)) * 1000


def calc_juno_impl(truth_e, ans_e):
    def likelihood(args):
        sigma2 = ans_e * args[0] ** 2 + ans_e**2 * args[1] ** 2 + args[2]
        return -np.sum(np.log(sigma2) / 2 + (ans_e - truth_e) ** 2 / (2 * sigma2))

    args = opt.minimize(likelihood, x0=[0.02, 0.007, 0.01])
    if not args.success:
        raise RuntimeError("Cannot get args")
    args = args.x
    return np.sqrt(args[0] ** 2 + (1.6 * args[1]) ** 2 + (args[2] / 1.6) ** 2)


def calc_score(truth, ans):
    n = len(truth)
    if len(ans) != n:
        raise ValueError("Answer table must have {} rows.".format(n))
    if not np.all(truth["EventID"] == ans["EventID"]):
        raise ValueError("Answer table should include all the event IDs.")

    score = calc_score_impl(truth["Ek"], ans["Ek"])
    sec_score = calc_juno_impl(truth["Evis"], ans["Evis"])
    return score, sec_score


class GhostHunter2022STDGrader(CommonGrader):
    def __init__(self, *kargs):
        super(GhostHunter2022STDGrader, self).__init__(*kargs)
        file_path = self.answer_file_path
        print("BEFORE")
        if files.__contains__(file_path):
            self.df_ans = files[file_path]
        else:
            with h5.File(file_path) as f_ans:
                if "ParticleTruth" in f_ans:
                    self.df_ans = f_ans["ParticleTruth"][()]
                elif "Answer" in f_ans:
                    self.df_ans = f_ans["Answer"][()]
            files[file_path] = self.df_ans
        print(type(self.df_ans))

    @staticmethod
    def check_column(row_name, fields):
        if row_name not in fields:
            raise ValueError(
                "Bad submission: column {} not found in Answer table".format(row_name)
            )

    def do_grade(self):
        b = io.BytesIO(self.submission_content)
        with h5.File(b) as f_sub:
            if "Answer" not in f_sub:
                raise ValueError("Bad submission: no Answer table found")
            answer_fields = f_sub["Answer"].dtype.fields
            self.check_column("EventID", answer_fields)
            self.check_column("p", answer_fields)

            return calc_score(self.df_ans, f_sub["Answer"][()])


if __name__ == "__main__":
    import argparse

    psr = argparse.ArgumentParser()
    psr.add_argument("-r", dest="ref", help="reference")
    psr.add_argument("ipt", help="input to be graded")
    args = psr.parse_args()

    with h5.File(args.ref, "r") as ref, h5.File(args.ipt, "r") as ipt:
        truth = ref["ParticleTruth"][()]
        answer = ipt["Answer"][()]
    score, secondary_score = calc_score(truth, answer)
    print("Score: {}".format(score))
    print("Secondary score: {}".format(secondary_score))
