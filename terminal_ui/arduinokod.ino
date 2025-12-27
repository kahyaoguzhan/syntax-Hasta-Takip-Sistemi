// =====================================================
// Arduino Uno Multi-System Control via Serial Commands + I2C LCD
// =====================================================
// Project: Finalized Integrated System Control with LCD Display
// Platform: Arduino Uno
// Date: December 2025
// 
// SYSTEM CONSTRAINTS:
// - System 1: Runs for 10 seconds (reads LDR, controls LED)
// - System 2: Runs for 10 seconds (measures distance, capped at 300mm)
// - System 3: Runs until 20 correct button presses (reaction time game)
// - All systems: Non-blocking timing with millis()
// - Returns to Listening Mode after completing task
// - LCD Display: I2C 16x2 with countdown and system-specific displays
// =====================================================

// =====================================================
// LIBRARY INCLUDES
// =====================================================
#include <LiquidCrystal_I2C.h>
#include <Wire.h>

// =====================================================
// LCD INITIALIZATION (I2C Address 0x27, 16x2 Layout)
// =====================================================
LiquidCrystal_I2C lcd(0x3F, 16, 2);  // Address 0x3F (try 0x27 if doesn't work)

// =====================================================
// PIN DEFINITIONS FOR SYSTEM 1
// =====================================================
const int LDR_PIN = A0;              // Analog pin for LDR (Light Dependent Resistor)
const int LED_PIN = 8;               // PWM digital pin for LED (Pin 3 supports PWM on Uno)

// =====================================================
// PIN DEFINITIONS FOR SYSTEM 2
// =====================================================
const int TRIG_PIN = 9;              // Digital pin for HC-SR04 Trig (Trigger)
const int ECHO_PIN = 10;             // Digital pin for HC-SR04 Echo (Pulse)
const int MAX_DISTANCE_MM = 300;     // Maximum distance to display (300mm = 30cm)

// =====================================================
// PIN DEFINITIONS FOR SYSTEM 3
// =====================================================
const int RED_PIN = 3;               // PWM pin for Red LED
const int GREEN_PIN = 6;             // PWM pin for Green LED
const int BLUE_PIN = 11;             // PWM pin for Blue LED
const int BUTTON_UP = 12;            // Button for Blue (Up)
const int BUTTON_DOWN = 7;           // Button for Green (Down)
const int BUTTON_RIGHT = 2;          // Button for Yellow/Red+Green (Right)
const int BUTTON_LEFT = 13;          // Button for Red (Left)
const int MAX_PRESSES = 20;          // Game ends after 20 correct presses

// =====================================================
// TIMING CONSTRAINTS
// =====================================================
const unsigned long SYSTEM_1_DURATION = 10000;    // 10 seconds in milliseconds
const unsigned long SYSTEM_2_DURATION = 10000;    // 10 seconds in milliseconds
const unsigned long SAMPLE_INTERVAL = 100;        // 100ms between sensor readings

// =====================================================
// VARIABLES FOR SYSTEM 1
// =====================================================
int currentLDRValue = 0;             // Stores current LDR reading
int mappedLEDBrightness = 0;         // Stores mapped brightness (0-255)
unsigned long system1StartTime = 0;  // When System 1 was activated
unsigned long lastReadTime = 0;      // Timestamp of last sensor reading

// =====================================================
// VARIABLES FOR SYSTEM 2
// =====================================================
unsigned long system2StartTime = 0;  // When System 2 was activated
unsigned long lastSystem2ReadTime = 0;     // Timestamp of last ultrasonic reading
long pulseDuration = 0;              // Duration of echo pulse in microseconds
float distanceInMM = 0;              // Calculated distance in millimeters

// =====================================================
// VARIABLES FOR SYSTEM 3 - Reaction Time Game
// =====================================================
int currentColor = 0;                // Current color (0=Blue, 1=Green, 2=Yellow, 3=Red)
unsigned long gameStartTime = 0;     // When the color was displayed
unsigned long reactionTime = 0;      // Measured reaction time in milliseconds
boolean gameActive = false;          // Is a color currently displayed?
int correctPressCount = 0;           // Counter for correct button presses
unsigned long lastRoundStartTime = 0;// Timestamp for non-blocking round delays
const int LED_BRIGHTNESS = 255;      // Full brightness for RGB LED
const unsigned long ROUND_DELAY = 500; // 500ms delay between rounds (non-blocking)
boolean buttonPressed = false;       // Flag to prevent multiple presses from one button hold

