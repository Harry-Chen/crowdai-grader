from common_grader import CommonGrader

import io
import numpy as np
import h5py as h5

files = {}


def p2e(p):
    return np.sqrt(p**2 + 0.511**2)


def calc_score_impl(truth_e, ans_e):
    temp = (ans_e - truth_e) / np.sqrt(truth_e)
    return np.sqrt(np.mean(temp**2))


def calc_juno_impl(truth_e, ans_e):
    sim_e = np.round(truth_e - 0.511)
    ans_std = np.zeros_like(ans_e)
    for re in np.unique(sim_e):
        mask = sim_e == re
        ans_std[mask] = np.std(ans_e[mask])
    # std**2 == c**2 + a**2 * e + b**2 * e**2
    fit = np.polyfit(ans_e, ans_std**2, 2)
    return np.sqrt(np.poly1d(fit)(1.6**2) / (1.6**2))


def calc_score(truth, ans):
    n = len(truth)
    if len(ans) != n:
        raise ValueError("Answer table must have {} rows.".format(n))
    if not np.all(truth["EventID"] == ans["EventID"]):
        raise ValueError("Answer table should include all the event IDs.")

    truth_p = truth["p"]
    ans_p = ans["p"]

    truth_e = p2e(truth_p)
    ans_e = p2e(ans_p)

    score = calc_score_impl(truth_e, ans_e)
    gun_mask = truth["Gun"] == 1
    sec_score = calc_juno_impl(truth_e[gun_mask], ans_e[gun_mask])
    return score, sec_score


class PhysicsData2022JUNOGrader(CommonGrader):
    def __init__(self, *kargs):
        super(PhysicsData2022JUNOGrader, self).__init__(*kargs)
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
