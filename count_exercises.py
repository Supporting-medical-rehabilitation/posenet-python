"""Programme counts different exercises"""
import time
import argparse
from enum import Enum

import tensorflow as tf
import cv2

import posenet
from exercises.forward_bends_knee import forward_bends_knee
from exercises.squats import count_squats
from exercises.hands_up import hands_up
from exercises.head_ex import head_ex
from exercises.lift_leg import lift_leg
from exercises.elbow_knee import count_bends
from get_pose import get_pose


class ExercisesType(Enum):
    HEAD = 1
    HANDS_LEFT = 2
    HANDS_RIGHT = 3
    BENDS = 4
    LIFT_LEG_LEFT = 5
    LIFT_LEG_RIGHT = 6
    SQUAT = 7
    BEND_LEFT_KNEE = 8
    BEND_RIGHT_KNEE = 9


PARSER = argparse.ArgumentParser()
PARSER.add_argument('--model', type=int, default=101)
PARSER.add_argument('--cam_id', type=int, default=0)
PARSER.add_argument('--cam_width', type=int, default=1280)
PARSER.add_argument('--cam_height', type=int, default=720)
PARSER.add_argument('--scale_factor', type=float, default=0.7125)
PARSER.add_argument(
    '--file', type=str, default=None, help="Optionally use a video file instead of a live camera")
ARGS = PARSER.parse_args()


def count_exercises(amount, exercise):
    """ Wait 3 sec for person to stand in a right position, find initial position,
        count exercises.
    """

    time.sleep(3)
    with tf.Session() as sess:
        model_cfg, model_outputs = posenet.load_model(ARGS.model, sess)
        output_stride = model_cfg['output_stride']
        if ARGS.file is not None:
            cap = cv2.VideoCapture(ARGS.file)
        else:
            cap = cv2.VideoCapture(ARGS.cam_id)
        cap.set(3, ARGS.cam_width)
        cap.set(4, ARGS.cam_height)

        amount = int(amount)
        if exercise == ExercisesType.SQUAT:
            count_squats(amount, output_stride, cap, sess, model_outputs)
        elif exercise == ExercisesType.BENDS:
            forward_bends_knee(amount, output_stride, cap, sess, model_outputs)
        elif exercise == ExercisesType.HANDS_LEFT:
            hands_up(amount, output_stride, cap, sess, model_outputs, "left")
        elif exercise == ExercisesType.HANDS_RIGHT:
            hands_up(amount, output_stride, cap, sess, model_outputs, "right")
        elif exercise == ExercisesType.HEAD:
            head_ex(amount, output_stride, cap, sess, model_outputs)
        elif exercise == ExercisesType.LIFT_LEG_LEFT:
            lift_leg(amount, output_stride, cap, sess, model_outputs, "left")
        elif exercise == ExercisesType.LIFT_LEG_RIGHT:
            lift_leg(amount, output_stride, cap, sess, model_outputs, "right")
        elif exercise == ExercisesType.BEND_LEFT_KNEE:
            count_bends(amount, output_stride, cap, sess, model_outputs, "left")
        elif exercise == ExercisesType.BEND_RIGHT_KNEE:
            count_bends(amount, output_stride, cap, sess, model_outputs, "right")

        get_pose(output_stride, cap, "GREAT!", sess, model_outputs)