// =====================================================
// SYSTEM STATE VARIABLES
// =====================================================
char activeSystem = '0';             // Tracks which system is currently active ('0' = Listening, '1', '2', '3')
char countdownSystem = '0';          // System waiting for countdown (during countdown phase)
char incomingByte = 0;               // Stores incoming serial data
boolean system1Initialized = false;  // Flag to track System 1 initialization
boolean system2Initialized = false;  // Flag to track System 2 initialization
boolean system3Initialized = false;  // Flag to track System 3 initialization

// =====================================================
// FORWARD DECLARATIONS
// =====================================================
void displayListeningMode();
void displayColor(int colorCode);
void system1_Execute();
void system2_Execute();
void system3_Execute();

// =====================================================
// LCD & COUNTDOWN VARIABLES
// =====================================================
unsigned long countdownStartTime = 0;    // When countdown began
const unsigned long COUNTDOWN_INTERVAL = 1000;  // 1 second between countdown numbers
int countdownValue = 3;              // Current countdown number (3, 2, 1)
boolean countdownActive = false;     // Is countdown currently running?
boolean listeningModeDisplayed = false; // Flag to display listening mode only once

// =====================================================
// SETUP FUNCTION - Runs once at startup
// =====================================================
void setup() {
  // Initialize Serial communication at 9600 baud rate
  Serial.begin(9600);
  delay(100);  // Give Serial time to initialize
  
  // Initialize I2C communication
  Wire.begin();
  delay(500);
  
  // Initialize LCD display (I2C) with proper delay
  delay(500);
  
  lcd.begin(16, 2);
  delay(500);
  
  lcd.backlight();
  delay(200);
  
  lcd.clear();
  delay(200);
  
  lcd.setCursor(0, 0);
  lcd.print("System Start");
  delay(1000);
  lcd.clear();
  
  // Configure pin modes for System 1
  pinMode(LDR_PIN, INPUT);           // LDR as input (analog)
  pinMode(LED_PIN, OUTPUT);          // LED as output (PWM)
  analogWrite(LED_PIN, 0);           // Initial LED state: OFF
  
  // Configure pin modes for System 2
  pinMode(TRIG_PIN, OUTPUT);         // Ultrasonic Trig as output
  pinMode(ECHO_PIN, INPUT);          // Ultrasonic Echo as input
  
  // Configure pin modes for System 3 - RGB LED
  pinMode(RED_PIN, OUTPUT);          // Red LED as output (PWM)
  pinMode(GREEN_PIN, OUTPUT);        // Green LED as output (PWM)
  pinMode(BLUE_PIN, OUTPUT);         // Blue LED as output (PWM)
  
  // Configure pin modes for System 3 - Pushbuttons (using INPUT_PULLUP)
  pinMode(BUTTON_UP, INPUT_PULLUP);     // Button 1 - Blue (Up)
  pinMode(BUTTON_DOWN, INPUT_PULLUP);   // Button 2 - Green (Down)
  pinMode(BUTTON_RIGHT, INPUT_PULLUP);  // Button 3 - Yellow (Right)
  pinMode(BUTTON_LEFT, INPUT_PULLUP);   // Button 4 - Red (Left)
  
  // Initialize all RGB LEDs to OFF
  analogWrite(RED_PIN, 0);
  analogWrite(GREEN_PIN, 0);
  analogWrite(BLUE_PIN, 0);
  
  // Initialize random number generator with seed from analog pin
  // This ensures different random sequences each time Arduino is powered on
  randomSeed(analogRead(A1));        // Use A1 (unused analog pin) for random seed
  
  // Welcome message on Serial
  Serial.println("====================================");
  Serial.println("Arduino Multi-System Control Ready");
  Serial.println("====================================");
  Serial.println("Send commands via Serial Monitor:");
  Serial.println("'1' - Activate System 1 (LDR-LED)");
  Serial.println("'2' - Activate System 2 (Distance)");
  Serial.println("'3' - Activate System 3 (Game)");
  Serial.println("====================================");
  
  // Display welcome on LCD
  displayListeningMode();
}

