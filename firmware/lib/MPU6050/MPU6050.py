# MicroPython MPU6050 driver, based on the InvenSense MPU-6050 register map and descriptions.

from .MPU6050_defs import *
from . import I2Cdev
import time

class MPU6050:
  
  def __init__(self, address=MPU6050_DEFAULT_ADDRESS, bus=None):
    self.devAddr = address
    self.bus = bus
    self.fifoTimeout = MPU6050_FIFO_DEFAULT_TIMEOUT

  def initialize(self):
    self.setClockSource(MPU6050_CLOCK_PLL_XGYRO)
    self.setFullScaleGyroRange(MPU6050_GYRO_FS_250)
    self.setFullScaleAccelRange(MPU6050_ACCEL_FS_2)
    self.setSleepEnabled(False)

  def testConnection(self):
    return self.getDeviceID() == 0x34


  def getXGyroOffset(self):
    return self.bus.readBytes(self.devAddr, MPU6050_RA_XG_OFFS_USRH, 2)
  
  def setXGyroOffset(self, offset):
    self.bus.writeWord(self.devAddr, MPU6050_RA_XG_OFFS_USRH, offset & 0xFFFF)

  def getYGyroOffset(self):
    return self.bus.readBytes(self.devAddr, MPU6050_RA_YG_OFFS_USRH, 2)
  
  def setYGyroOffset(self, offset):
    self.bus.writeWord(self.devAddr, MPU6050_RA_YG_OFFS_USRH, offset & 0xFFFF)

  def getZGyroOffset(self):
    return self.bus.readBytes(self.devAddr, MPU6050_RA_ZG_OFFS_USRH, 2)
  
  def setZGyroOffset(self, offset):
    self.bus.writeWord(self.devAddr, MPU6050_RA_ZG_OFFS_USRH, offset & 0xFFFF)

  def getXAccelOffset(self):
    SaveAddress = MPU6050_RA_XA_OFFS_H if (self.getDeviceID() < 0x38) else 0x77
    buffer = self.bus.readBytes(self.devAddr, SaveAddress, 2)
    return ((buffer[0] << 8) | buffer[1])
  
  def setXAccelOffset(self, offset):
    SaveAddress = MPU6050_RA_XA_OFFS_H if (self.getDeviceID() < 0x38) else 0x77
    self.bus.writeWord(self.devAddr, SaveAddress, offset & 0xFFFF)

  def getYAccelOffset(self):
    SaveAddress = MPU6050_RA_YA_OFFS_H if (self.getDeviceID() < 0x38) else 0x7A
    buffer = self.bus.readBytes(self.devAddr, SaveAddress, 2)
    return ((buffer[0] << 8) | buffer[1])
  
  def setYAccelOffset(self, offset):
    SaveAddress = MPU6050_RA_YA_OFFS_H if (self.getDeviceID() < 0x38) else 0x7A
    self.bus.writeWord(self.devAddr, SaveAddress, offset & 0xFFFF)

  def getZAccelOffset(self):
    SaveAddress = MPU6050_RA_ZA_OFFS_H if (self.getDeviceID() < 0x38) else 0x7D
    buffer = self.bus.readBytes(self.devAddr, SaveAddress, 2)
    return ((buffer[0] << 8) | buffer[1])
  
  def setZAccelOffset(self, offset):
    SaveAddress = MPU6050_RA_ZA_OFFS_H if (self.getDeviceID() < 0x38) else 0x7D
    self.bus.writeWord(self.devAddr, SaveAddress, offset & 0xFFFF)


  def getRate(self):
    return self.bus.readByte(self.devAddr, MPU6050_RA_SMPLRT_DIV)
  
  def setRate(self, rate):
    self.bus.writeByte(self.devAddr, MPU6050_RA_SMPLRT_DIV, rate)



  def getFullScaleGyroRange(self):
    return self.bus.readBits(self.devAddr, MPU6050_RA_GYRO_CONFIG, MPU6050_GCONFIG_FS_SEL_BIT, MPU6050_GCONFIG_FS_SEL_LENGTH)
  
  def setFullScaleGyroRange(self, range):
    self.bus.writeBits(self.devAddr, MPU6050_RA_GYRO_CONFIG, MPU6050_GCONFIG_FS_SEL_BIT, MPU6050_GCONFIG_FS_SEL_LENGTH, range)

  def getFullScaleAccelRange(self):
    return self.bus.readBits(self.devAddr, MPU6050_RA_ACCEL_CONFIG, MPU6050_ACONFIG_AFS_SEL_BIT, MPU6050_ACONFIG_AFS_SEL_LENGTH)
  
  def setFullScaleAccelRange(self, range):
    self.bus.writeBits(self.devAddr, MPU6050_RA_ACCEL_CONFIG, MPU6050_ACONFIG_AFS_SEL_BIT, MPU6050_ACONFIG_AFS_SEL_LENGTH, range)


  def getDeviceID(self):
    return self.bus.readBits(self.devAddr, MPU6050_RA_WHO_AM_I, MPU6050_WHO_AM_I_BIT, MPU6050_WHO_AM_I_LENGTH)


  def setClockSource(self, source):
    self.bus.writeBits(self.devAddr, MPU6050_RA_PWR_MGMT_1, MPU6050_PWR1_CLKSEL_BIT, MPU6050_PWR1_CLKSEL_LENGTH, source)

  def setFullScaleGyroRange(self, range):
    self.bus.writeBits(self.devAddr, MPU6050_RA_GYRO_CONFIG, MPU6050_GCONFIG_FS_SEL_BIT, MPU6050_GCONFIG_FS_SEL_LENGTH, range)

  def setFullScaleAccelRange(self, range):
    self.bus.writeBits(self.devAddr, MPU6050_RA_ACCEL_CONFIG, MPU6050_ACONFIG_AFS_SEL_BIT, MPU6050_ACONFIG_AFS_SEL_LENGTH, range)

  def setSleepEnabled(self, enabled):
    self.bus.writeBits(self.devAddr, MPU6050_RA_PWR_MGMT_1, MPU6050_PWR1_SLEEP_BIT, 1, int(enabled))


  def setDMPEnabled(self, enabled):
    self.bus.writeBit(self.devAddr, MPU6050_RA_USER_CTRL, MPU6050_USERCTRL_DMP_EN_BIT, int(enabled))


  def setMemoryBank(self, bank, prefetchEnabled=False, userBank=False):
    bank = bank & 0x1F
    if (userBank):
      bank = bank | 0x20
    if (prefetchEnabled):
      bank = bank | 0x40
    self.bus.writeByte(self.devAddr, MPU6050_RA_BANK_SEL, bank)


  def setMemoryStartAddress(self, address):
    self.bus.writeByte(self.devAddr, MPU6050_RA_MEM_START_ADDR, address)


  def writeMemoryBlock(self, data, dataSize, bank=0, address=0, verify=True):
    self.setMemoryBank(bank)
    self.setMemoryStartAddress(address)

    i = 0
    while(i < dataSize):
      chunkSize = MPU6050_DMP_MEMORY_CHUNK_SIZE

      # make sure we don't go past the data size
      if (i + chunkSize > dataSize):
        chunkSize = dataSize - i

      # make sure this chunk doesn't go past the bank boundary (256 bytes)
      if (chunkSize > 256 - address):
        chunkSize = 256 - address

      self.setMemoryBank(bank)
      self.setMemoryStartAddress(address)
      self.bus.writeBytes(self.devAddr, MPU6050_RA_MEM_R_W, data[i:i+chunkSize])

      if (verify):
        self.setMemoryBank(bank)
        self.setMemoryStartAddress(address)
        verifyData = self.bus.readBytes(self.devAddr, MPU6050_RA_MEM_R_W, chunkSize)
        for j in range(chunkSize):
          if (verifyData[j] != data[i + j]):
            return False
          
      # increase byte index by chunkSize
      i += chunkSize

      address = (address + chunkSize) % 256  # wrap around to the beginning of the bank if necessary

      # if we aren't done, update bank (if necessary) and address
      if (i < dataSize):
        if (address == 0):
          bank += 1
          self.setMemoryBank(bank)
          self.setMemoryStartAddress(address)

    return True


  def writeProgMemoryBlock(self, data, dataSize, bank=0, address=0, verify=True):
    return self.writeMemoryBlock(data, dataSize, bank, address, verify)
  

  def resetFIFO(self):
    self.bus.writeBit(self.devAddr, MPU6050_RA_USER_CTRL, MPU6050_USERCTRL_FIFO_RESET_BIT, 1)

  def resetDMP(self):
    self.bus.writeBit(self.devAddr, MPU6050_RA_USER_CTRL, MPU6050_USERCTRL_DMP_RESET_BIT, 1)


  def getFIFOCount(self):
    return self.bus.readWord(self.devAddr, MPU6050_RA_FIFO_COUNTH)
  
  def getFIFOBytes(self, data, length):
    if(length > 0):
      data[0:length] = self.bus.readBytes(self.devAddr, MPU6050_RA_FIFO_R_W, length)
    else:
      data = []

  def getFIFOTimeout(self):
    return self.fifoTimeout
  
  def setFIFOTimeout(self, timeout):
    self.fifoTimeout = timeout


  def GetCurrentFIFOPacket(self, data, length):
    i2cBufLength = 256

    fifoC = 0
    # This section of code is for when we allowed more than 1 packet to be acquired
    BreakTimer = time.ticks_us()
    packetReceived = False
    
    while not packetReceived:
      fifoC = self.getFIFOCount()
      if fifoC > length:

        if fifoC > 200:  # if you waited to get the FIFO buffer to > 200 bytes it will take longer to get the last packet in the FIFO Buffer than it will take to  reset the buffer and wait for the next to arrive
          self.resetFIFO()  # Fixes any overflow corruption
          fifoC = 0
          while not (fifoC := self.getFIFOCount()) and ((time.ticks_us() - BreakTimer) <= (self.getFIFOTimeout())):  # Get Next New Packet
            pass
        else:  # We have more than 1 packet but less than 200 bytes of data in the FIFO Buffer
          Trash = bytearray(i2cBufLength)
          while (fifoC := self.getFIFOCount()) > length:  # Test each time just in case the MPU is writing to the FIFO Buffer
            fifoC = fifoC - length  # Save the last packet
            RemoveBytes = 0
            while fifoC:  # fifo count will reach zero so this is safe
              RemoveBytes = fifoC if fifoC < i2cBufLength else i2cBufLength  # Buffer Length is different than the packet length this will efficiently clear the buffer
              self.getFIFOBytes(Trash, RemoveBytes)
              fifoC -= RemoveBytes

      if not fifoC:
        return 0  # Called too early no data or we timed out after FIFO Reset
      # We have 1 packet
      packetReceived = fifoC == length
      if not packetReceived and (time.ticks_us() - BreakTimer) > (self.getFIFOTimeout()):
        return 0  # Called too early no data or we timed out after FIFO Reset

    self.getFIFOBytes(data, length); # Get 1 packet
    
    return 1




  def map(self, x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

  @staticmethod
  def _to_int16(val):
    """Convert unsigned 16-bit value to signed int16."""
    return val - 0x10000 if val > 0x7FFF else val


  def CalibrateGyro(self, loops=6):
    kP = 0.3
    kI = 90
    x = (100 - self.map(loops, 1, 5, 20, 0)) * 0.01
    kP *= x
    kI *= x
    self.PID(0x43, kP, kI, loops)


  def CalibrateAccel(self, loops=6):
    kP = 0.3
    kI = 20
    x = (100 - self.map(loops, 1, 5, 20, 0)) * 0.01
    kP *= x
    kI *= x
    self.PID(0x3B, kP, kI, loops)

  
  def PID(self, ReadAddress, kP, kI, loops):
    SaveAddress = 0x13
    if(ReadAddress == 0x3B):
      if(self.getDeviceID() < 0x38):
        SaveAddress = 0x06
      else:
        SaveAddress = 0x77

    BitZero = [0, 0, 0]
    shift = 2
    if(SaveAddress == 0x77):
      shift = 3

    Error = 0.0
    PTerm = 0.0
    ITerm = [0.0, 0.0, 0.0]

    gravity = 8192
    if(ReadAddress == 0x3B):
      gravity = 16384 >> self.getFullScaleAccelRange()

    print(">")

    for i in range(3):
      reading = self._to_int16(self.bus.readWord(self.devAddr, SaveAddress + (i * shift)))
      if(SaveAddress != 0x13):
        BitZero[i] = reading & 1
        ITerm[i] = float(reading) * 8.0
      else:
        ITerm[i] = float(reading) * 4.0

    for loop in range(loops):
      eSample = 0
      for c in range(100): # 100 PI Calculations
        eSum = 0
        for i in range(3):
          Reading = self._to_int16(self.bus.readWord(self.devAddr, ReadAddress + (i * 2)))
          if (ReadAddress == 0x3B) and (i == 2):
            Reading -= gravity  # remove Gravity
          Error = -Reading
          eSum += abs(Reading)
          PTerm = kP * Error
          ITerm[i] += (Error * 0.001) * kI  # Integral term 1000 Calculations a second = 0.001
          if(SaveAddress != 0x13):
            Data = round((PTerm + ITerm[i]) / 8)  # Compute PID Output
            Data = max(-32768, min(32767, Data))  # clamp to int16
            Data = (Data & ~1) | BitZero[i]  # Insert Bit0 Saved at beginning
          else:
            Data = round((PTerm + ITerm[i]) / 4)  # Compute PID Output
            Data = max(-32768, min(32767, Data))  # clamp to int16

          self.bus.writeWord(self.devAddr, SaveAddress + (i * shift), Data & 0xFFFF)
	
        if((c == 99) and eSum > 1000):					# Error is still to great to continue 
          c = 0
          print('*')

        coef = 0.05 if (ReadAddress == 0x3B) else 1
        if((eSum * coef) < 5):
          eSample += 1 # Successfully found offsets prepare to  advance

        if((eSum < 100) and (c > 10) and (eSample >= 10)):
          break		# Advance to next Loop

        time.sleep_ms(1)
		
      print('.')
      kP *= 0.75
      kI *= 0.75
      for i in range(3):
        if(SaveAddress != 0x13):
          Data = round(ITerm[i] / 8)  # Compute PID Output
          Data = max(-32768, min(32767, Data))  # clamp to int16
          Data = (Data & ~1) | BitZero[i]  # Insert Bit0 Saved at beginning
        else:
          Data = round(ITerm[i] / 4)
          Data = max(-32768, min(32767, Data))  # clamp to int16

        self.bus.writeWord(self.devAddr, SaveAddress + (i * shift), Data & 0xFFFF)

    self.resetFIFO()
    self.resetDMP()



  def GetActiveOffsets(self):
    AOffsetRegister = 0x06 if self.getDeviceID() < 0x38 else 0x77
    offsets = [0] * 6
    if AOffsetRegister == 0x06:
      offsets[0] = self.bus.readWord(self.devAddr, AOffsetRegister)
      offsets[1] = self.bus.readWord(self.devAddr, AOffsetRegister + 2)
      offsets[2] = self.bus.readWord(self.devAddr, AOffsetRegister + 4)
    else:
      offsets[0] = self.bus.readWord(self.devAddr, AOffsetRegister)
      offsets[1] = self.bus.readWord(self.devAddr, AOffsetRegister + 3)
      offsets[2] = self.bus.readWord(self.devAddr, AOffsetRegister + 6)

    offsets[3] = self.bus.readWord(self.devAddr, 0x13)
    offsets[4] = self.bus.readWord(self.devAddr, 0x15)
    offsets[5] = self.bus.readWord(self.devAddr, 0x17)

    return offsets
  

  def SetActiveOffsets(self, offsets):
    AOffsetRegister = 0x06 if self.getDeviceID() < 0x38 else 0x77
    if AOffsetRegister == 0x06:
      self.bus.writeWord(self.devAddr, AOffsetRegister, offsets[0] & 0xFFFF)
      self.bus.writeWord(self.devAddr, AOffsetRegister + 2, offsets[1] & 0xFFFF)
      self.bus.writeWord(self.devAddr, AOffsetRegister + 4, offsets[2] & 0xFFFF)
    else:
      self.bus.writeWord(self.devAddr, AOffsetRegister, offsets[0] & 0xFFFF)
      self.bus.writeWord(self.devAddr, AOffsetRegister + 3, offsets[1] & 0xFFFF)
      self.bus.writeWord(self.devAddr, AOffsetRegister + 6, offsets[2] & 0xFFFF)

    self.bus.writeWord(self.devAddr, 0x13, offsets[3] & 0xFFFF)
    self.bus.writeWord(self.devAddr, 0x15, offsets[4] & 0xFFFF)
    self.bus.writeWord(self.devAddr, 0x17, offsets[5] & 0xFFFF)
  
  def PrintActiveOffsets(self):
    offsets = self.GetActiveOffsets()
    print(f"{offsets[0]},\t{offsets[1]},\t{offsets[2]},\t{offsets[3]},\t{offsets[4]},\t{offsets[5]}\n\n")
