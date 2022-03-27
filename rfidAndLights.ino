#include <Adafruit_NeoPixel.h>

#define PIN 2
#define LEDS 12

// LED Strip
Adafruit_NeoPixel strip = Adafruit_NeoPixel(LEDS,PIN,NEO_GRB + NEO_KHZ800);

// Variable to store information from serial
String incomingString;
int lightPos;

void setup() {
  Serial.begin(115200);
  strip.begin();
  strip.show();

}

void loop() {
  if (Serial.available() > 0){
    incomingString = Serial.readString();

    // If moving to a new position turn its light on
    if (incomingString.startsWith("P")){
          strip.clear();
          lightPos = incomingString.substring(1).toInt();
          strip.setPixelColor(lightPos,255,255,0);
          
    }
  }

}
