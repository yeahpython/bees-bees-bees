bees-bees-bees
==============
![screenshot from game](https://raw.githubusercontent.com/yeahpython/bees-bees-bees/master/bees_screenshot_2.png)
####Features:  
* a modular way to specify the structure of neural networks
* a custom physics engine
* a fun stretchy player
* procedural map generation and art
* editable levels (via text file)
* some *very* fun debugging tools

#### Requirements:
* Python
* PyGame
* Numpy

#### Mac OS X Note:
Works way slower on Retina displays. This runs at ~16 frames per second if I put the window on my external monitor but at ~7 frames per second if I put it on my MacBook Retina display. This should be because X11 doesn't like things outside the 72-90 DPI range. You can change the number of bees to adjust frame rate.
