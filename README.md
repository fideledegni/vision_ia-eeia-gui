# vision_ia-eeia-gui
A simple GUI for EEIA VISION/IA project

## Install requirements
`pip install -r requirements.txt`. In a virtuel env if possible!

## Run
- Update [`config.py`](config.py). You may need to change the value of `CAMERA_SOURCE`
- In [`main.py`](main.py), `detect_all`, `detect_zems` and `count_zems` methods should be updated. For now, `detect_all` and `detect_zems` add a fixed text on the video; `count_zems` returns a random number between `0` and `10`.
- **Run: `python main.py`**
