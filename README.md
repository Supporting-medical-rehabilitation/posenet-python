## Medical Rehabilitation support 

This repository contains an desktop application for supporting medical rehabilitation using
implementation of PoseNet in Python.


### Install and run

A suitable Python 3.x environment is requried. 
```
pip install -r requirements.txt
python main_window.py
```
### Usage 
The user can choose one exercise from the list of available exercises, enter the number of repetitions and start performing the exercise. The application monitors the user's pose by the webcam and counts the number of repetitions performed, it also instructs the user with simple commands to do the exercise correctly.
It counts the number of examples that have not been correctly completed, but does not count them in the final results.
The appication allows adding new exercises in a simple way. Implementation of all exercises are contained in *exercises* folder.
  

### Credits

The implementation of poseNet in Python used in this project was created by rwightman at https://github.com/rwightman/posenet-python.
In this project it was used to prepare desktop application for supporting medical rehabilitation.