// =====================================================
// MAIN LOOP - Runs continuously
// =====================================================
void loop() {
  // Check for incoming Serial commands (non-blocking)
  if (Serial.available() > 0) {
    char command = Serial.read();    // Read incoming byte

    // Process the command only if in Listening Mode
    if (activeSystem == '0') {
      switch (command) {
        case '1':
          countdownSystem = '1';
          countdownActive = true;
          countdownStartTime = millis();
          countdownValue = 3;
          activeSystem = '0';  // Stay in listening mode during countdown
          Serial.println("\n>>> Countdown Starting for System 1 <<<");
          break;
   
        case '2':
          countdownSystem = '2';
          countdownActive = true;
          countdownStartTime = millis();
          countdownValue = 3;
          activeSystem = '0';  // Stay in listening mode during countdown
          Serial.println("\n>>> Countdown Starting for System 2 <<<");
          break;

        case '3':
          countdownSystem = '3';
          countdownActive = true;
          countdownStartTime = millis();
          countdownValue = 3;
          activeSystem = '0';  // Stay in listening mode during countdown
          Serial.println("\n>>> Countdown Starting for System 3 <<<");
          break;
          
        default:
          // Invalid command
          if (command != '\n' && command != '\r') {
            Serial.print("Invalid command: '");
            Serial.print((char)command);
            Serial.println("'. Use '1', '2', or '3'.");
          }
          break;
      }
    }
  }
  
  // COUNTDOWN LOGIC - Non-blocking countdown execution
  if (countdownActive) {
    unsigned long currentTime = millis();
    unsigned long countdownElapsed = currentTime - countdownStartTime;
    
    // Check if it's time to update the countdown
    if (countdownElapsed >= (unsigned long)(4 - countdownValue) * COUNTDOWN_INTERVAL) {
      if (countdownValue > 1) {
        // Display countdown number
        lcd.clear();
        lcd.setCursor(7, 0);
        lcd.print(countdownValue);
        Serial.print(countdownValue);
        Serial.println("...");
        countdownValue--;
      } else if (countdownValue == 1) {
        // Display final "1"
        lcd.clear();
        lcd.setCursor(7, 0);
        lcd.print("1");
        Serial.println("1...");
        countdownValue--;
      } else {
        // Countdown finished - activate the system
        countdownActive = false;
        activeSystem = countdownSystem;
        countdownSystem = '0';
        
        // Display system start message
        lcd.clear();
        lcd.print("SYSTEM ");
        lcd.print(activeSystem);
        lcd.print(" START!");
        Serial.print("\n>>> SYSTEM ");
        Serial.print(activeSystem);
        Serial.println(" STARTING <<<");
        
        // Initialize the system
        switch(activeSystem) {
          case '1':
            system1Initialized = false;
            system1StartTime = millis();
            Serial.println("LDR Reading (10 second duration)");
            Serial.println("=====================================");
            break;
          case '2':
            system2Initialized = false;
            system2StartTime = millis();
            Serial.println("Distance Measurement (10 second duration, max 300mm)");
            Serial.println("=====================================");
            break;
          case '3':
            system3Initialized = false;
            gameActive = false;
            correctPressCount = 0;
            buttonPressed = false;
            lastRoundStartTime = 0;
            analogWrite(RED_PIN, 0);
            analogWrite(GREEN_PIN, 0);
            analogWrite(BLUE_PIN, 0);
            Serial.println("Reaction Time Game (20 button presses to complete)");
            Serial.println("=====================================");
            break;
        }
        
        delay(1000);  // Brief pause to show start message
      }
    }
    return;  // Skip system execution during countdown
  }
  
  // Execute the active system logic
  switch (activeSystem) {
    case '1':
      system1_Execute();
      break;
      
    case '2':
      system2_Execute();
      break;
      
    case '3':
      system3_Execute();
      break;
      
    default:
      // Listening Mode - no system active
      displayListeningMode();
      break;
  }
}

