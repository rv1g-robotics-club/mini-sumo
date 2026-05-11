from machine import Pin, I2C
from MPU6050 import I2Cdev
from MPU6050.MPU6050_DMP import MPU6050_DMP
from MPU6050.helper_3dmath import Quaternion, VectorFloat
import time
import json


class IMU:

  def __init__(self):
    self.i2c = I2C(0, sda=Pin(10), scl=Pin(9), freq=400000)
    self.imuI2c = I2Cdev.I2Cdev(self.i2c)

    self.mpu = MPU6050_DMP(bus=self.imuI2c)
    self.mpu.initialize()

    if(self.mpu.testConnection()):
        print("MPU6050 connection OK")
    else:
        print("MPU6050 connection failed")
    
    print("Initializing DMP...")
    devStatus = self.mpu.dmpInitialize()


    #mpu.setXGyroOffset(220)
    #mpu.setYGyroOffset(76)
    #mpu.setZGyroOffset(-85)
    #mpu.setZAccelOffset(1788) # 1688 factory default for my test chip

    if(devStatus == 0):
      print("DMP OK")

      # Try to load calibration, if it fails, do calibration and save it
      if(self.loadCalibration() is None):
        self.mpu.CalibrateAccel(6)
        self.mpu.CalibrateGyro(6)
        self.mpu.PrintActiveOffsets()
        self.saveCalibration()
        print("Calibration saved")
      else:
        print("Calibration loaded")

      self.mpu.setDMPEnabled(True)
    else:
      print("DMP failed")
        
        
    self.fifoBuffer = bytearray(64)
    self.q = Quaternion()
    self.gravity = VectorFloat()
    self.ypr = [0.0, 0.0, 0.0]
    self.t = time.ticks_us()
    self.cnt = 0
    self.yawUnwrapped = 0.0
    self.lastYawRaw = None
        
    print("Done")


  def saveCalibration(self):
    offsets = self.mpu.GetActiveOffsets()
    with open("imu_calibration.json", "w") as f:
      json.dump(offsets, f)


  def loadCalibration(self):
    try:
      with open("imu_calibration.json", "r") as f:
        offsets = json.load(f)
        # self.mpu.setXAccelOffset(offsets[0])
        # self.mpu.setYAccelOffset(offsets[1])
        # self.mpu.setZAccelOffset(offsets[2])
        # self.mpu.setXGyroOffset(offsets[3])
        # self.mpu.setYGyroOffset(offsets[4])
        # self.mpu.setZGyroOffset(offsets[5])
        self.mpu.SetActiveOffsets(offsets)
        return offsets
    except Exception as e:
      print("Failed to load calibration:", e)
    return None
  

  def read(self):
    if(self.mpu.dmpGetCurrentFIFOPacket(self.fifoBuffer)):
      now = time.ticks_us()
      period = now - self.t
      self.t = now
      self.mpu.dmpGetQuaternion(self.q, self.fifoBuffer)
      self.mpu.dmpGetGravity(self.gravity, self.q)
      self.mpu.dmpGetYawPitchRoll(self.ypr, self.q, self.gravity)
      yawRaw = self.ypr[0] * 180 / 3.1415
      if self.lastYawRaw is None:
        self.lastYawRaw = yawRaw
      delta = yawRaw - self.lastYawRaw
      # Unwrap: correct for wrap-around at ±180
      if delta > 180:
        delta -= 360
      elif delta < -180:
        delta += 360
      self.yawUnwrapped += delta
      self.lastYawRaw = yawRaw
      return [self.yawUnwrapped, (self.ypr[1] * 180 / 3.1415), (self.ypr[2] * 180 / 3.1415)]
