from machine import Pin, PWM


class Motor:
    
  def __init__(self, motorPins=[[14,13],[11,12]]):
    print("This is robot")
    
    self.motor = [[PWM(Pin(motorPins[0][0]),freq=1024,duty_u16=0xFFFF),
                  PWM(Pin(motorPins[0][1]),freq=1024,duty_u16=0xFFFF)],
                  [PWM(Pin(motorPins[1][0]),freq=1024,duty_u16=0xFFFF),
                  PWM(Pin(motorPins[1][1]),freq=1024,duty_u16=0xFFFF)]]

  
  def deinit(self):
    self.stop()
      
  def drive(self, left, right):
    self.__driveMotor(0,left)
    self.__driveMotor(1,right)
      
  
  def stop(self):
    self.drive(0,0)
      
      
  def __driveMotor(self, mId, speed):        
    if speed > 0:
      if speed > 0xFFFF:
        speed = 0xFFFF
      self.motor[mId][0].duty_u16(0xFFFF)
      self.motor[mId][1].duty_u16(0xFFFF-speed)
    elif speed < 0:
      if speed < -0xFFFF:
        speed = -0xFFFF
      self.motor[mId][1].duty_u16(0xFFFF)
      self.motor[mId][0].duty_u16(0xFFFF+speed)
    else:
      self.motor[mId][0].duty_u16(0xFFFF)
      self.motor[mId][1].duty_u16(0xFFFF)
