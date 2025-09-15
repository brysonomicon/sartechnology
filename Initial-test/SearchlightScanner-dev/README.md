# README for SAR Searchlight Scanner

## Overview

This software package is organized into several directories, including `backend`, `frontend`, `constants`, and `sounds`, each containing relevant modules for handling various device functionalities such as GPS tracking, object detection through image processing, camera management, image storage, constant management, and a graphical user interface for real-time interaction. The system is designed to integrate these functions seamlessly, providing efficient real-time tracking, image processing, and data handling capabilities.


## Modules Description

### GPSManager

Handles GPS device interactions, ensuring that coordinates are updated only when valid and providing methods for starting and stopping the GPS tracking thread. The manager supports multiple serial ports and provides GPS coordinate updates, altitude, speed calculations, and bearing directions.

### ImageProcessor

Utilizes deep learning models (SSD-Mobilenet-v1) for object detection within images. The processor can handle full images or divide them into grids for localized detection. Detected objects are returned with their labels and confidence levels.

### ImageSaver

Manages the storage of images based on detection relevance and GPS coordinates. Images are prioritized and saved to a designated directory, maintaining organization and ease of access. The system ensures images are annotated and their metadata is correctly formatted before storage.

### CameraManager

Manages camera inputs, allowing changes in camera sources and resolutions. The class is optimized for use with `videoSource` from `jetson_utils`, but can be adapted for use with other camera management libraries.

### SoundManager 

Plays specified sounds based on the detection labels received from the ImageProcessor. It uses a default sound for all detections aside from powerlines, which has its own specific sound.

### ConstantsManager

This class manages constants that are used across the application. It provides methods for loading constants from a JSON file and writing updates back to the file. If the specified JSON file does not exist, it creates a new one with a default structure.

### Application (GUI)

A tkinter-based graphical user interface (GUI) application that integrates the functionalities of the `GPSManager`, `CameraManager`, and an image processing setup. The application features multiple frames for different settings and functionalities, allowing the user to interact with the system through a graphical interface.

### CameraFeed

This class manages video capture from a designated camera source using OpenCV. It provides functionalities to change the video source and capture frames which can be processed by other components of the application.

## Notes

The model can be downloaded at https://drive.google.com/drive/folders/1cSUit-qn6RUP69SZKrJayjlbVZrnEtsf?usp=sharing 

Project deployment notes can be viewed at https://docs.google.com/document/d/1rzz0O65910Saukt-Ppdr1zIEvkJdUONx/edit

Release notes can be viewed at https://docs.google.com/document/d/1J6jRMFk4gDtfDnW0x19CBua5L9uNC4Ai/edit 

## Installation

Ensure you have the following dependencies installed:

- Python 3.x
- PIL
- numpy
- threading
- queue
- piexif
- jetson-inference
- jetson-utils

Installation of dependencies can be done via pip:

```bash
pip install Pillow numpy piexif jetson-inference
