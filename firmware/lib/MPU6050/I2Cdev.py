from machine import I2C


class I2Cdev:

  def __init__(self, i2c: I2C):
    self.i2c = i2c

  def readByte(self, devAddr, regAddr):
    return self.i2c.readfrom_mem(devAddr, regAddr, 1)[0]
  
  def readBytes(self, devAddr, regAddr, length):
    return self.i2c.readfrom_mem(devAddr, regAddr, length)
  
  def readWord(self, devAddr, regAddr):
    data = self.i2c.readfrom_mem(devAddr, regAddr, 2)
    return int.from_bytes(data, 'big')
  
  def writeByte(self, devAddr, regAddr, data):
    self.i2c.writeto_mem(devAddr, regAddr, bytes([data]))

  def writeBytes(self, devAddr, regAddr, data):
    self.i2c.writeto_mem(devAddr, regAddr, bytes(data))

  def writeWord(self, devAddr, regAddr, data):
    self.i2c.writeto_mem(devAddr, regAddr, data.to_bytes(2, 'big'))

  def readBits(self, devAddr, regAddr, bitStart, length):
    b = self.readByte(devAddr, regAddr)
    mask = ((1 << length) - 1) << (bitStart - length + 1)
    b &= mask
    b >>= (bitStart - length + 1)
    return b

  def writeBit(self, devAddr, regAddr, bitNum, data):
    b = self.readByte(devAddr, regAddr)
    b = (b & ~(1 << bitNum)) | ((data & 1) << bitNum)
    self.writeByte(devAddr, regAddr, b)

  def writeBits(self, devAddr, regAddr, bitStart, length, data):
    b = self.readByte(devAddr, regAddr)
    mask = ((1 << length) - 1) << (bitStart - length + 1)
    data <<= (bitStart - length + 1)  # shift data into correct position
    data &= mask  # zero all non-important bits in data
    b &= ~mask  # zero all important bits in existing byte
    b |= data  # combine data with existing byte
    self.writeByte(devAddr, regAddr, b)