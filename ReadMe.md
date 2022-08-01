# Automated Pill Sorting
## What is this project 


https://user-images.githubusercontent.com/37784441/182250058-951c6865-d840-4d49-b33f-1fa5c6e0104d.mp4



This is a mechanical engineering project for a year-long senior design capstone course. The goal of this project is to take a patients prescribed medications and sort them by days of the week or times of day. To accomplish this there is a major software component utilizing C, Python, and QT widget library. Python and QT are used to create the GUI for the end user allowing control and tuning of the machine as well as generating GCode statements for an Ardunio Uno to interpret. If you want to know more check out the design report pdf. If you still have questions send me a message. 
## How does it work
The machine itself is inspired by a SCARRA robotic arm. A central sorting using two 12V stepper motors controls the location of an SMT pick and place head. When the machine has positioned itself over a pill slot a solenoid valve is activated creating suction at the tip of the SMT head allowing for the retrieval of a pill. This is the basics of how pills are retrieved from storage locations. Now, it is a bit more complicated than that as the machine needs code to understand what to do. This is where the Arduino Uno flashed with the GRBL gcode interpeter comes in. This means that the python program needs to generate the GCode statements for the Arduino to read and control the multiple servo motors.  

![Screenshot](https://github.com/timMetzger/SeniorDesignPillSorting/blob/master/Pictures/FINAL_CAD.png?raw=true)
![Screenshot](https://github.com/timMetzger/SeniorDesignPillSorting/blob/master/Pictures/Exploded_Head.png?raw=true)

## GUI

### Main Panel
The main panel is responsible for selecting a patient and indicating the medications required. When sorting is in process the program does so in a secondary thread to allow the user to remain in control. 

![Screenshot](https://github.com/timMetzger/SeniorDesignPillSorting/blob/master/Pictures/GUI_1.png?raw=true)
![Screenshot](https://github.com/timMetzger/SeniorDesignPillSorting/blob/master/Pictures/GUI_2.png?raw=true)
![Screenshot](https://github.com/timMetzger/SeniorDesignPillSorting/blob/master/Pictures/GUI_5.png?raw=true)
![Screenshot](https://github.com/timMetzger/SeniorDesignPillSorting/blob/master/Pictures/GUI_6.png?raw=true)

### Tuning Panel
The tuning panel allows for fine-tuning of the gcode interpreters settings 

![Screenshot](https://github.com/timMetzger/SeniorDesignPillSorting/blob/master/Pictures/GUI_3.png?raw=true)
### Direct Control Panel
The direct control panel allows for the direct control of the machine via relative and absolute means via the buttons. One may also input gcode statements directly. Additionally, there is a serial monitor reading out the status of the gcode interpreter. When utilizing this tool the serial output is monitored in a secondary thread so that the user does not lose control of the GUI. 

![Screenshot](https://github.com/timMetzger/SeniorDesignPillSorting/blob/master/Pictures/GUI_4.png?raw=true)

