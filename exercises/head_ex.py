import posenet
import cv2
from get_pose import get_pose


def check_eyes(keypoint_scores, pose, eye):
    part_eye = posenet.PART_NAMES.index(eye)
    print(keypoint_scores[pose, part_eye])
    return keypoint_scores[pose, part_eye] < 0.4


def head_ex(amount, output_stride, cap, sess, model_outputs):
    count_left = 0
    count_right = 0
    startEx = False
    print("[HEAD] START")
    while count_left < amount or count_right < amount:
        count_title = ""
        if count_right > count_left:
            count_title = "Turning more left, "
        elif count_left > count_right:
            count_title = "Turning more right, "

        count_title += "L: " + str(count_left) + ", R: " + str(count_right)
        pose_scores, keypoint_scores, kp_coords = get_pose(
            output_stride, cap, count_title, sess, model_outputs, False)

        for pose in range(len(pose_scores)):
            if pose_scores[pose] == 0.:
                break
            left_ear = posenet.PART_NAMES.index("leftEar")
            right_ear = posenet.PART_NAMES.index("rightEar")

            if keypoint_scores[pose, left_ear] > 0.5 and keypoint_scores[pose, right_ear] > 0.5:
                print("START")
                startEx = True
            if keypoint_scores[pose, left_ear] < 0.2 < keypoint_scores[pose, right_ear] and startEx:
                print("Turned left")
                count_left += 1
                startEx = False
            if keypoint_scores[pose, right_ear] < 0.2 < keypoint_scores[pose, left_ear] and startEx:
                print("Turned right")
                count_right += 1
                startEx = False

        if cv2.waitKey(1) & 0xFF == ord('q'):
            print(f"Stopped before finishing series. Turn right: {count_right} Turn left: {count_left} ")
            break

    print(f"Turn right: {count_right} Turn left: {count_left} ")
