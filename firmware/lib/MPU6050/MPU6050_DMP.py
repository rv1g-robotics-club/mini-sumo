from .MPU6050 import MPU6050
from .MPU6050_defs import *
from .MPU6050_DMP_FW import dmpMemory
from .helper_3dmath import Quaternion, VectorFloat
import time
from math import atan2, sqrt, pi as PI

class MPU6050_DMP(MPU6050):
  def __init__(self, address=MPU6050_DEFAULT_ADDRESS, bus=None):
    super().__init__(address, bus)
    self.dmpPacketSize = 0
    self.dmpPacketBuffer = None


  def dmpInitialize(self):
    self.bus.writeBit(self.devAddr, 0x6B, 7, 1)
    time.sleep(0.1)
    self.bus.writeBits(self.devAddr, 0x6A, 2, 3, 7)
    time.sleep(0.1)
    self.bus.writeByte(self.devAddr, 0x6B, 0x01)  # 1000 0001 PWR_MGMT_1:Clock Source Select PLL_X_gyro
    self.bus.writeByte(self.devAddr, 0x38, 0x00)  # 0000 0000 INT_ENABLE: no Interrupt
    self.bus.writeByte(self.devAddr, 0x23, 0x00)  # 0000 0000 MPU FIFO_EN: (all off) Using DMP's FIFO instead
    self.bus.writeByte(self.devAddr, 0x1C, 0x00)  # 0000 0000 ACCEL_CONFIG: 0 =  Accel Full Scale Select: 2g
    self.bus.writeByte(self.devAddr, 0x37, 0x80)  # 1000 0000 INT_PIN_CFG: ACTL active low interrupt
    self.bus.writeByte(self.devAddr, 0x6B, 0x01)  # 0000 0001 PWR_MGMT_1: Clock Source Select PLL_X_gyro
    self.bus.writeByte(self.devAddr, 0x19, 0x04)  # 0000 0100 SMPLRT_DIV: Divides the internal sample rate 400Hz ( Sample Rate = Gyroscope Output Rate / (1 + SMPLRT_DIV))
    self.bus.writeByte(self.devAddr, 0x1A, 0x01)  # 0000 0001 CONFIG: Digital Low Pass Filter (DLPF) Configuration 188HZ  //Im betting this will be the beat

    # Loads the DMP image into the MPU6050 Memory // Should Never Fail
    if (not self.writeProgMemoryBlock(dmpMemory, len(dmpMemory))):
      return 1
      
    self.bus.writeWord(self.devAddr, 0x70, 0x0400)  # DMP Program Start Address
    self.bus.writeByte(self.devAddr, 0x1B, 0x18)     # 0001 1000 GYRO_CONFIG: 3 = +2000 Deg/sec
    self.bus.writeByte(self.devAddr, 0x6A, 0xC0)     # 1100 1100 USER_CTRL: Enable Fifo and Reset Fifo
    self.bus.writeByte(self.devAddr, 0x38, 0x02)     # 0000 0010 INT_ENABLE: RAW_DMP_INT_EN on
    self.bus.writeBit(self.devAddr,  0x6A, 2, 1)      # Reset FIFO one last time just for kicks. (MPUi2cWrite reads 0x6A first and only alters 1 bit and then saves the byte)

    self.setDMPEnabled(False) # disable DMP for compatibility with the MPU6050 library

    self.dmpPacketSize = 28

    return 0
  

  def dmpGetQuaternionInt16(self, data, packet):
    # TODO: accommodate different arrangements of sent data (ONLY default supported now)
    if (packet == None):
      packet = self.dmpPacketBuffer

    data[0] = ((packet[0] << 8) | packet[1])
    data[1] = ((packet[4] << 8) | packet[5])
    data[2] = ((packet[8] << 8) | packet[9])
    data[3] = ((packet[12] << 8) | packet[13])
    # Convert unsigned 16-bit to signed 16-bit
    for i in range(4):
      if data[i] > 32767:
        data[i] -= 65536
    return 0


  def dmpGetQuaternion(self, q, packet):
    # TODO: accommodate different arrangements of sent data (ONLY default supported now)
    qI = [0] * 4
    status = self.dmpGetQuaternionInt16(qI, packet)
    if status == 0:
        q.w = float(qI[0]) / 16384.0
        q.x = float(qI[1]) / 16384.0
        q.y = float(qI[2]) / 16384.0
        q.z = float(qI[3]) / 16384.0
        return 0
    return status
  

  def dmpGetGravity(self, v, q):
    v.x = 2 * (q.x * q.z - q.w * q.y)
    v.y = 2 * (q.w * q.x + q.y * q.z)
    v.z = q.w * q.w - q.x * q.x - q.y * q.y + q.z * q.z
    return 0


  def dmpGetYawPitchRoll(self, data, q, gravity):
    # yaw: (about Z axis)
    data[0] = atan2(2*q.x*q.y - 2*q.w*q.z, 2*q.w*q.w + 2*q.x*q.x - 1)
    # pitch: (nose up/down, about Y axis)
    data[1] = atan2(gravity.x , sqrt(gravity.y*gravity.y + gravity.z*gravity.z))
    # roll: (tilt left/right, about X axis)
    data[2] = atan2(gravity.y , gravity.z)
    if (gravity.z < 0):
      if(data[1] > 0):
        data[1] = PI - data[1]
      else:
        data[1] = -PI - data[1]
    return 0

  
  def dmpGetFIFOPacketSize(self):
    return self.dmpPacketSize
  

  def dmpGetCurrentFIFOPacket(self, data):
    return self.GetCurrentFIFOPacket(data, self.dmpPacketSize)