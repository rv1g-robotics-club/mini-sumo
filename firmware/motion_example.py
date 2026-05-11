import time
import lib.motion


# Initialize motion control - motors and IMU
motion = lib.motion.Motion()
# If motors do not work properly, you might need to change the motor pinout
# by executing initialization with extra parameter motorPins
# Default connection is: [[14,13],[11,12]]
# You might need to swap the motor pins from 14,13 to 13,14 or 11,12 to 12,11 depending on your wiring
# Example:
#   # Initialize with swapped left motor pins
#   motion = lib.motion.Motion(motorPins=[[13,14],[11,12]])

# Start Motion control
motion.start()

# Motion usage examples:

# Go forward at speed 10000 (max is 0xFFFF or 65535)
motion.forward(10000) # This is non-blocking, it will keep moving until you call stop() or forward() again with different speed or duration
time.sleep_ms(1000)  # Move for 1 second
motion.stop()

# Or you can do the same with duration parameter:
motion.forward(10000, durationMs=1000)  # Move at speed 10000 for 1 second. This will block until the specified duration has passed

# Go backward at speed 5000 for 2 seconds
motion.forward(-5000, durationMs=2000) # Move backward at speed 5000 for 2 seconds

# Turn 90 degrees to the right at speed 5000
motion.turn(90, speed=5000) # This is non-blocking, it will start turning and return immediately. You can check if the turn is completed with isTurning() method or block until it's done with blocking=True parameter
while motion.isTurning():
  time.sleep_ms(10)

# Turn 90 degrees to the right at max speed, blocking until the turn is completed
motion.turn(90, blocking=True) # This will block until the turn is completed. You can also specify speed parameter if you don't want to turn at max speed