from common_grader import CommonGrader

import io
import numpy as np
import h5py as h5

files = {}


def calc_score_impl(truth_p, ans_p):
    truth_e = np.sqrt(truth_p**2 + 0.511**2)
    ans_e = np.sqrt(ans_p**2 + 0.511**2)

    temp = (ans_e - truth_e) / np.sqrt(truth_e)
    return np.sqrt(np.mean(temp**2))


def calc_score(truth, ans):
    n = len(truth)
    if len(ans) != n:
        raise ValueError("Answer table must have {} rows.".format(n))
    if not np.all(truth["EventID"] == ans["EventID"]):
        raise ValueError("Answer table should include all the event IDs.")

    truth_p = truth["p"]
    ans_p = ans["p"]

    score = calc_score_impl(truth_p, ans_p)
    gun_mask = truth["Gun"] == 1
    sec_score = calc_score_impl(truth_p[gun_mask], ans_p[gun_mask])
    return score, sec_score


class GhostHunter2022JUNOGrader(CommonGrader):
    def __init__(self, *kargs):
        super(GhostHunter2022JUNOGrader, self).__init__(*kargs)
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
    print("Secondary score: {}".format(score))
