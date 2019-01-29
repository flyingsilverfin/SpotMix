import numpy as np


class VectorComparator():
    """ Collection of possible methods to score two vectors' similarity. All methods return a float between 0 and 1 """

    @staticmethod
    def l1(v1, v2):
        v1, v2 = np.array(v1), np.array(v2)
        return np.sum(np.abs(v1 - v2))

    @staticmethod
    def l2(v1, v2):
        v1, v2 = np.array(v1), np.array(v2)
        return np.sum((v1-v2)**2)
        
