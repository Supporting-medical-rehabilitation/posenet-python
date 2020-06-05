import time
import argparse
from enum import Enum

import tensorflow as tf
import cv2

import posenet

PARSER = argparse.ArgumentParser()
PARSER.add_argument('--model', type=int, default=101)
PARSER.add_argument('--cam_id', type=int, default=0)
PARSER.add_argument('--cam_width', type=int, default=1280)
PARSER.add_argument('--cam_height', type=int, default=720)
PARSER.add_argument('--scale_factor', type=float, default=0.7125)
PARSER.add_argument(
    '--file', type=str, default=None, help="Optionally use a video file instead of a live camera")
ARGS = PARSER.parse_args()

def get_pose(output_stride, cap, legend, sess, model_outputs):
    """Gets pose's coordinates, draws lines ans prints text."""

    input_image, display_image, output_scale = posenet.read_cap(
        cap, scale_factor=ARGS.scale_factor, output_stride=output_stride)

    heatmaps_result, offsets_result, displacement_fwd_result, displacement_bwd_result = sess.run(
        model_outputs,
        feed_dict={'image:0': input_image}
    )

    pose_scores, keypoint_scores, keypoint_coords = posenet.decode_multi.decode_multiple_poses(
        heatmaps_result.squeeze(axis=0),
        offsets_result.squeeze(axis=0),
        displacement_fwd_result.squeeze(axis=0),
        displacement_bwd_result.squeeze(axis=0),
        output_stride=output_stride,
        max_pose_detections=10,
        min_pose_score=0.15)

    keypoint_coords *= output_scale

    overlay_image = posenet.draw_skel_and_kp(
        display_image, pose_scores, keypoint_scores, keypoint_coords,
        min_pose_score=0.15, min_part_score=0.1)
    if legend:
        cv2.putText(
            overlay_image, legend, (300, 300), cv2.FONT_HERSHEY_SIMPLEX, 6, (0, 0, 255), 20)
    cv2.imshow('posenet', overlay_image)
    return (pose_scores, keypoint_scores, keypoint_coords)