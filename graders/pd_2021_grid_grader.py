from common_grader import CommonGrader

import io
import numpy as np
import h5py

import itertools as it

# cache hdf5 results
files = {}

def angleScore(df_ans, df_sub):
    ans_shape = df_ans.shape
    if not ans_shape == df_sub.shape:
        raise ValueError("Answer table must have shape {}.".format(ans_shape))

    vecproduct = np.sin(-df_sub[:, 1]+np.pi/2)*np.cos(df_sub[:, 0]) * \
                        np.sin(-df_ans[:, 1]+np.pi/2)*np.cos(df_ans[:, 0]) + \
                    np.sin(-df_sub[:, 1]+np.pi/2)*np.sin(df_sub[:, 0]) * \
                        np.sin(-df_ans[:, 1]+np.pi/2)*np.sin(df_ans[:, 0]) + \
                    np.cos(-df_sub[:, 1]+np.pi/2) * \
                        np.cos(-df_ans[:, 1]+np.pi/2)
    vecproduct[vecproduct > 1] = 1
    vecproduct[vecproduct < -1] = -1
    # vecproduct is (1000, ) , so result is [0, 1000]
    return np.sum(np.arccos(vecproduct)) / np.pi


class GRIDGrader(CommonGrader):

    def __init__(self, *kargs):
        super(GRIDGrader, self).__init__(*kargs)
        file_path = self.answer_file_path
        if files.__contains__(file_path):
            self.df_ans = files[file_path]
        else:
            with h5py.File(file_path) as f_ans:
                self.df_ans = f_ans["source"][()]
            files[file_path] = self.df_ans

    @staticmethod
    def check_column(row_name, fields):
        if row_name not in fields:
            raise ValueError('Bad submission: column {} not found in ans table'.format(row_name))

    def do_grade(self):
        b = io.BytesIO(self.submission_content)
        with h5py.File(b) as f_sub:
            # check for data structure in hdf5 file
            if "source" not in f_sub:
                raise ValueError('Bad submission: no source table found')
            answer_fields = f_sub['source'].dtype.fields
            return angleScore(self.df_ans, f_sub['source'][()]), None


if __name__ == "__main__":
    import argparse
    psr = argparse.ArgumentParser()
    psr.add_argument("-r", dest='ref', help="reference")
    psr.add_argument('ipt', help="input to be graded")
    args = psr.parse_args()

    with h5py.File(args.ref) as ref, h5py.File(args.ipt) as ipt:
        df_ans = ref["source"][()]
        df_sub = ipt["source"][()]

    print("Score: {}".format(angleScore(df_ans, df_sub)))

