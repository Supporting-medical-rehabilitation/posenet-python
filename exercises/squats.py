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


def count_squats(amount, output_stride, cap, sess, model_outputs, count):
    """Gets pose's coordinates, checks if difference in knees height is big enough,
    if yes - adds squat.
    """
    down = False
    going_down = 1
    kp_coords_start_av = find_initial(output_stride, cap, sess, model_outputs)
    compare_val = abs(kp_coords_start_av[0, 0] - kp_coords_start_av[-1, 0]) * 0.04
    while count < amount:
        if going_down == 0:
            label = str(count)
            going_down = 1
        elif going_down == 1:
            label = "Down"
        elif going_down == -1:
            label = "Up"

        pose_scores, keypoint_scores, kp_coords = get_pose(
            output_stride, cap, label, sess, model_outputs)
        for pose in range(len(pose_scores)):
            if pose_scores[pose] == 0.:
                break
            # for ki, (s, c) in enumerate(zip(keypoint_scores[pose, :], kp_coords[pose, :, :])):
            #     print('Keypoint %s, score = %f, coord = %s' % (posenet.PART_NAMES[ki], s, c))
            l_knee_in = posenet.PART_NAMES.index("leftKnee")
            r_knee_in = posenet.PART_NAMES.index("rightKnee")
            if keypoint_scores[pose, l_knee_in] > 0.7:
                diff = kp_coords[pose, l_knee_in, :] - kp_coords_start_av[l_knee_in, :]
            elif keypoint_scores[pose, r_knee_in] > 0.7:
                diff = kp_coords[pose, r_knee_in, :] - kp_coords_start_av[r_knee_in, :]
            else:
                break

            if diff[0] > compare_val and not down:
                down = True
                going_down = -1
            elif diff[0] < compare_val and diff[0] > 0 and down:
                down = False
                count += 1

            if going_down == -1 and diff[0] < compare_val*0.1:
                going_down = 0

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
