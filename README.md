Persona5AutoGallows  
===================

Sometimes I'm just that lazy...

A small script to automate the min-max process for the Gallows in Persona 5 by detecting the stats that will level up and repeating the selection process until the desired stats are highlighted. No more endless "What are you waiting for?!" loops

NOTE: This script currently only works in Windows for a Persona 5 game emulated in [rpcs3](https://github.com/RPCS3/rpcs3)

Dependencies
============

* [Pillow](https://github.com/python-pillow/Pillow), [numpy](https://github.com/numpy/numpy) and [opencv-python](https://github.com/skvark/opencv-python) for image processing.

* [pywin32](https://github.com/mhammond/pywin32) for detecting the location, width and height of the game window.

Usage 
=====

1. While you're running Persona 5 in your rpcs3 emulator, go to the gallows and select the Persona to strengthen, while leaving the cursor over the Persona you want to sacrifice.

2. Call the `auto_gallows` function in Python, passing a list containing the stats you wish to level up, for example if you wish to increase strength, magic and endurance:

```
from P5Gallows import auto_gallows


auto_gallows(['st', 'ma', 'en'])
```

3. When the script detects that the stats you want are highlighted, it will stop at the confirmation

