""" Program counts hands up"""
import posenet
import numpy as np
import cv2
from get_pose import get_pose


def isLine2(point1, point2, point3):
    x = [point1[0], point2[0]]
    y = [point1[1], point2[1]]
    coefficients = np.polyfit(x, y, 1)
    return abs((point3[0] * coefficients[0] + coefficients[1]) - point3[1]) < 60


def is90(hip, shoulder, wrist):
    a = np.array(hip)
    b = np.array(shoulder)
    c = np.array(wrist)

    ba = a - b
    bc = c - b
    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    angle = np.arccos(cosine_angle)
    print(np.degrees(angle))
    return abs(np.degrees(angle) - 90) <= 10

def is70(hip, shoulder, wrist):
    a = np.array(hip)
    b = np.array(shoulder)
    c = np.array(wrist)

    ba = a - b
    bc = c - b
    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    angle = np.arccos(cosine_angle)
    # print(np.degrees(angle))
    return np.degrees(angle)  < 80 and np.degrees(angle) > 30




def hands_up(amount, output_stride, cap, sess, model_outputs, which_side="left"):
    count = 0
    startEx = False
    notEnough = False
    count_cond = 0
    while count < amount:
        try:
            pose_scores, keypoint_scores, kp_coords = get_pose(
                output_stride, cap, str(count), sess, model_outputs)
            for pose in range(len(pose_scores)):
                if pose_scores[pose] == 0.:
                    break
                left_shoulder = posenet.PART_NAMES.index(which_side + "Shoulder")
                left_elbow = posenet.PART_NAMES.index(which_side + "Elbow")
                left_wrist = posenet.PART_NAMES.index(which_side + "Wrist")
                left_hip = posenet.PART_NAMES.index(which_side + "Hip")

                if keypoint_scores[pose, left_shoulder] > 0.4 and keypoint_scores[pose, left_elbow] > 0.4 \
                        and keypoint_scores[pose, left_wrist] > 0.4 and keypoint_scores[pose, left_hip] > 0.4:
                    print("TEST")
                    # print(kp_coords[pose, left_shoulder, :])
                    # print(kp_coords[pose, left_elbow, :])
                    # print(kp_coords[pose, left_wrist, :])
                    # print(kp_coords[pose, left_hip, :])
                    if not startEx and abs(
                            kp_coords[pose, left_shoulder, :][1] - kp_coords[pose, left_elbow, :][1]) < 50 and abs(
                        kp_coords[pose, left_elbow, :][1] - kp_coords[pose, left_wrist, :][1]) < 50:
                        # if not startEx and abs(kp_coords[pose, left_hip, :][0]-kp_coords[pose,left_elbow, :][0]) <30 :
                        print("start")
                        startEx = True
                    elif startEx and abs(
                            kp_coords[pose, left_shoulder, :][1] - kp_coords[pose, left_elbow, :][1]) < 50 and abs(
                        kp_coords[pose, left_elbow, :][1] - kp_coords[pose, left_wrist, :][1]) < 50 and notEnough:
                        print("za malo liczymt")
                        startEx = False
                        notEnough=False
                        count_cond+=1
                if startEx:

                    if isLine2([kp_coords[pose, left_shoulder, :][1], kp_coords[pose, left_shoulder, :][0]],
                               [kp_coords[pose, left_elbow, :][1], kp_coords[pose, left_elbow, :][0]],
                               [kp_coords[pose, left_wrist, :][1], kp_coords[pose, left_wrist, :][0]]):
                        print("linia prosta")
                        if is90(kp_coords[pose, left_hip, :], kp_coords[pose, left_shoulder, :],
                                kp_coords[pose, left_wrist, :]):
                            print("mamy kąt prosty")
                            count += 1
                            startEx = False
                            notEnough=False
                        elif is70(kp_coords[pose, left_hip, :], kp_coords[pose, left_shoulder, :],
                                kp_coords[pose, left_wrist, :]):
                            print("za nisko")
                            notEnough = True

                    else:
                        print("niejestprosto")
                        # pose_scores, keypoint_scores, kp_coords = get_pose(
                        #     output_stride, cap, str(count), sess, model_outputs)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("Hands up: ", count)
                break
        except StopIteration:
            break
    print(count_cond)
    print("Hands up: ", count)
