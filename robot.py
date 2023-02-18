import math
import time
import sys

import wpilib
import wpilib.drive
import ctre 
import navx

import ntcore 
import logging 
import cscore

import math

#from networktables import NetworkTables

# HARDWARE DEF

#from wpilib.drive import DifferentialDrive

#logging.basicConfig(level=logging.DEBUG)

#GLOBAL DEF
minTX = -1
maxTX = 1

#Distance equation
def targetDistance(x):
        a = 4.509
        b = -0.5132
        distance = 0
        if x > 0:
            distance = a * x ** b
        else:
            pass
        return distance

def targetAlignment(x):
    isTargetAligned = ''
    if (minTX <= x <= maxTX):
        #print("Aligned")
        isTargetAligned = 'Aligned'
    else:
        #print("unaligned")
        isTargetAligned = 'Unaligned'
    return isTargetAligned

def armExtension(x):
    runningTotal = 0
    avgFactor = 75
    for y in range(avgFactor):
        distance = 28250 / (x-229.5)
        runningTotal = runningTotal + distance
    else:
        distance = (runningTotal + distance)
    return distance

def solenoidclaw(x):
    isSolenoidClawOpen = ''
    if (x==1):
        #print ("Claw Open")
        isSolenoidClawOpen = 'Open'
    else:
        #print ("Claw Close")
        isSolenoidClawOpen = 'Close'
    return isSolenoidClawOpen

