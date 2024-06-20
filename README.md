# BMP_WifiDisplay
This project is about sending bmp pixel data over wifi to 240x240 display. 

- Config your display at user setup of TFT_eSPI library
- Upload Code to ur esp32
- Config wifi via serial terminal
- If you want to change wifi, over serial terminal type SET_WIFI, and you are able to set new wifi. This maybe glitchy duo to my sketchy coding skill. Well at least I get this to work.

- This works on TFT Display ST7789 with or without cs pin

- WifiDisplay-wificonfig.ino is main arduino file for flashing esp32
- image_conv.py is tool for converting image to 240x240 24bit.
- SendPixel.py is for sending pixel data to display

- This way can send image to display faster than sending .bmp via serial :D 


NOTE: Both esp32 and host must be on the same network.
      Make sure to install all necessary library installed
