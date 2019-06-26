# Qwiic_BME280_Py
Python module for the qwiic bme280 sensor, which is part of the [SparkFun Qwiic Environmental Combo Breakout](https://www.sparkfun.com/products/14348)

![SparkFun Qwiic Environmental Combo Breakout](https://cdn.sparkfun.com//assets/parts/1/2/3/2/9/14348-01.jpg)

This python package is a port of the existing [SparkFun BME280 Arduino Library](https://github.com/sparkfun/SparkFun_BME280_Arduino_Library)

## Dependencies 
This driver package depends on the qwii I2C driver: 
[Qwiic_I2C_Py](https://github.com/sparkfun/Qwiic_I2C_Py)

  
## Installation

### PyPi Installation
On systems that support PyPi installation via pip, this library is installed using the following commands

For all users (note: the user must have sudo privileges):
```
  sudo pip install sparkfun_qwiic_bme280
```
For the current user:

```
  pip install sparkfun_qwiic_bme280
```

### Local Installation
To install, make sure the setuptools package is installed on the system.

Direct installation at the command line:
```
  $ python setup.py install
```

To build a package for use with pip:
```
  $ python setup.py sdist
 ```
A package file is built and placed in a subdirectory called dist. This package file can be installed using pip.
```
  cd dist
  pip install sparkfun_qwiic_bme280-<version>.tar.gz
  
```
 ## Example Use
See the examples directory for more detailed use examples.

```python
import qwiic_bme280
import time
import sys

def runExample():

	print("\nSparkFun BME280 Sensor  Example 1\n")
	mySensor = qwiic_bme280.QwiicBme280()

	if mySensor.isConnected() == False:
		print("The Qwiic BME280 device isn't connected to the system. Please check your connection", \
			file=sys.stderr)
		return

	mySensor.begin()

	while True:
		print("Humidity:\t%.3f" % mySensor.humidity)

		print("Pressure:\t%.3f" % mySensor.pressure)	

		print("Altitude:\t%.3f" % mySensor.altitude_feet)

		print("Temperature:\t%.2f" % mySensor.temperature_fahrenheit)		

		print("")
		
		time.sleep(1)
```
