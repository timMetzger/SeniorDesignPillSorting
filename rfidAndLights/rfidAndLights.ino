#include <Adafruit_NeoPixel.h>


#define PIN 3
#define LEDS 23

#define holdPin 12
#define abortPin 13

// LED Strip
Adafruit_NeoPixel strip = Adafruit_NeoPixel(LEDS,PIN,NEO_GRB + NEO_KHZ800);

// Variable to store information from serial
String incomingString;
int lightPos;
int blinkCount;




void setup() {
  Serial.begin(115200);
  
  strip.begin();
  strip.show();

  pinMode(holdPin, OUTPUT);
  pinMode(abortPin, OUTPUT);
}

void loop() {
  if (Serial.available() > 0){
    incomingString = Serial.readString();

    // If moving to a new position turn corresponding light on
    if (incomingString.startsWith("P")){
        strip.clear();
        lightPos = incomingString.substring(1).toInt();
        strip.setPixelColor(lightPos,0,0,255);
        strip.show();
      }

    // Handle lights for start sequence
    else if(incomingString.equals("start")){
        strip.clear();
        strip.fill(strip.Color(255,0,0),0,LEDS);
        strip.show();
      }

    // Handle lights for paused sequence
    else if(incomingString.equals("hold")){
        strip.clear();
        strip.fill(strip.Color(255,255,0),0,LEDS);
        strip.show();

        digitalWrite(holdPin,HIGH);
      }

    else if(incomingString.equals("resume")){
        strip.clear();
        strip.fill(strip.Color(0,255,0),0,LEDS);
        strip.show();
        digitalWrite(holdPin,LOW);
      }

    // Handle lights for abort
    else if(incomingString.equals("abort")){
        strip.clear();
        strip.fill(strip.Color(0,255,0),0,LEDS);
        strip.show();
        
        digitalWrite(abortPin,HIGH);
      }

    else if(incomingString.equals("done")){
      blinkCount = 0;
      while(blinkCount < 5){
          strip.clear();
          strip.rainbow(0,1,255,255,true);
          strip.show();
          delay(1000);
          strip.clear();
          strip.show();
          delay(250);
          blinkCount += 1;
        }
      }

    // Handle rfid scan
    else if(incomingString.equals("scan")){
        Serial.print("scanning");
      }
    }
  
}
