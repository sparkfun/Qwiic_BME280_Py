#!/usr/bin/env python
#-----------------------------------------------------------------------------
# qwiic_env_bme280_ex4.py
#
# Simple Example for the Qwiic BME280 Device
#------------------------------------------------------------------------
#
# Written by  SparkFun Electronics, May 2019
# 
# This python library supports the SparkFun Electroncis qwiic 
# qwiic sensor/board ecosystem on a Raspberry Pi (and compatable) single
# board computers. 
#
# More information on qwiic is at https:# www.sparkfun.com/qwiic
#
# Do you like this library? Help support SparkFun. Buy a board!
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http:# www.gnu.org/licenses/>.
#-----------------------------------------------------------------------------
# Example 4 - port of the Arduino example 4
#

from __future__ import print_function
import qwiic_bme280
import time
import sys

def runExample():

	print("\nSparkFun BME280 Sensor  Example 4\n")
	mySensor = qwiic_bme280.QwiicBme280()

	if mySensor.isConnected() == False:
		print("The Qwiic BME280 device isn't connected to the system. Please check your connection", \
			file=sys.stderr)
		return

	mySensor.begin()

	mySensor.setFilter(1); # 0 to 4 is valid. Filter coefficient. See 3.4.4
	mySensor.setStandbyTime(0); # 0 to 7 valid. Time between readings. See table 27.
	
	mySensor.setTempOverSample(1); # 0 to 16 are valid. 0 disables temp sensing. See table 24.
	mySensor.setPressureOverSample(1); # 0 to 16 are valid. 0 disables pressure sensing. See table 23.
	mySensor.setHumidityOverSample(1); # 0 to 16 are valid. 0 disables humidity sensing. See table 19.
	mySensor.setMode(mySensor.MODE_NORMAL); # MODE_SLEEP, MODE_FORCED, MODE_NORMAL is valid. See 3.3

	while True:
		print("Humidity:\t%.3f" % mySensor.readFloatHumidity())

		print("Pressure:\t%.3f" % mySensor.readFloatPressure())		

		print("Altitude:\t%.3f" % mySensor.readFloatAltitudeFeet())

		print("Temperature:\t%.2f" % mySensor.readTempF())		

		time.sleep(.4)


if __name__ == '__main__':
	try:
		runExample()
	except (KeyboardInterrupt, SystemExit) as exErr:
		print("\nEnding Example 4")
		sys.exit(0)


