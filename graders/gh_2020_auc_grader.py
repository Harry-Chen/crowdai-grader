from common_grader import CommonGrader

import io
import numpy as np
import h5py

files = {}

def calcAUCScore(df_ans, df_sub):
    #TODO calculate distance
    assert False


class GhostHunter2020AUCGrader(CommonGrader):
    
    def __init__(self, *kargs):
        super(GhostHunter2020AUCGrader, self).__init__(*kargs)
        file_path = self.answer_file_path
        self.df_ans = {}
        if files.__contains__(file_path):
            self.df_ans = files[file_path]
        else:
            with h5py.File(file_path) as f_ans:
                assert False
                #TODO read and cache answer files self.df_ans
            files[file_path] = self.df_ans

    def do_grade(self):
        b = io.BytesIO(self.submission_content)
        df_sub = {}
        with h5py.File(b) as f_sub:
            assert False
            #TODO read to df_sub
            return calcDistanceDic(self.df_ans, df_sub)


if __name__ == "__main__":
    import argparse
    psr = argparse.ArgumentParser()
    psr.add_argument("-r", dest='ref', help="reference")
    psr.add_argument('ipt', help="input to be graded")
    args = psr.parse_args()
    df_ansDic = {}
    df_subDic = {}
    
    with h5py.File(args.ref) as ref, h5py.File(args.ipt) as ipt:
        assert False
        #TODO read to df_sub and df_ans
    print("AUC Score: {}".format(*calcAUCScore(df_ans, df_sub)))
