from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
RES_FILES_DIR = BASE_DIR / "res"
STYLE_PATH = str(RES_FILES_DIR / "style.qss")

CONFIG_INI_PATH = str(BASE_DIR / "config.ini")

# ICON_PATH = str(RES_FILES_DIR / "be_fv.png")
ICON_PATH = str(RES_FILES_DIR / "logo-BE.png")


DEFAULT_CAMERA = 0
"""
0 is the default camera (normally the webcam)
"""

CAMERA_SOURCE = 1
"""
1 for an external USB camera for example

or '/dev/video1' on Linux

or an IP camera URL (e.g., 'http://192.168.1.100:8080/video')
"""

DEFAULT_FPS = 25
"""
Frames per second
"""
