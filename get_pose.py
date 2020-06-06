import cv2

import posenet


def set_style(style):
    font_scale = 6
    org = (300, 300)
    thickness = 15
    color = (0, 0, 255)
    if style == "count_info":
        font_scale = 2
        org = (50, 100)
        thickness = 4
    elif style == "warning":
        org = (200, 200)
        thickness = 10
        font_scale = 2
        color = (139, 0, 0)

    return font_scale, org, thickness, color


def get_pose(output_stride, cap, legend, sess, model_outputs, style=""):
    """Gets pose's coordinates, draws lines and prints text."""

    input_image, display_image, output_scale = posenet.read_cap(
        cap, scale_factor=0.7125, output_stride=output_stride)

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
        font_scale, org, thickness, color = set_style(style)
        cv2.putText(
            overlay_image, legend, org, cv2.FONT_HERSHEY_SIMPLEX, font_scale, color, thickness)
    cv2.imshow('posenet', overlay_image)
    return pose_scores, keypoint_scores, keypoint_coords
