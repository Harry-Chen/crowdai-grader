import h5py as h5
import numpy as np

def calc_score(truth, ans):
    n = len(truth)
    if len(ans) != n:
        raise ValueError("Answer table must have {} rows.".format(n))
    if not np.all(truth["EventID"] == ans["EventID"]):
        raise ValueError("Answer table should include all the event IDs.")
    
    truth_vis = truth["vis"]
    ans_vis = ans["vis"]

    return np.std((ans_vis - truth_vis) / np.sqrt(truth_vis))

if __name__ == "__main__":
    import argparse
    psr = argparse.ArgumentParser()
    psr.add_argument("-r", dest='ref', help="reference")
    psr.add_argument('ipt', help="input to be graded")
    args = psr.parse_args()

    with h5.File(args.ref, "r") as ref, h5.File(args.ipt, "r") as ipt:
        truth = ref["ParticleTruth"][()]
        answer = ipt["Answer"][()]
    print("Score: {}".format(calc_score(truth, answer)))
