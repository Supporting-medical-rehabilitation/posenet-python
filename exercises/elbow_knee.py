"""Counts bending knees to elbows"""
import cv2

import posenet
from get_pose import get_pose
from exercises.get_init_pose import find_initial


def count_bends(amount, output_stride, cap, sess, model_outputs, side):
    """ Checks elbow position - if it becomes higher and
        knee's position - if it becomes higer and more left or right, depending on which side
    """

    count = 0
    flag = False
    bending = 1
    kp_coords_start_av = find_initial(output_stride, cap, sess, model_outputs)
    knee_compare = [
        (kp_coords_start_av[-4, 0] - kp_coords_start_av[-5, 0])*0.5,
        (kp_coords_start_av[-4, 1] - kp_coords_start_av[-5, 1])*0.3]
    elbow_compare = [
        (kp_coords_start_av[-1, 0] - kp_coords_start_av[0, 0])*0.02,
        (kp_coords_start_av[-8, 1] - kp_coords_start_av[-7, 1])*0.04]
    if side == "left":
        elbow_in = posenet.PART_NAMES.index("rightElbow")
        knee_in = posenet.PART_NAMES.index("leftKnee")
    elif side == "right":
        elbow_in = posenet.PART_NAMES.index("leftElbow")
        knee_in = posenet.PART_NAMES.index("rightKnee")

    while count < amount:
        if bending == 0:
            label = str(count)
            bending = 1
        elif bending == 1:
            label = "Bend"
        elif bending == -1:
            label = "Back"

        pose_scores, keypoint_scores, kp_coords = get_pose(
            output_stride, cap, label, sess, model_outputs)
        for pose in range(len(pose_scores)):
            if pose_scores[pose] == 0.:
                break
            knee_diff = kp_coords_start_av[knee_in, :] - kp_coords[pose, knee_in, :]
            elbow_diff = kp_coords_start_av[elbow_in, :] - kp_coords[pose, elbow_in, :]
            if side == "right":
                knee_diff[1] *= -1       
            if knee_diff[0] > knee_compare[0] and knee_diff[1] > knee_compare[1] and elbow_diff[0] > elbow_compare[0] and not flag:
                flag = True
                bending = -1
            elif knee_diff[0] < knee_compare[0] and knee_diff[1] < knee_compare[1] and elbow_diff[0] < elbow_compare[0] and flag:
                flag = False
                count += 1
            if bending == -1 and knee_diff[0] < knee_compare[0]*0.1 and knee_diff[1] < knee_compare[1]*0.1:
                bending = 0

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
