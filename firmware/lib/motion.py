import lib.imu as imu
import motor
from machine import Timer
import time


class Motion:
  def __init__(self, motorPins=[[14,13],[11,12]], turnPrecision=3, turnTimeoutMs=5000):
    self.imu = imu.IMU()
    self.motor = motor.Motor(motorPins)
    self.timer = Timer(0)

    self.turnPrecision = turnPrecision
    self.turnTimeoutMs = turnTimeoutMs

    self.cnt = 0
    self.imuData = None
    self.cmd = None
    self.lastCmd = None
    self.startAngle = 0.0
    self.targetAngle = 0.0  # cumulative yaw target
    self.prevError = 0.0
    self.integral = 0.0
    self.doneCnt = 0
    self.speed = 0
    self.turnSpeed = 0
    self.busy = False
    self.tStart = 0


  def start(self):
    self.timer.init(period=10, mode=Timer.PERIODIC, callback=self.update)


  def stopMotion(self):
    self.timer.deinit()
    self.motor.stop()


  def turn(self, angle, speed=0xFFFF, blocking=False):
    self.cmd = ('turn', angle, speed)
    self.busy = True
    if blocking:
      while self.busy:
        time.sleep_ms(10)

  def forward(self, speed=1000):
    self.cmd = ('forward', speed)

  def stop(self):
    self.cmd = ('stop', 0)

  def getYaw(self):
    return self.imu.yawUnwrapped

  def update(self, t):
    imuData = self.imu.read()
    if(imuData):
      self.imuData = imuData
      # self.cnt = self.cnt + 1
      # if(self.cnt > 10):
      #   self.cnt = 0
      #   print("IMU data:", imuData)

    if self.cmd:
      self.lastCmd = self.cmd
      self.cmd = None
      # print("Executing command:", self.lastCmd)
      if self.lastCmd[0] == 'turn':
        self.startAngle = self.imuData[0]
        self.targetAngle = self.startAngle + self.lastCmd[1]
        self.speed = 0
        self.turnSpeed = self.lastCmd[2]
        self.doneCnt = 0
        self.tStart = time.ticks_ms()
      elif self.lastCmd[0] == 'forward':
        self.startAngle = self.imuData[0]
        self.targetAngle = self.startAngle
        self.speed = self.lastCmd[1]
      elif self.lastCmd[0] == 'stop':
        self.motor.stop()
        self.lastCmd = None
        # print("Stop command executed")

    
    if self.lastCmd:
      if self.lastCmd[0] == 'turn' or self.lastCmd[0] == 'forward':
        # Do PID turn using cumulative (unwrapped) yaw
        error = self.targetAngle - self.imuData[0]
        if (abs(error) < self.turnPrecision  or time.ticks_diff(time.ticks_ms(), self.tStart) > self.turnTimeoutMs) and self.lastCmd[0] == 'turn':
          self.doneCnt += 1
          if self.doneCnt > 5:
            self.motor.stop()
            self.lastCmd = None
            self.busy = False
            # print("Turn completed")
        else:
          p = error
          d = (error - self.prevError) / 0.01
          self.integral += error * 0.01
          i = self.integral
          self.prevError = error

          turnSpeed = int(1000 * p + 10 * d + 20 * i)

          # Limit to self.turnSpeed
          turnSpeed = max(-self.turnSpeed, min(self.turnSpeed, turnSpeed))

          self.motor.drive(max(-65535, min(65535, self.speed + turnSpeed)), max(-65535, min(65535, self.speed - turnSpeed)))