# NeuroPy-MindBand

Original code cloned from https://github.com/dweidai/NeuroPy-Python3.0 and then adapted to work with Sichiray Mindband headset. The library itself was written originally by Sahil Singh in Python 2.x (https://pypi.org/project/NeuroPy/) to connect and interact with Neurosky's MindWave EEG headset.

Sichiray's MindBand uses the chipset from the same vendor, so it's almost fully compatible with NeuroSky-specific code.

## Installation:

1. Download the source distribution (zip file) from [dist directory](https://github.com/LazaUK/NeuroPy-MindBand/archive/master.zip) 
2. unzip and navigate to the folder containing _setup.py_ and other files 
3. run the following command: `python setup.py install` 

## Usage:

1. Importing the module: `from NeuroPy import NeuroPy`
2. Initialising: `object1=NeuroPy("COM6",57600)` for Windows, or `object1=NeuroPy("/dev/rfcomm0",57600)` for Linux
3. After initialising , the callbacks must be set using the "start" method, e.g. `object1.start()`
4. Similarly stop method can be called to stop fetching the data, e.g. `object1.stop()` 

### The data from the device can be obtained using either of the following methods or bot of them together:

* Obtaining value: `variable1=object1.attention` _\# to get value of attention_
* Setting callback:a call back can be associated with any variable below, so that a function is called when the variable is updated. Syntax: `setCallBack("variable",callback_function)` E.g., to set a callback for attention data the syntax is `setCallBack("attention",callback_function)` 

Supported variables: attention, meditation, rawValue, delta, theta, lowAlpha, highAlpha, lowBeta, highBeta, lowGamma, midGamma,  poorSignal and blinkStrength

## Examples:

* Sahil's example can be found in sahil_demo.py file
* My example can be found in laziz_demo.py file
