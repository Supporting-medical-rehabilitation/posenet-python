import copy
import numpy as np
import cv2

import posenet
from get_pose import get_pose

def find_initial(output_stride, cap, sess, model_outputs):
    """While person stays still gets its coordinates and return average."""

    glob_count = 0
    while glob_count < 40:
        count = 1
        pose_scores_start, _, kp_coords_start = get_pose(
            output_stride, cap, "Stay still", sess, model_outputs)
        for pose, kp_coord_start in enumerate(kp_coords_start):
            if pose_scores_start[pose] != 0.:
                glob_count += 1
                try:
                    kp_coords_start_av = kp_coords_start_av + kp_coord_start
                except NameError:
                    kp_coords_start_av = copy.deepcopy(kp_coord_start)
                else:
                    count += 1
        if count != 1:
            kp_coords_start_av = np.divide(kp_coords_start_av, count)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    return kp_coords_start_av