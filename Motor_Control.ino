	#include <Wire.h>
	#include <Adafruit_MotorShield.h>
	#include utility/Adafruit_MS_PWMServoDriver.h
	
	// Create the motor shield object with the default I2C address
	Adafruit_MotorShield AFMS = Adafruit_MotorShield();
	// Connect pump to motor port #1 (M2)
	Adafruit_DCMotor *myPump = AFMS.getMotor(2);
	// Connect stepper to motor port #2 (M3 and M4)
	Adafruit_StepperMotor *myStepper = AFMS.getStepper(48, 2);
	// Connected stepper motor: 7.5 degrees/step => 48 steps/rev
	// Displacement = 0.0167mm/step => 10mm/598.8steps
	// 10mm/s = 748.5rpm
	
	void setup(){
	  Serial.begin(9600);
	  AFMS.begin();  // create with the default frequency 1.6KHz
	}
	
	// Takes given option code from Rpi (0-9) and determines what task to run
	void loop(){
	  if (Serial.available())  {
	     taskOption(int(Serial.read()) - '0');  // convert the character '0'-'9' to decimal 0-9
	  }
	  delay(500);
	}
	
	void taskOption(int peripheralCode){
	  int newCode = 0;
	
	  // *** INITIALISE SEQUENCE ***
	  if (peripheralCode == 0) {
	    myStepper->setSpeed(700);  // 700 rpm
	    Serial.println("Stepper motor returning to home position");
	    myStepper->step(800, BACKWARD, SINGLE);;
	    myStepper->release();
	    // Set the speed to start, from 0 (off) to 255 (max speed)
	    myPump->setSpeed(150);
	    myPump->run(FORWARD);
	    // turn on motor
	    myPump->run(RELEASE);
	  }
	
	
	  // *** DYNAMIC REST STATE ***
	  else if (peripheralCode == 1) {
	    myStepper->release();
	    Serial.println("Stepper Rest");
	    Serial.println(peripheralCode);
	  }
	
	  // *** DYNAMIC OPTION ***
	  else if (peripheralCode == 2) {
	    myStepper->setSpeed(748.5);  // 748.5 rpm
	    int stepCount;
	    Serial.println("Stepper motor will run until interrupted");
	    while (1) {
	      myStepper->step(1, FORWARD, SINGLE);
	      stepCount += 1;
	      newCode = int(Serial.read() - "0");
	      //-49 is value read when a character has not been written by the RPi
	      if (newCode != -49) {
	        myStepper->release();
	      break;
	      }
	    }
	    myStepper->step(stepCount, BACKWARD, SINGLE);;
	    Serial.println("Loop broken");
	    Serial.println(newCode);
	    taskOption(newCode);
	  }
	
	  // *** LINEAR OPTION 1 ***
	  else if (peripheralCode == 3) {
	      myStepper->setSpeed(748.5);  // 748.5 rpm
	      Serial.println("Stepper motor will now run 10mm at 1Hz");
	      myStepper->step(598, FORWARD, SINGLE);
	      myStepper->step(598, BACKWARD, SINGLE);;
	  }
	
	  // *** LINEAR OPTION 2 ***
	  else if (peripheralCode == 4) {
	      myStepper->setSpeed(748.5);
	      Serial.println("Stepper motor will now run 5mm at 0.5Hz");
	      myStepper->step(299, FORWARD, SINGLE);
	      myStepper->step(299, BACKWARD, SINGLE);;
	  }
	
	  // *** LINEAR OPTION 3 ***
	  else if (peripheralCode == 5) {
	      myStepper->setSpeed(748.5);
	      Serial.println("Stepper motor will now run 2.5mm at 0.25Hz");
	      myStepper->step(150, FORWARD, SINGLE);
	      myStepper->step(150, BACKWARD, SINGLE);;
	  }
	
	  // *** PUMP OPTION 1 ***
	  else if (peripheralCode == 6) {
	    Serial.print("Pump Option 1");
	    myPump->setSpeed(200);
	    myPump->run(FORWARD);
	  }
	
	  // *** PUMP OPTION 2 ***
	  else if (peripheralCode == 7) {
	    Serial.print("Pump Option 2");
	    myPump->setSpeed(150);
	    myPump->run(FORWARD);
	  }
	
	  // *** PUMP OPTION 3 ***
	  else if (peripheralCode == 8) {
	    Serial.print("Pump Option 3");
	    myPump->setSpeed(100);
	    myPump->run(FORWARD);
	  }
	
	  // *** REST STATE ***
	  else {
	    Serial.print("Pump Option 4");
	    myPump->run(RELEASE);
	    myStepper->release();
