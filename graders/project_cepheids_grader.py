from common_grader import CommonGrader

import io
import numpy as np
import h5py

import itertools as it

# cache hdf5 results
files = {}

def calcAccuracy(df_ans, df_sub):
    N = len(df_ans)
    if not N == len(df_sub):
        raise ValueError("Answer table must have {} rows.".format(N))
    if not np.all(df_ans["ID"] == df_sub["ID"]):
        raise ValueError("Answer table include all the IDs.")

    # 1-cep 2-acep 3-t2cep 4-rrlyr 5-ecl
    df_ansT = df_ans['Type']
    df_subT = df_sub['Type']
    # calculate weight of every type
    typenum = np.array([len(df_ansT[df_ansT == i]) for i in range(1, 6)])
    prescore =  20 / typenum
    # compare value
    compres = df_subT[df_subT == df_ansT]

    return np.sum([len(compres[compres == i]) * prescore[i - 1] for i in range(1, 6)]), None



class CepheidsGrader(CommonGrader):

    def __init__(self, *kargs):
        super(CepheidsGrader, self).__init__(*kargs)
        file_path = self.answer_file_path
        if files.__contains__(file_path):
            self.df_ans = files[file_path]
        else:
            with h5py.File(file_path) as f_ans:
                self.df_ans = f_ans["ans"][()]
            files[file_path] = self.df_ans

    @staticmethod
    def check_column(row_name, fields):
        if row_name not in fields:
            raise ValueError('Bad submission: column {} not found in ans table'.format(row_name))

    def do_grade(self):
        b = io.BytesIO(self.submission_content)
        with h5py.File(b) as f_sub:
            # check for data structure in hdf5 file
            if "ans" not in f_sub:
                raise ValueError('Bad submission: no ans table found')
            answer_fields = f_sub['ans'].dtype.fields
            self.check_column('ID', answer_fields)
            self.check_column('Type', answer_fields)
            return calcAccuracy(self.df_ans, f_sub['ans'][()])


if __name__ == "__main__":
    import argparse
    psr = argparse.ArgumentParser()
    psr.add_argument("-r", dest='ref', help="reference")
    psr.add_argument('ipt', help="input to be graded")
    args = psr.parse_args()

    with h5py.File(args.ref) as ref, h5py.File(args.ipt) as ipt:
        df_ans = ref["ans"][()]
        df_sub = ipt["ans"][()]

    print("Accuracy: {}%".format(calcAccuracy(df_ans, df_sub)))
