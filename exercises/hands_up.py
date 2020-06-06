""" Program counts hands up"""
import posenet
import numpy as np
import cv2
from get_pose import get_pose


def is_straight_line(point1, point2, point3):
    x = [point1[0], point2[0]]
    y = [point1[1], point2[1]]
    coefficients = np.polyfit(x, y, 1)
    return abs((point3[0] * coefficients[0] + coefficients[1]) - point3[1]) < 60


def calculate_angle(hip, shoulder, wrist):
    a = np.array(hip)
    b = np.array(shoulder)
    c = np.array(wrist)

    ba = a - b
    bc = c - b
    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    return np.arccos(cosine_angle)


def is_straight_angle(hip, shoulder, wrist):
    angle = calculate_angle(hip, shoulder, wrist)
    return abs(np.degrees(angle) - 90) <= 10


def is_too_lower(hip, shoulder, wrist):
    angle = calculate_angle(hip, shoulder, wrist)
    return 80 > np.degrees(angle) > 30


def hands_up(amount, output_stride, cap, sess, model_outputs, which_side="left"):
    count = 0
    startEx = False
    tooLow = False
    count_cond = 0
    print("[HANDS] Starting...")
    while count < amount:
        text_info = str(count)
        style = ""
        if count_cond > 0:
            style = "count_info"
            text_info += ",incorrect: " + str(count_cond)

        pose_scores, keypoint_scores, kp_coords = get_pose(
            output_stride, cap, text_info, sess, model_outputs, style)
        for pose in range(len(pose_scores)):

            if pose_scores[pose] == 0.:
                break

            left_shoulder = posenet.PART_NAMES.index(which_side + "Shoulder")
            left_elbow = posenet.PART_NAMES.index(which_side + "Elbow")
            left_wrist = posenet.PART_NAMES.index(which_side + "Wrist")
            left_hip = posenet.PART_NAMES.index(which_side + "Hip")

            if keypoint_scores[pose, left_shoulder] > 0.4 and keypoint_scores[pose, left_elbow] > 0.4 \
                    and keypoint_scores[pose, left_wrist] > 0.4 and keypoint_scores[pose, left_hip] > 0.4:

                if not startEx and abs(kp_coords[pose, left_shoulder, :][1] - kp_coords[pose, left_elbow, :][1]) < 50 \
                        and abs(kp_coords[pose, left_elbow, :][1] - kp_coords[pose, left_wrist, :][1]) < 50:
                    print("Start")
                    startEx = True
                elif startEx and abs(kp_coords[pose, left_shoulder, :][1] - kp_coords[pose, left_elbow, :][1]) < 50 \
                        and abs(kp_coords[pose, left_elbow, :][1] - kp_coords[pose, left_wrist, :][1]) < 50 and tooLow:
                    print("Incorrect")
                    startEx = False
                    tooLow = False
                    count_cond += 1

            if startEx:

                if is_straight_line([kp_coords[pose, left_shoulder, :][1], kp_coords[pose, left_shoulder, :][0]],
                                    [kp_coords[pose, left_elbow, :][1], kp_coords[pose, left_elbow, :][0]],
                                    [kp_coords[pose, left_wrist, :][1], kp_coords[pose, left_wrist, :][0]]):

                    if is_straight_angle(kp_coords[pose, left_hip, :], kp_coords[pose, left_shoulder, :],
                                         kp_coords[pose, left_wrist, :]):
                        print("Done")
                        count += 1
                        startEx = False
                        tooLow = False
                    elif is_too_lower(kp_coords[pose, left_hip, :], kp_coords[pose, left_shoulder, :],
                                      kp_coords[pose, left_wrist, :]):
                        tooLow = True

                else:
                    pose_scores, keypoint_scores, kp_coords = get_pose(
                        output_stride, cap, "Straighten your arm", sess, model_outputs, "warning")

        if cv2.waitKey(1) & 0xFF == ord('q'):
            print(f"Stopped before finishing series. Correct hands up: {count}, incorrect: {count_cond}.")
            break

    print(f"Correct hands up: {count}, incorrect: {count_cond}.")