// =====================================================
// SYSTEM 1 IMPLEMENTATION - LDR-LED Control
// =====================================================
void system1_Execute() {
  // Get current time in milliseconds
  unsigned long currentTime = millis();
  unsigned long elapsedTime = currentTime - system1StartTime;
  unsigned long remainingTime = (elapsedTime >= SYSTEM_1_DURATION) ? 0 : (SYSTEM_1_DURATION - elapsedTime);
  
  // CHECK IF SYSTEM 1 DURATION LIMIT REACHED (10 seconds)
  if (elapsedTime >= SYSTEM_1_DURATION) {
    // System 1 has completed - return to Listening Mode
    analogWrite(LED_PIN, 0);  // Turn off LED
    Serial.println("--------------------------------------");
    Serial.println(">>> System 1 Finished (10 seconds elapsed) <<<");
    Serial.println(">>> LISTENING MODE <<<");
    Serial.println("Send '1', '2', or '3' to activate a system");
    Serial.println("====================================\n");
    
    // Display finished on LCD
    lcd.clear();
    lcd.print("FINISHED!");
    delay(1500);
    displayListeningMode();
    
    activeSystem = '0';  // Return to Listening Mode
    system1Initialized = false;  // Reset for next activation
    lastReadTime = 0;  // Reset timing variables
    listeningModeDisplayed = false;  // Reset LCD display flag
    return;
  }
  
  // Print initialization message once per activation
  if (!system1Initialized) {
    system1Initialized = true;
    lastReadTime = currentTime;  // Initialize reading timer
  }
  
  // Check if it's time for the next sensor reading
  if (currentTime - lastReadTime >= SAMPLE_INTERVAL) {
    // Update the last read time
    lastReadTime = currentTime;
    
    // ===== STEP 1: Read LDR Value =====
    // Read analog value from LDR (0-1023 for 10-bit ADC)
    currentLDRValue = analogRead(LDR_PIN);
    
    // ===== STEP 2: Map LDR Value to LED Brightness =====
    // Map the LDR value (0-1023) to PWM brightness (0-255)
    mappedLEDBrightness = map(currentLDRValue, 0, 1023, 0, 255);
    
    // ===== STEP 3: Apply Brightness to LED =====
    // Use PWM to set LED brightness
    analogWrite(LED_PIN, mappedLEDBrightness);
    
    // ===== STEP 4: Update LCD Display =====
    lcd.clear();
    lcd.print("LDR:");
    lcd.print(currentLDRValue);
    lcd.setCursor(0, 1);
    lcd.print("Time:");
    lcd.print(remainingTime / 1000);
    lcd.print("s");
    
    // ===== STEP 5: Print Data to Serial Monitor =====
    Serial.print(elapsedTime);
    Serial.print(" ms     | ");
    Serial.print(currentLDRValue);
    Serial.print("      | ");
    Serial.println(mappedLEDBrightness);
  }
}

// =====================================================
// SYSTEM 2 IMPLEMENTATION - HC-SR04 Ultrasonic Sensor
// =====================================================
void system2_Execute() {
  // Get current time in milliseconds
  unsigned long currentTime = millis();
  unsigned long elapsedTime = currentTime - system2StartTime;
  unsigned long remainingTime = (elapsedTime >= SYSTEM_2_DURATION) ? 0 : (SYSTEM_2_DURATION - elapsedTime);
  
  // CHECK IF SYSTEM 2 DURATION LIMIT REACHED (10 seconds)
  if (elapsedTime >= SYSTEM_2_DURATION) {
    // System 2 has completed - return to Listening Mode
    Serial.println("------------------------------");
    Serial.println(">>> System 2 Finished (10 seconds elapsed) <<<");
    Serial.println(">>> LISTENING MODE <<<");
    Serial.println("Send '1', '2', or '3' to activate a system");
    Serial.println("====================================\n");
    
    // Display finished on LCD
    lcd.clear();
    lcd.print("FINISHED!");
    delay(1500);
    displayListeningMode();
    
    activeSystem = '0';  // Return to Listening Mode
    system2Initialized = false;  // Reset for next activation
    lastSystem2ReadTime = 0;  // Reset timing variables
    listeningModeDisplayed = false;  // Reset LCD display flag
    return;
  }
  
  // Print initialization message once per activation
  if (!system2Initialized) {
    system2Initialized = true;
    lastSystem2ReadTime = currentTime;  // Initialize timing
  }
  
  // Check if it's time for the next sensor reading (100ms interval)
  if (currentTime - lastSystem2ReadTime >= SAMPLE_INTERVAL) {
    // Update the last read time
    lastSystem2ReadTime = currentTime;
    
    // ===== STEP 1: Generate Trigger Pulse =====
    // HC-SR04 requires a 10µs trigger pulse on the Trig pin
    digitalWrite(TRIG_PIN, LOW);
    delayMicroseconds(2);            // Short low pulse
    digitalWrite(TRIG_PIN, HIGH);
    delayMicroseconds(10);           // 10µs high pulse
    digitalWrite(TRIG_PIN, LOW);     // End trigger pulse
    
    // ===== STEP 2: Measure Echo Pulse Duration =====
    // pulseIn() measures the duration of the echo pulse
    // Timeout of 23200µs corresponds to ~4 meters
    pulseDuration = pulseIn(ECHO_PIN, HIGH, 23200);
    
    // ===== STEP 3: Calculate Distance in Millimeters =====
    // Speed of sound: 343 m/s = 0.343 mm/µs
    // Distance = (pulseDuration * speed) / 2
    // The division by 2 is because sound travels to object and back
    // Formula: distance(mm) = (pulseDuration * 0.343) / 2
    // Simplified: distance(mm) = pulseDuration * 0.1715
    distanceInMM = (pulseDuration * 0.343) / 2.0;
    
    // ===== STEP 4: Cap Distance at 300mm =====
    // Limit output to 300mm maximum
    if (distanceInMM > MAX_DISTANCE_MM) {
      distanceInMM = MAX_DISTANCE_MM;
    }
    
    // ===== STEP 5: Update LCD Display =====
    lcd.clear();
    lcd.print("Dist:");
    lcd.print(distanceInMM, 0);
    lcd.print("mm");
    lcd.setCursor(0, 1);
    lcd.print("Time:");
    lcd.print(remainingTime / 1000);
    lcd.print("s");
    
    // ===== STEP 6: Print Data to Serial Monitor =====
    // Format: Elapsed Time (ms) | Distance (mm)
    Serial.print(elapsedTime);
    Serial.print(" ms | ");
    Serial.print(distanceInMM, 1);   // Print with 1 decimal place for precision
    Serial.println(" mm");
  }
  
  // Note: No blocking delay() used - system remains responsive to Serial commands
}