class MyRobot(wpilib.TimedRobot):
    def robotInit(self):
        """Robot initialization function"""

        # object that handles basic drive operations
        # Check for the right motor definition (Talon or other)
        
        '''
        self.frontLeftMotor = wpilib.Talon(0)
        self.rearLeftMotor = wpilib.Talon(1)
        self.frontRightMotor = wpilib.Talon(15)
        self.rearRightMotor = wpilib.Talon(14)
        '''
        # Phoenix Tuner
        # PID 1: Right Back; PID 2: Right Front; PID 14: Left Front; PID 15: Left Back; PID 0: PDP
        ''' 
        self.frontLeftMotor = wpilib.Talon(15)
        self.rearLeftMotor = wpilib.Talon(14)
        self.frontRightMotor = wpilib.Talon(2)
        self.rearRightMotor = wpilib.Talon(1)
        '''
        
        self.frontLeftMotor = ctre.WPI_TalonSRX(0)
        #self.frontLeftMotor.set(0.3)
        self.rearLeftMotor = ctre.WPI_TalonSRX(1)
        #self.rearLeftMotor.set(0.3)
        self.frontRightMotor = ctre.WPI_TalonSRX(15)
        #self.frontRightMotor.set(0.3)
        self.rearRightMotor = ctre.WPI_TalonSRX(14)
        #self.rearRightMotor.set(0.3)
        '''
        self.frontLeftMotor = ctre.WPI_TalonSRX(0)
        #self.frontLeftMotor.set(0.3)
        self.rearLeftMotor = ctre.WPI_TalonSRX(1)
        #self.rearLeftMotor.set(0.3)
        self.frontRightMotor = ctre.WPI_TalonSRX(15)
        #self.frontRightMotor.set(0.3)
        self.rearRightMotor = ctre.WPI_TalonSRX(14)
        #self.rearRightMotor.set(0.3)
        '''
        self.m_left = wpilib.MotorControllerGroup(self.frontLeftMotor, self.rearLeftMotor)
        self.m_right = wpilib.MotorControllerGroup(self.frontRightMotor, self.rearRightMotor)
        
        self.m_left.setInverted(True)

        #self.myRobot = DifferentialDrive(self.left, self.right)
        #self.myRobot.setExpiration(0.1)
        
        #self.myRobot = wpilib.drive.DifferentialDrive(self.left, self.right)
        self.driveTrain = wpilib.drive.DifferentialDrive(self.m_left, self.m_right)
        self.driveTrain.setExpiration(0.1)
        #self.myRobot.setExpiration(0.1)

        # joysticks 1 & 2 on the driver station
        self.joystick = wpilib.Joystick(0)
        self.controller = wpilib.Joystick(1)
        #self.rightStick = wpilib.Joystick(1)
        self.timer = wpilib.Timer()

         ## SOLENOID TESTING
        self.doubleSolenoid = wpilib.DoubleSolenoid(3,wpilib.PneumaticsModuleType.CTREPCM, 1,2)
        kForward = 1
        kOff = 0
        kReverse = 2
        
        ## DEFINE COMPRESSOR
        self.compressor = wpilib.Compressor(3,wpilib.PneumaticsModuleType.CTREPCM)
        
        ## ENCODER DEFINITION
        
        # Encoder Testing
        self.kTimeoutMs = 0
        self.kPIDLoopIdx = 0
        self.kSlotIdx = 0
        #self.rearRightMotor.configSelectedFeedbackSensor(ctre.FeedbackDevice.PulseWidthEncodedPosition, 0, 0)
        #self.rearRightMotor.configSelectedFeedbackSensor(ctre.FeedbackDevice.QuadEncoder, 0, 0)
        #self.rearRightMotor.configSelectedFeedbackSensor(ctre.FeedbackDevice.CTRE_MagEncoder_Relative, 0, 0)
        #self.rearRightMotor.configSelectedFeedbackSensor(ctre.FeedbackDevice.CTRE_MagEncoder_Absolute, 0, 0)
        self.frontLeftMotor.configSelectedFeedbackSensor(ctre.FeedbackDevice.CTRE_MagEncoder_Absolute, 0, 0,)
        self.frontLeftMotor.setSensorPhase(True)
        self.frontLeftMotor.setSelectedSensorPosition(100,0,0)
        # Set relevant frame periods to be at least as fast as periodic rate
        ##self.rearRightMotor.setStatusFramePeriod(ctre.WPI_TalonSRX.StatusFrameEnhanced.Status_13_Base_PIDF0, 10, 0)
        ##self.rearRightMotor.setStatusFramePeriod(ctre.WPI_TalonSRX.StatusFrameEnhanced.Status_10_MotionMagic, 10, self.kTimeoutMs)

        # set the peak and nominal outputs
        self.frontLeftMotor.configNominalOutputForward(0, self.kTimeoutMs)
        self.frontLeftMotor.configNominalOutputReverse(0, self.kTimeoutMs)
        self.frontLeftMotor.configPeakOutputForward(1, self.kTimeoutMs)
        self.frontLeftMotor.configPeakOutputReverse(-1, self.kTimeoutMs)

        # set closed loop gains in slot0 - see documentation */
        self.frontLeftMotor.selectProfileSlot(self.kSlotIdx, self.kPIDLoopIdx)
        self.frontLeftMotor.config_kF(0, 0.2, self.kTimeoutMs)
        self.frontLeftMotor.config_kP(0, 0.2, self.kTimeoutMs)
        self.frontLeftMotor.config_kI(0, 0, self.kTimeoutMs)
        self.frontLeftMotor.config_kD(0, 0, self.kTimeoutMs)
        # set acceleration and vcruise velocity - see documentation
        self.frontLeftMotor.configMotionCruiseVelocity(15000, self.kTimeoutMs)
        self.frontLeftMotor.configMotionAcceleration(6000, self.kTimeoutMs)
        # zero the sensor
        self.frontLeftMotor.setSelectedSensorPosition(0, self.kPIDLoopIdx, self.kTimeoutMs)

        
        ## NETWORK TABLES
        self.inst = ntcore.NetworkTableInstance.getDefault()
        #self.inst.startServer()
        #self.inst = ntcore.NetworkTableInstance.create()
        self.sd = self.inst.getTable("SmartDashboard")
        self.lmtable = self.inst.getTable("limelight")
        #self.lltable = ntcore.NetworkTableInstance
        
        ## DEFINE NAVX
        #self.navx = navx.AHRS.create_i2c(wpilib.I2C.Port.kMXP, update_rate_hz=80)
        self.navxer = navx.AHRS.create_i2c()
        print("NAVX firmware = ", navx.AHRS.getFirmwareVersion)
        #print("I2C device address is {}".format(wpilib.I2C.getDeviceAddress()))
        #print("I2C address only {}".format(wpilib.I2C.addressOnly()))
        
        ## DEFINE LIMELIGHT
        '''
        table = NetworkTables.getTable("limelight")
        tx = table.getNumber('tx', None)
        ty = table.getNumber('ty', None)
        ta = table.getNumber('ta', None)
        ts = table.getNumber('ts', None)
        '''
        '''
        self.tx = NetworkTable.getNumber('tx', None)
        self.ty = NetworkTable.getNumber('ty', None)
        self.ta = NetworkTable.getNumber('ta', None)
        self.ts = NetworkTable.getNumber('ts', None)
        '''
        #self.table = ntcore.NetworkTableInstance()
        #self.table1 = self.table.getTable('limelight')
        '''
        self.tx = self.lmtable.getNumber('tx', None)
        self.ty = self.lmtable.getNumber('ty', None)
        self.ta = self.lmtable.getNumber('ta', None)
        self.ts = self.lmtable.getNumber('ts', None)
        '''
        # Mr. Carlin's genius helped find this "da" moment, had to add the call to teleop
        
        """Executed at the start of teleop mode"""
        #self.myRobot.setSafetyEnabled(True)
        self.driveTrain.setSafetyEnabled(True)
        self.driveTrain.setSafetyEnabled(False)
        self.driveTrain.setExpiration(0.1)
        self.driveTrain.feed()
        # Launch Camera
        wpilib.CameraServer.launch()

        #ARM EXTENTION
        self.extension = wpilib.AnalogInput(3)

    def teleopPeriodic(self):
        """Runs the motors with tank steering"""
        #self.myRobot.tankDrive(self.leftStick.getY() * -1, self.rightStick.getY() * -1)
        i = 0
        #if i==0:
        #    print("In TeleopMode")
        #    i=i+1
        #self.driveTrain.arcadeDrive(-0.5, 0)
        #print("Driving")
        #time.sleep(1)
        #print("Sleep Complete")
        #self.driveTrain.arcadeDrive(0,0)
        #self.myRobot.arcadeDrive(
        #    self.stick.getRawAxis(0), self.stick.getRawAxis(1), True
        #)
        #print(self.joystick.getY())
        #print(self.joystick.getX())
        #print(self.joystick.getRawButtonPressed(1))
        
        #LIMELIGHT Variables
        
        self.tx = self.lmtable.getNumber('tx', None)
        self.ty = self.lmtable.getNumber('ty', None)
        self.ta = self.lmtable.getNumber('ta', None)
        self.ts = self.lmtable.getNumber('ts', None)
        self.displacement = self.navxer.getDisplacementX()
        self.angle = self.navxer.getAngle()
        self.yaw = self.navxer.getYaw()

        self.limelightLensHeightInches = 14

        #target distance to dashborard
        self.distance = targetDistance(self.ta)
        self.sd.putNumber('tDistance', self.distance)

        #target alignment pushing to dashboard
        self.aim = targetAlignment(self.tx)
        self.sd.putString('tAim', self.aim)

        #arm extension to dashboard
        self.reach = armExtension(self.distance)
        self.sd.putNumber('reach', self.reach)        

        if self.joystick.getRawButtonPressed(1):
            print("Button 1 Pressed")
            self.doubleSolenoid.set(wpilib.DoubleSolenoid.Value.kForward) #opens
            self.sd.putString(solenoidclaw(1)) #claw to dashboard
        if self.joystick.getRawButtonPressed(2):
            print("Button 2 Pressed")
            self.doubleSolenoid.set(wpilib.DoubleSolenoid.Value.kOff)
        if self.joystick.getRawButtonPressed(3):
            print("Button 3 Pressed")
            self.doubleSolenoid.set(wpilib.DoubleSolenoid.Value.kReverse) #closes
            self.sd.putString(solenoidclaw(3)) #claw to dashboard
        if self.joystick.getRawButtonPressed(4):
            print("Button 4 Pressed")
            #print("solenoid value = ",self.doubleSolenoid.get())
            # NAVX uses network tables as well 
            print("Displacement X = ", self.displacement)
            print("Yaw = ", self.yaw)  
            print("Angle = ", self.angle)   
        if self.joystick.getRawButtonPressed(5):
            print("Button 5 Pressed")
            '''
            print("CTRE PulseWidthEncoded Position := ", self.encoder.PulseWidthEncodedPosition.value)
            print("QuadEncoder = ", self.encoder.QuadEncoder.value)
            sensorreadout = self.rearRightMotor.getSensorCollection()
            print("Sensor Collection Analog In Raw = ", sensorreadout.getAnalogInRaw())
            print("Sensor Collection Pulse Width Pos = ", sensorreadout.getPulseWidthPosition())
            print("Sensor Collection Pulse Width Rise to Fall = ", sensorreadout.getPulseWidthRiseToFallUs())
            print("Sensor Collection QuadIdx = ", sensorreadout.getPinStateQuadIdx())
            print("Sensor Collection Pulse Width Velocity = ", sensorreadout.getPulseWidthVelocity())
            print("Sensor Collection Quad Position = ", sensorreadout.getQuadraturePosition())
            print("Sensor Collection Quad Velocity = ", sensorreadout.getQuadratureVelocity)
            '''
            # Encoder Testing
            print("Sensor Position", self.frontLeftMotor.getSelectedSensorPosition(0))
        if self.joystick.getRawButtonPressed(6):
            print("Button 6 Pressed")
            self.compressor.disable()
        if self.joystick.getRawButtonPressed(7):
            #Limelight
            print("Button 7 Pressed")
            print("Limelight ta = ", self.ta)
            print("Limelight ts = ", self.ts)
            print("Limelight ty = ", self.ty)
            print("Limelight tx = ", self.tx)
            
        self.driveTrain.arcadeDrive(-self.joystick.getY(), self.joystick.getX())
        
        #CONTROLLER BUTTONS
        if self.controller.getRawButtonPressed(1):
            print("Controller button 1 pressed")
            self.lmtable.putNumber('ledMode', 1)
        if self.controller.getRawButtonPressed(2):
            print("Controller button 2 pressed")
            self.lmtable.putNumber('ledMode', 3)
        if self.controller.getRawButtonPressed(3):
            print("Controller button 3 pressed")
            print("Setting to April Tag Mode")
            self.lmtable.putNumber('pipeline', 0)
        if self.controller.getRawButtonPressed(4):
            print("Controller button 4 pressed")
        if self.controller.getRawButtonPressed(5):
            print("Controller button 5 pressed")
            print("Setting to Peg Mode")
            self.lmtable.putNumber('pipeline', 1)
        if self.controller.getRawButtonPressed(6):
            print("Controller button 6 pressed")
            if (self.tx >= -1):
                print("Aligned")
            else:
                print("unaligned")
        if self.controller.getRawButtonPressed(7):
            print("Controller button 7 pressed")
            #print("extension_value", self.extension.getValue())
            armDistance = armExtension(self.extension.getValue())
            print("arm_extension = ", armDistance)
        if self.controller.getRawButtonPressed(8):
            print("Controller button 8 pressed")
        if self.controller.getRawButtonPressed(9):
            print("Controller button 9 pressed")
        if self.controller.getRawButtonPressed(10):
            print("Controller buttone 10 pressed")
        '''
        if self.tx == 0:
            print("Aligned")
        else:
            print("Unaligned")
        '''
    ''' TEST class MyRobot(wpilib.TimedRobot)
    def robotInit(self):
        self.frontLeft = wpilib.Spark(0)
        self.rearLeft = wpilib.Spark(1)
        self.left = wpilib.MotorControllerGroup(self.frontLeft, self.rearLeft)
        self.frontRight = wpilib.Spark(15)
        self.rearRight = wpilib.Spark(14)
        self.right = wpilib.MotorControllerGroup(self.frontRight, self.rearRight)
        self.drive = wpilib.drive.DifferentialDrive(self.left, self.right)
    '''
    def autonomousInit(self):
        """This function is run once each time the robot enters autonomous mode."""
        #self.driveTrain.setSafetyEnabled(True)
        self.driveTrain.setSafetyEnabled(False)
        self.driveTrain.setExpiration(0.1)
        self.driveTrain.feed()
        self.timer.reset()
        self.timer.start()

    def autonomousPeriodic(self):
        """This function is called periodically during autonomous."""
        '''
        print("Autonomous Mode")
        self.driveTrain.arcadeDrive(-0.5, 0)
        #print("Driving")
        time.sleep(1)
        #print("Sleep Complete")
        self.driveTrain.arcadeDrive(0,0)
        # Drive for two seconds
        '''
        i = 0
        if i==0:
            print("In Autonomous Mode")
            i=i+1
        #self.driveTrain.arcadeDrive(-0.5, 0)
        #time.sleep(0.5)
        #self.driveTrain.arcadeDrive(0, 0)
        
        if self.timer.get() < 2.0:
            self.driveTrain.arcadeDrive(-0.5, 0)  # Drive forwards at half speed
        else:
            self.driveTrain.arcadeDrive(0, 0)  # Stop robot
    
   
'''
    def teleopPeriodic(self):
        """This function is called periodically during operator control."""
        self.drive.arcadeDrive(self.stick.getY(), self.stick.getX())
'''

# MAIN LOOP

if __name__ == '__main__':
    print("Working")
    wpilib.run(MyRobot)
   
