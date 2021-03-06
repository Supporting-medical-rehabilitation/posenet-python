""" Program counts bends over to knee"""
import posenet
import cv2

from get_pose import get_pose


def forward_bends_knee(amount, output_stride, cap, sess, model_outputs):

    print("[BENDS] Starting...")
    count = 0
    startEx = False

    while count < amount:
        pose_scores, keypoint_scores, kp_coords = get_pose(
            output_stride, cap, str(count), sess, model_outputs, "count_info")
        for pose in range(len(pose_scores)):
            if pose_scores[pose] == 0.:
                break

            left_dest = posenet.PART_NAMES.index("leftKnee")
            right_dest = posenet.PART_NAMES.index("rightKnee")
            left_wrist = posenet.PART_NAMES.index("leftWrist")
            right_wrist = posenet.PART_NAMES.index("rightWrist")
            left_hip = posenet.PART_NAMES.index("leftHip")
            right_hip = posenet.PART_NAMES.index("rightHip")

            if keypoint_scores[pose, left_hip] > 0.5 and keypoint_scores[pose, right_hip] > 0.5 \
                    and keypoint_scores[pose, left_wrist] > 0.5 and keypoint_scores[pose, right_wrist] > 0.5:

                if abs(kp_coords[pose, left_hip, :][1] - kp_coords[pose, left_wrist, :][1]) < 70 and abs(
                        kp_coords[pose, right_hip, :][1] - kp_coords[pose, right_wrist, :][1]) < 70:
                    print("Start")
                    startEx = True

            if keypoint_scores[pose, left_dest] > 0.4 and keypoint_scores[pose, right_dest] > 0.4 \
                    and keypoint_scores[pose, left_wrist] > 0.4 and keypoint_scores[pose, right_wrist] > 0.4 \
                    and startEx:

                if abs(kp_coords[pose, left_dest, :][0] - kp_coords[pose, left_wrist, :][0]) < 60 and abs(
                        kp_coords[pose, right_dest, :][0] - kp_coords[pose, right_wrist, :][0]) < 60:
                    startEx = False
                    count += 1
                    print("Done")
                elif abs(kp_coords[pose, left_dest, :][0] - kp_coords[pose, left_wrist, :][0]) < 100 and abs(
                        kp_coords[pose, right_dest, :][0] - kp_coords[pose, right_wrist, :][0]) < 100:
                    pose_scores, keypoint_scores, kp_coords = get_pose(
                        output_stride, cap, "Go lower", sess, model_outputs, "warning")

        if cv2.waitKey(1) & 0xFF == ord('q'):
            print(f"Stopped before finishing series. Bends:{count}")
            break

    print(f"Bends:{count}")