// =====================================================
// SYSTEM 3 IMPLEMENTATION - Reaction Time Game
// =====================================================
void system3_Execute() {
  unsigned long currentTime = millis();
  
  // Print initialization message once per activation
  if (!system3Initialized) {
    system3Initialized = true;
    correctPressCount = 0;  // Initialize press counter
    lastRoundStartTime = 0;  // Reset round timing
    Serial.println("Starting game... Watch for colors!");
  }
  
  // Check button inputs (non-blocking) - INPUT_PULLUP makes LOW when pressed
  boolean buttonUp = !digitalRead(BUTTON_UP);      // Button 1 - Blue
  boolean buttonDown = !digitalRead(BUTTON_DOWN);  // Button 2 - Green
  boolean buttonRight = !digitalRead(BUTTON_RIGHT);// Button 3 - Yellow
  boolean buttonLeft = !digitalRead(BUTTON_LEFT);  // Button 4 - Red
  
  // Check if any button is currently pressed
  boolean anyButtonPressed = (buttonUp || buttonDown || buttonRight || buttonLeft);
  
  // CHECK IF GAME COMPLETION REACHED (20 correct presses)
  if (correctPressCount >= MAX_PRESSES) {
    // Game completed - return to Listening Mode
    analogWrite(RED_PIN, 0);
    analogWrite(GREEN_PIN, 0);
    analogWrite(BLUE_PIN, 0);
    Serial.println("=====================================");
    Serial.print(">>> GAME OVER! Total ");
    Serial.print(correctPressCount);
    Serial.println(" correct presses completed! <<<");
    Serial.println(">>> LISTENING MODE <<<");
    Serial.println("Send '1', '2', or '3' to activate a system");
    Serial.println("====================================\n");
    
    // Display finished on LCD
    lcd.clear();
    lcd.print("FINISHED!");
    delay(1500);
    displayListeningMode();
    
    activeSystem = '0';  // Return to Listening Mode
    system3Initialized = false;  // Reset for next activation
    buttonPressed = false;  // Reset button flag
    lastRoundStartTime = 0;  // Reset round timing
    listeningModeDisplayed = false;  // Reset LCD display flag
    return;
  }
  
  // If no game is active, start a new round (non-blocking delay)
  if (!gameActive) {
    // Wait ROUND_DELAY before showing new color
    if (lastRoundStartTime == 0 || (currentTime - lastRoundStartTime >= ROUND_DELAY)) {
      currentColor = random(4);         // Pick random color (0-3)
      displayColor(currentColor);       // Light up the RGB LED
      gameStartTime = millis();         // Start timer
      gameActive = true;
      lastRoundStartTime = currentTime;
      
      // Update LCD for new round
      lcd.clear();
      lcd.print("Press:");
      lcd.print(correctPressCount + 1);
      lcd.print("/20");
      lcd.setCursor(0, 1);
      lcd.print("Ready!");
      Serial.print("Round ");
      Serial.print(correctPressCount + 1);
      Serial.println(": Color displayed. Press the matching button!");
    }
  }
  
  // Check if correct button was pressed with debouncing
  if (gameActive && anyButtonPressed && !buttonPressed) {
    // Button just pressed (not held) - debouncing activated
    buttonPressed = true;  // Set flag to prevent multiple counts
    
    boolean correctPress = false;
    
    // Check for correct button press based on current color
    if (currentColor == 0 && buttonUp) {
      correctPress = true;           // Blue color + Button Up = Correct
    } else if (currentColor == 1 && buttonDown) {
      correctPress = true;           // Green color + Button Down = Correct
    } else if (currentColor == 2 && buttonRight) {
      correctPress = true;           // Yellow color + Button Right = Correct
    } else if (currentColor == 3 && buttonLeft) {
      correctPress = true;           // Red color + Button Left = Correct
    }
    
    // If correct button was pressed
    if (correctPress) {
      reactionTime = millis() - gameStartTime;
      correctPressCount++;  // Increment correct press counter
      
      Serial.print("Correct! Reaction Time: ");
      Serial.print(reactionTime);
      Serial.print(" ms | Presses: ");
      Serial.print(correctPressCount);
      Serial.println("/20");
      
      // Update LCD with result
      lcd.clear();
      lcd.print("CORRECT!");
      lcd.setCursor(0, 1);
      lcd.print(reactionTime);
      lcd.print("ms ");
      lcd.print(correctPressCount);
      lcd.print("/20");
      
      // Turn off RGB LED
      analogWrite(RED_PIN, 0);
      analogWrite(GREEN_PIN, 0);
      analogWrite(BLUE_PIN, 0);
      
      gameActive = false;  // Ready for next round
      lastRoundStartTime = currentTime;  // Start round delay
    } 
    else {
      // Wrong button pressed
      Serial.println("Wrong button! Try again.");
    }
  }
  
  // Reset button flag when button is released (all buttons released)
  if (!anyButtonPressed && buttonPressed) {
    buttonPressed = false;  // Button released
  }
}

