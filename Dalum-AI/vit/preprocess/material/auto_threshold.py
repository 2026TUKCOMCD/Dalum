import numpy as np


class AutoThresholdTuner:
    def __init__(self):
        self.conf_list = []

    def collect(self, top3):
        top1_prob = top3[0][1]
        self.conf_list.append(top1_prob)

    def get_threshold(self):
        if len(self.conf_list) == 0:
            return 0.25

        mean = np.mean(self.conf_list)
        std = np.std(self.conf_list)

        # 보수적으로 설정
        return max(0.18, mean - 0.5 * std)
