import posenet
import numpy as np
import cv2

from exercises.hands_up import calculate_angle
from get_pose import get_pose


def is_straight_angle_leg(hip, shoulder, wrist):
    angle = calculate_angle(hip, shoulder, wrist)
    return abs(np.degrees(angle) - 55) <= 10


def is_too_lower(hip, shoulder, wrist):
    angle = calculate_angle(hip, shoulder, wrist)
    return 45 > np.degrees(angle) > 35


def lift_leg(amount, output_stride, cap, sess, model_outputs, which_side="left"):
    count = 0
    count_cond = 0
    startEx = False
    toLower = False
    print("[LEGS] Starting...")

    while count < amount:
        text_info = str(count)
        if count_cond > 0:
            text_info += ",incorrect: " + str(count_cond)

        pose_scores, keypoint_scores, kp_coords = get_pose(
            output_stride, cap, text_info, sess, model_outputs, "count_info")

        for pose in range(len(pose_scores)):

            if pose_scores[pose] == 0.:
                break

            if which_side == "left":
                left_knee = posenet.PART_NAMES.index("leftKnee")
                right_knee = posenet.PART_NAMES.index("rightKnee")
                right_hip = posenet.PART_NAMES.index("rightHip")
            else:
                left_knee = posenet.PART_NAMES.index("rightKnee")
                right_knee = posenet.PART_NAMES.index("leftKnee")
                right_hip = posenet.PART_NAMES.index("leftHip")

            if keypoint_scores[pose, left_knee] > 0.5 and keypoint_scores[pose, right_knee] > 0.5 \
                    and keypoint_scores[pose, right_hip] > 0.5:
                if abs(kp_coords[pose, left_knee, :][0] - kp_coords[pose, right_knee, :][0]) < 30 and not startEx:
                    print("Start")
                    startEx = True
                elif startEx and abs(kp_coords[pose, left_knee, :][0] - kp_coords[pose, right_knee, :][0]) < 30 \
                        and toLower:
                    print("Incorrect")
                    startEx = False
                    toLower = False
                    count_cond += 1

            if startEx:
                if is_straight_angle_leg(kp_coords[pose, right_knee, :], kp_coords[pose, right_hip, :],
                                         kp_coords[pose, left_knee, :]):
                    print("Done")
                    count += 1
                    toLower = False
                    startEx = False

                elif is_too_lower(kp_coords[pose, right_knee, :], kp_coords[pose, right_hip, :],
                                  kp_coords[pose, left_knee, :]):
                    toLower = True

        if cv2.waitKey(1) & 0xFF == ord('q'):
            print(
                f"Stopped before finishing series. Correct {which_side} leg lifting: {count}, incorrect: {count_cond}.")
            break
    print(count_cond)
    print(f"Lifting Correct {which_side} leg lifting: {count}, incorrect: {count_cond}.")
