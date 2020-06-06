import posenet
import numpy as np
import cv2

from get_pose import get_pose



def isLine2(point1, point2, point3):
    x = [point1[0], point2[0]]
    y = [point1[1], point2[1]]
    coefficients = np.polyfit(x, y, 1)
    return abs((point3[0] * coefficients[0] + coefficients[1]) - point3[1]) < 50


def is90(hip, shoulder, wrist):
    a = np.array(hip)
    b = np.array(shoulder)
    c = np.array(wrist)

    ba = a - b
    bc = c - b
    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    angle = np.arccos(cosine_angle)
    print(np.degrees(angle))

    return abs(np.degrees(angle) - 55) < 10


def isNotEnouugh90(hip, shoulder, wrist):
    a = np.array(hip)
    b = np.array(shoulder)
    c = np.array(wrist)

    ba = a - b
    bc = c - b
    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    angle = np.arccos(cosine_angle)
    print(np.degrees(angle))

    return abs(np.degrees(angle) - 35) < 10


def lift_leg(amount, output_stride, cap, sess, model_outputs, which_side="left"):

    count = 0
    startEx = False
    while count < amount:

        pose_scores, keypoint_scores, kp_coords = get_pose(
            output_stride, cap, str(count), sess, model_outputs)
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
                print("TEST")
                # print(kp_coords[pose, left_shoulder, :])
                # print(kp_coords[pose, left_elbow, :])
                # print(kp_coords[pose, left_wrist, :])
                # print(kp_coords[pose, left_hip, :])
                if not startEx and abs(
                        kp_coords[pose, left_knee, :][0] - kp_coords[pose, right_knee, :][0]) < 30:
                    # if not startEx and abs(kp_coords[pose, left_hip, :][0]-kp_coords[pose,left_elbow, :][0]) <30 :
                    print("start")
                    startEx = True
                    # is90(kp_coords[pose, left_hip, :], kp_coords[pose, left_shoulder, :],
                    #      kp_coords[pose, left_wrist, :])
            if startEx:

                # if isLine2([kp_coords[pose, left_shoulder, :][1], kp_coords[pose, left_shoulder, :][0]],
                #            [kp_coords[pose, left_elbow, :][1], kp_coords[pose, left_elbow, :][0]],
                #            [kp_coords[pose, left_wrist, :][1], kp_coords[pose, left_wrist, :][0]]):
                if is90(kp_coords[pose, right_knee, :], kp_coords[pose, right_hip, :],
                        kp_coords[pose, left_knee, :]):
                    print("mamy kąt prosty")
                    count += 1
                # if isNotEnouugh90(kp_coords[pose, right_knee, :], kp_coords[pose, right_hip, :],
                #         kp_coords[pose, left_knee, :]):
                #     cound=True
                #     print("kat niezadowalajacy")


                    # pose_scores, keypoint_scores, kp_coords = get_pose(
                    #     output_stride, cap, str(count), sess, model_outputs)
                    startEx = False
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print(f"Lifting {which_side} leg: ", count)
            break

    print(f"Lifting {which_side} leg: ", count)

