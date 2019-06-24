#-----------------------------------------------------------------------------
# exampledevice.py
#
# Simple Example device for qwiic
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

	
import math
import qwiic_i2c

# Define the device name and I2C addresses. These are set in the class defintion 
# as class variables, making them avilable without having to create a class instance.
#
# The base class and associated support functions use these class varables to 
# allow users to easily identify connected devices as well as provide basic 
# device services.
#
# The name of this device - note this is private 
_DEFAULT_NAME = "Qwiic BME280"

# Some devices have multiple availabel addresses - this is a list of these addresses.
# NOTE: The first address in this list is considered the default I2C address for the 
# device.
_AVAILABLE_I2C_ADDRESS = [0x77, 0x76]

# Default Setting Values
_settings = { "runMode" : 3, 		\
				"tStandby" 	: 0, 		\
				"filter" 	: 0, 		\
				"tempOverSample"  : 1, 	\
				"pressOverSample" : 1, 	\
				"humidOverSample" : 1, 	\
				"tempCorrection"  : 0.0  }

# define our valid chip IDs
_validChipIDs = [0x58, 0x60]




# define the class that encapsulates the device being created. All information associated with this
# device is encapsulated by this class. The device class should be the only value exported 
# from this module.

class QwiicBme280(object):

	# Constructor
	device_name = _DEFAULT_NAME
	available_addresses = _AVAILABLE_I2C_ADDRESS

	# mode flags for the device - user exposed
	MODE_SLEEP = 0b00
	MODE_FORCED = 0b01
	MODE_NORMAL = 0b11

	# Register names for the BME280
	BME280_DIG_T1_LSB_REG =			0x88
	BME280_DIG_T1_MSB_REG =			0x89
	BME280_DIG_T2_LSB_REG =			0x8A
	BME280_DIG_T2_MSB_REG =			0x8B
	BME280_DIG_T3_LSB_REG =			0x8C
	BME280_DIG_T3_MSB_REG =			0x8D
	BME280_DIG_P1_LSB_REG =			0x8E
	BME280_DIG_P1_MSB_REG =			0x8F
	BME280_DIG_P2_LSB_REG =			0x90
	BME280_DIG_P2_MSB_REG =			0x91
	BME280_DIG_P3_LSB_REG =			0x92
	BME280_DIG_P3_MSB_REG =			0x93
	BME280_DIG_P4_LSB_REG =			0x94
	BME280_DIG_P4_MSB_REG =			0x95
	BME280_DIG_P5_LSB_REG =			0x96
	BME280_DIG_P5_MSB_REG =			0x97
	BME280_DIG_P6_LSB_REG =			0x98
	BME280_DIG_P6_MSB_REG =			0x99
	BME280_DIG_P7_LSB_REG =			0x9A
	BME280_DIG_P7_MSB_REG =			0x9B
	BME280_DIG_P8_LSB_REG =			0x9C
	BME280_DIG_P8_MSB_REG =			0x9D
	BME280_DIG_P9_LSB_REG =			0x9E
	BME280_DIG_P9_MSB_REG =			0x9F
	BME280_DIG_H1_REG =				0xA1
	BME280_CHIP_ID_REG =			0xD0 # Chip ID
	BME280_RST_REG =				0xE0 # Softreset Reg
	BME280_DIG_H2_LSB_REG =			0xE1
	BME280_DIG_H2_MSB_REG =			0xE2
	BME280_DIG_H3_REG =				0xE3
	BME280_DIG_H4_MSB_REG =			0xE4
	BME280_DIG_H4_LSB_REG =			0xE5
	BME280_DIG_H5_MSB_REG =			0xE6
	BME280_DIG_H6_REG =				0xE7
	BME280_CTRL_HUMIDITY_REG =		0xF2 # Ctrl Humidity Reg
	BME280_STAT_REG =				0xF3 # Status Reg
	BME280_CTRL_MEAS_REG =			0xF4 # Ctrl Measure Reg
	BME280_CONFIG_REG =				0xF5 # Configuration Reg
	BME280_PRESSURE_MSB_REG =		0xF7 # Pressure MSB
	BME280_PRESSURE_LSB_REG =		0xF8 # Pressure LSB
	BME280_PRESSURE_XLSB_REG =		0xF9 # Pressure XLSB
	BME280_TEMPERATURE_MSB_REG =	0xFA # Temperature MSB
	BME280_TEMPERATURE_LSB_REG =	0xFB # Temperature LSB
	BME280_TEMPERATURE_XLSB_REG =	0xFC # Temperature XLSB
	BME280_HUMIDITY_MSB_REG =		0xFD # Humidity MSB
	BME280_HUMIDITY_LSB_REG =		0xFE # Humidity LSB

	def __init__(self, address=None):


		self.address = address if address != None else self.available_addresses[0]

		# load the I2C driver

		self._i2c = qwiic_i2c.getI2CDriver()
		if self._i2c == None:
			print("Unable to load I2C driver for this platform.")
			return

		# create a dictionary to stash our calibration data for the sensor
		self.calibration={}

		self.t_fine=0

		self._referencePressure = 101325.0

	def isConnected(self):
		return qwiic_i2c.isDeviceConnected(self.address)

	def begin(self):

		# are we who we need to be?
		chipID = self._i2c.readByte(self.address, self.BME280_CHIP_ID_REG)
		if not chipID in _validChipIDs:
			print("Invalid Chip ID: 0x%.2X" % chipID)
			return chipID;

		# Reading all compensation data, range 0x88:A1, 0xE1:E7
		self.calibration["dig_T1"] = (self._i2c.readByte(self.address, self.BME280_DIG_T1_MSB_REG) << 8) + self._i2c.readByte(self.address, self.BME280_DIG_T1_LSB_REG)
		self.calibration["dig_T2"] = (self._i2c.readByte(self.address, self.BME280_DIG_T2_MSB_REG) << 8) + self._i2c.readByte(self.address, self.BME280_DIG_T2_LSB_REG)
		self.calibration["dig_T3"] = (self._i2c.readByte(self.address, self.BME280_DIG_T3_MSB_REG) << 8) + self._i2c.readByte(self.address, self.BME280_DIG_T3_LSB_REG)

		self.calibration["dig_P1"] = (self._i2c.readByte(self.address, self.BME280_DIG_P1_MSB_REG) << 8) + self._i2c.readByte(self.address, self.BME280_DIG_P1_LSB_REG)
		self.calibration["dig_P2"] = (self._i2c.readByte(self.address, self.BME280_DIG_P2_MSB_REG) << 8) + self._i2c.readByte(self.address, self.BME280_DIG_P2_LSB_REG)
		self.calibration["dig_P3"] = (self._i2c.readByte(self.address, self.BME280_DIG_P3_MSB_REG) << 8) + self._i2c.readByte(self.address, self.BME280_DIG_P3_LSB_REG)
		self.calibration["dig_P4"] = (self._i2c.readByte(self.address, self.BME280_DIG_P4_MSB_REG) << 8) + self._i2c.readByte(self.address, self.BME280_DIG_P4_LSB_REG)
		self.calibration["dig_P5"] = (self._i2c.readByte(self.address, self.BME280_DIG_P5_MSB_REG) << 8) + self._i2c.readByte(self.address, self.BME280_DIG_P5_LSB_REG)
		self.calibration["dig_P6"] = (self._i2c.readByte(self.address, self.BME280_DIG_P6_MSB_REG) << 8) + self._i2c.readByte(self.address, self.BME280_DIG_P6_LSB_REG)
		self.calibration["dig_P7"] = (self._i2c.readByte(self.address, self.BME280_DIG_P7_MSB_REG) << 8) + self._i2c.readByte(self.address, self.BME280_DIG_P7_LSB_REG)
		self.calibration["dig_P8"] = (self._i2c.readByte(self.address, self.BME280_DIG_P8_MSB_REG) << 8) + self._i2c.readByte(self.address, self.BME280_DIG_P8_LSB_REG)
		self.calibration["dig_P9"] = (self._i2c.readByte(self.address, self.BME280_DIG_P9_MSB_REG) << 8) + self._i2c.readByte(self.address, self.BME280_DIG_P9_LSB_REG)

		self.calibration["dig_H1"] = self._i2c.readByte(self.address, self.BME280_DIG_H1_REG)
		self.calibration["dig_H2"] = (self._i2c.readByte(self.address, self.BME280_DIG_H2_MSB_REG) << 8) + self._i2c.readByte(self.address, self.BME280_DIG_H2_LSB_REG)
		self.calibration["dig_H3"] = self._i2c.readByte(self.address, self.BME280_DIG_H3_REG)
		self.calibration["dig_H4"] = (self._i2c.readByte(self.address, self.BME280_DIG_H4_MSB_REG) << 4) + (self._i2c.readByte(self.address, self.BME280_DIG_H4_LSB_REG) & 0x0F)
		self.calibration["dig_H5"] = (self._i2c.readByte(self.address, self.BME280_DIG_H5_MSB_REG) << 4) + ((self._i2c.readByte(self.address, self.BME280_DIG_H4_LSB_REG) >> 4) & 0x0F)
		self.calibration["dig_H6"] = self._i2c.readByte(self.address, self.BME280_DIG_H6_REG)

		# Most of the time the sensor will be init with default values
		# But in case user has old/deprecated code, use the _settings.x values
	
		self.setStandbyTime(_settings["tStandby"])
		self.setFilter(_settings["filter"])
		self.setPressureOverSample(_settings["pressOverSample"]) # Default of 1x oversample
		self.setHumidityOverSample(_settings["humidOverSample"]) # Default of 1x oversample
		self.setTempOverSample(_settings["tempOverSample"]) # Default of 1x oversample
	
		self.setMode(self.MODE_NORMAL) #Go!
	
		return self._i2c.readByte(self.address, self.BME280_CHIP_ID_REG)  # Should return 0x60

	def setMode(self, mode):

		if mode > 0b11:
			mode = 0  # Error check. Default to sleep mode
	
		controlData = self._i2c.readByte(self.address, self.BME280_CTRL_MEAS_REG)
		controlData &= (~( (1<<1) | (1<<0) ) ) & 0xFF # Clear the mode[1:0] bits - note we just want a byte
		controlData |= mode   # Set
		self._i2c.writeByte(self.address, self.BME280_CTRL_MEAS_REG, controlData)


	def getMode(self):
		
		controlData = self._i2c.readByte(self.address, self.BME280_CTRL_MEAS_REG)
		return controlData & 0b00000011

	# Set the standby bits in the config register
	# tStandby can be:
	#   0, 0.5ms
	#   1, 62.5ms
	#   2, 125ms
	#   3, 250ms
	#   4, 500ms
	#   5, 1000ms
	#   6, 10ms
	#   7, 20ms
	def setStandbyTime(self, timeSetting):

		if timeSetting > 0b111 :
			timeSetting = 0 # Error check. Default to 0.5ms
		
		controlData = self._i2c.readByte(self.address, self.BME280_CONFIG_REG)
		controlData &= ( ~( (1<<7) | (1<<6) | (1<<5) )) & 0xff # Clear the 7/6/5 bits
		controlData |= (timeSetting << 5) # Align with bits 7/6/5
		self._i2c.writeByte(self.address, self.BME280_CONFIG_REG, controlData)

	# Set the filter bits in the config register
	# filter can be off or number of FIR coefficients to use:
	#   0, filter off
	#   1, coefficients = 2
	#   2, coefficients = 4
	#   3, coefficients = 8
	#   4, coefficients = 16
	def setFilter(self, filterSetting):

		if filterSetting > 0b111 : 
			filterSetting = 0 # Error check. Default to filter off
		
		controlData = self._i2c.readByte(self.address, self.BME280_CONFIG_REG)
		controlData &= (~( (1<<4) | (1<<3) | (1<<2) ) ) & 0xFF # Clear the 4/3/2 bits
		controlData |= (filterSetting << 2) # Align with bits 4/3/2
		self._i2c.writeByte(self.address, self.BME280_CONFIG_REG, controlData)


	# Set the temperature oversample value
	# 0 turns off temp sensing
	# 1 to 16 are valid over sampling values
	def setTempOverSample(self, overSampleAmount):
	
		overSampleAmount = self.checkSampleValue(overSampleAmount) # Error check
		
		originalMode = self.getMode() # Get the current mode so we can go back to it at the end
		
		self.setMode(self.MODE_SLEEP) # Config will only be writeable in sleep mode, so first go to sleep mode
	
		# Set the osrs_t bits (7, 6, 5) to overSampleAmount
		controlData = self._i2c.readByte(self.address, self.BME280_CTRL_MEAS_REG)
		controlData &= (~( (1<<7) | (1<<6) | (1<<5) )) & 0xFF # Clear bits 765
		controlData |= overSampleAmount << 5 # Align overSampleAmount to bits 7/6/5
		self._i2c.writeByte(self.address, self.BME280_CTRL_MEAS_REG, controlData)
		
		self.setMode(originalMode) # Return to the original user's choice


	# Set the pressure oversample value
	# 0 turns off pressure sensing
	# 1 to 16 are valid over sampling values
	def setPressureOverSample(self, overSampleAmount):
	
		overSampleAmount = self.checkSampleValue(overSampleAmount) # Error check
		
		originalMode = self.getMode() # Get the current mode so we can go back to it at the end
		
		self.setMode(self.MODE_SLEEP) # Config will only be writeable in sleep mode, so first go to sleep mode
	
		# Set the osrs_p bits (4, 3, 2) to overSampleAmount
		controlData = self._i2c.readByte(self.address, self.BME280_CTRL_MEAS_REG)
		controlData &= (~( (1<<4) | (1<<3) | (1<<2) )) & 0xFF  # Clear bits 432
		controlData |= overSampleAmount << 2 # Align overSampleAmount to bits 4/3/2
		self._i2c.writeByte(self.address, self.BME280_CTRL_MEAS_REG, controlData)
		
		self.setMode(originalMode) # Return to the original user's choice

	# Set the humidity oversample value
	# 0 turns off humidity sensing
	# 1 to 16 are valid over sampling values
	def setHumidityOverSample(self, overSampleAmount):

		overSampleAmount = self.checkSampleValue(overSampleAmount) # Error check
		
		originalMode = self.getMode() # Get the current mode so we can go back to it at the end
		
		self.setMode(self.MODE_SLEEP) # Config will only be writeable in sleep mode, so first go to sleep mode
	
		# Set the osrs_h bits (2, 1, 0) to overSampleAmount
		controlData = self._i2c._i2c.readByte(self.address, self.BME280_CTRL_HUMIDITY_REG)
		controlData &= (~( (1<<2) | (1<<1) | (1<<0) )) & 0xFF # Clear bits 2/1/0
		controlData |= overSampleAmount << 0 # Align overSampleAmount to bits 2/1/0
		self._i2c.writeByte(self.address, self.BME280_CTRL_HUMIDITY_REG, controlData)
	
		self.setMode(originalMode) # Return to the original user's choice

	# Validates an over sample value
	# Allowed values are 0 to 16
	# These are used in the humidty, pressure, and temp oversample functions
	def checkSampleValue(self, userValue):

		_valueMap = { 0: 0, 1: 1, 2: 2, 4: 3, 8: 4, 16: 5}

		return _valueMap[userValue] if userValue in _valueMap.keys() else 1
		
	# Check the measuring bit and return true while device is taking measurement
	def isMeasuring(self):

		stat = self._i2c.readByte(self.address, self.BME280_STAT_REG)
		return  stat & (1<<3) # If the measuring bit (3) is set, return true

	
	# Strictly resets.  Run .begin() afterwards
	def reset( self ):

		self._i2c.writeByte(self.address, self.BME280_RST_REG, 0xB6)

	# ****************************************************************************# 
	# 
	#   Pressure Section
	# 
	# ****************************************************************************# 
	def readFloatPressure( self ):
	
		#  Returns pressure in Pa as unsigned 32 bit integer in Q24.8 format (24 integer bits and 8 fractional bits).
		#  Output value of "24674867" represents 24674867/256 = 96386.2 Pa = 963.862 hPa

		buffer = self._i2c.readBlock(self.address, self.BME280_PRESSURE_MSB_REG, 3)
		adc_P = (buffer[0] << 12) | (buffer[1] << 4) | ((buffer[2] >> 4) & 0x0F)
		
		var1 = self.t_fine - 128000
		var2 = var1 * var1 * self.calibration["dig_P6"]
		var2 = var2 + ((var1 * self.calibration["dig_P5"])<<17)
		var2 = var2 + (self.calibration["dig_P4"] <<35)
		var1 = ((var1 * var1 * self.calibration["dig_P3"])>>8) + ((var1 * self.calibration["dig_P2"])<<12)
		var1 = ( (1 << 47) + var1 )*(self.calibration["dig_P1"])>>33

		if var1 == 0:
			return 0  #  avoid exception caused by division by zero

		p_acc = 1048576 - adc_P
		p_acc = (((p_acc<<31) - var2)*3125)//var1

		var1 = ((self.calibration["dig_P9"]) * (p_acc>>13) * (p_acc>>13)) >> 25
		var2 = ((self.calibration["dig_P8"]) * p_acc) >> 19
		p_acc = ((p_acc + var1 + var2) >> 8) + ((self.calibration["dig_P7"])<<4)
		
		return p_acc / 256.0
		

	# Sets the internal variable _referencePressure so the 
	def setReferencePressure(self, refPressure):

		self._referencePressure = float(refPressure)
	
	# Return the local reference pressure
	def getReferencePressure(self):
		return self._referencePressure
	
	def readFloatAltitudeMeters( self ):

		# heightOutput = ((float)-45846.2)*(pow(((float)readFloatPressure()/(float)_referencePressure), 0.190263) - (float)1);

		return (-44330.77)*(math.pow((self.readFloatPressure()/self._referencePressure), 0.190263) - 1.0) # Corrected, see issue 30
	
	def readFloatAltitudeFeet( self ):
	
		return self.readFloatAltitudeMeters() * 3.28084
	

	# ****************************************************************************# 
	# 
	#   Humidity Section
	# 
	# ****************************************************************************# 
	def readFloatHumidity( self ):
		
		#  Returns humidity in %RH as unsigned 32 bit integer in Q22. 10 format (22 integer and 10 fractional bits).
		#  Output value of "47445" represents 47445/1024 = 46. 33 %RH

		buffer = self._i2c.readBlock(self.address, self.BME280_HUMIDITY_MSB_REG, 2)
		adc_H = (buffer[0] << 8) | buffer[1]
		
		var1 = (self.t_fine - 76800)
		var1 = (((((adc_H << 14) - ((self.calibration["dig_H4"]) << 20) - ((self.calibration["dig_H5"]) * var1)) + \
			(16384)) >> 15) * (((((((var1 * (self.calibration["dig_H6"])) >> 10) * (((var1 * (self.calibration["dig_H3"])) >> 11) + (32768))) >> 10) + (2097152)) * \
			(self.calibration["dig_H2"]) + 8192) >> 14))
		var1 = (var1 - (((((var1 >> 15) * (var1 >> 15)) >> 7) * (self.calibration["dig_H1"])) >> 4))
		var1 = 0 if var1 < 0 else  var1 
		var1 = 419430400 if var1 > 419430400 else var1

	
		return (var1>>12) / 1024.0

	# ****************************************************************************# 
	# 
	#   Temperature Section
	# 
	# ****************************************************************************# 
	
	def readTempC( self ):

		#  Returns temperature in DegC, resolution is 0.01 DegC. Output value of "5123" equals 51.23 DegC.
		#  t_fine carries fine temperature as global value
	
		# get the reading (adc_T);

		buffer = self._i2c.readBlock(self.address, self.BME280_TEMPERATURE_MSB_REG, 3)
		adc_T = (buffer[0] << 12) | (buffer[1] << 4) | ((buffer[2] >> 4) & 0x0F)
	
		# By datasheet, calibrate
	
		var1 = ((((adc_T>>3) - (self.calibration["dig_T1"]<<1))) * (self.calibration["dig_T2"])) >> 11
		var2 = (((((adc_T>>4) - (self.calibration["dig_T1"])) * ((adc_T>>4) - (self.calibration["dig_T1"]))) >> 12) * \
				(self.calibration["dig_T3"])) >> 14
		self.t_fine = var1 + var2
		output = (self.t_fine * 5 + 128) >> 8
	
		return output / 100 + _settings["tempCorrection"]
		
	
	def readTempF( self ):

		output = self.readTempC()
		return (output * 9) / 5 + 32

	# ****************************************************************************# 
	# 
	#   Dew point Section
	# 
	# ****************************************************************************# 
	#  Returns Dew point in DegC

	def dewPointC(self):

		celsius = self.readTempC() 
		humidity = self.readFloatHumidity()
		#  (1) Saturation Vapor Pressure = ESGG(T)

		RATIO = 373.15 / (273.15 + celsius)
		RHS = -7.90298 * (RATIO - 1)
		RHS += 5.02808 * math.log10(RATIO)
		RHS += -1.3816e-7 * (math.pow(10, (11.344 * (1 - 1/RATIO ))) - 1) 
		RHS += 8.1328e-3 * (math.pow(10, (-3.49149 * (RATIO - 1))) - 1)
		RHS += math.log10(1013.246)
		       #  factor -3 is to adjust units - Vapor Pressure SVP * humidity
		VP = math.pow(10, RHS - 3) * humidity
		       #  (2) DEWPOINT = F(Vapor Pressure)
		T = math.log(VP/0.61078)   #  temp var
		return (241.88 * T) / (17.558 - T)
	
	#  Returns Dew point in DegF
	def dewPointF(self):
		return self.dewPointC() * 1.8 + 32 # Convert C to F

	