// =====================================================
// HELPER FUNCTION - Display Color on RGB LED
// =====================================================
void displayColor(int colorCode) {
  // Turn off all LEDs first
  analogWrite(RED_PIN, 0);
  analogWrite(GREEN_PIN, 0);
  analogWrite(BLUE_PIN, 0);
  
  // Display selected color based on color code
  switch(colorCode) {
    case 0:  // Blue
      Serial.println("[BLUE]");
      lcd.clear();
      lcd.setCursor(6, 0);
      lcd.print("BLUE");
      analogWrite(BLUE_PIN, LED_BRIGHTNESS);
      break;
    
    case 1:  // Green
      Serial.println("[GREEN]");
      lcd.clear();
      lcd.setCursor(6, 0);
      lcd.print("GREEN");
      analogWrite(GREEN_PIN, LED_BRIGHTNESS);
      break;
    
    case 2:  // Yellow (Red + Green)
      Serial.println("[YELLOW]");
      lcd.clear();
      lcd.setCursor(5, 0);
      lcd.print("YELLOW");
      analogWrite(RED_PIN, LED_BRIGHTNESS);
      analogWrite(GREEN_PIN, LED_BRIGHTNESS);
      break;
    
    case 3:  // Red
      Serial.println("[RED]");
      lcd.clear();
      lcd.setCursor(7, 0);
      lcd.print("RED");
      analogWrite(RED_PIN, LED_BRIGHTNESS);
      break;
  }
}

// =====================================================
// HELPER FUNCTION - Display Listening Mode on LCD
// =====================================================
void displayListeningMode() {
  // Only update LCD once when entering listening mode
  if (!listeningModeDisplayed) {
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Waiting Command");
    lcd.setCursor(0, 1);
    lcd.print("Select 1,2 or 3");
    listeningModeDisplayed = true;
  }
}

// =====================================================
// END OF CODE
// =====================================================