#include <WiFi.h>
#include <Preferences.h>
#include <TFT_eSPI.h>

#define SCR_WD 240
#define SCR_HT 240

TFT_eSPI lcd = TFT_eSPI();
Preferences preferences;

WiFiServer server(80);  // Create a TCP server on port 80
WiFiClient client;

void setup() {
  Serial.begin(115200);  // Serial communication for debugging
  
  // Initialize preferences
  preferences.begin("wifi-creds", false);
  
  // Retrieve stored SSID and password
  String ssid = preferences.getString("ssid", "");
  String password = preferences.getString("password", "");
  
  // Attempt Wi-Fi connection with stored credentials
  if (ssid.length() > 0) {
    Serial.println("Connecting to stored Wi-Fi...");
    WiFi.begin(ssid.c_str(), password.c_str());
  }

  // Wait for connection
  unsigned long startAttemptTime = millis();
  while (WiFi.status() != WL_CONNECTED && millis() - startAttemptTime < 10000) {
    delay(500);
    Serial.print(".");
  }
  Serial.println();

  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("Failed to connect to Wi-Fi. Enter new credentials:");
    enterNewCredentials();
  } else {
    Serial.println("Connected to Wi-Fi");
    Serial.print("ESP32 IP Address: ");
    Serial.println(WiFi.localIP());
  }

  server.begin();  // Start the TCP server

  lcd.init();
  lcd.setRotation(0);
  lcd.fillScreen(TFT_BLACK);
  lcd.drawRect(0, 0, 240, 240, TFT_YELLOW);
  lcd.setTextColor(TFT_WHITE);
  lcd.setTextSize(2);
  lcd.setCursor(24, 100);
  lcd.println("WAITING FOR DATA");
  lcd.setTextColor(TFT_GREEN);
  lcd.setCursor(34, 120);
  lcd.println(WiFi.localIP());
}

void loop() {
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();
    if (command == "SET_WIFI") {
      Serial.println("Enter new Wi-Fi credentials.");
      enterNewCredentials();
    }
  }

  if (!client.connected()) {
    client = server.available();  // Listen for incoming clients
    if (client) {
      Serial.println("Client connected");
      process_bmp();
    }
  }
}

// Function to read new Wi-Fi credentials from serial
void enterNewCredentials() {
  String newSSID;
  String newPassword;
  
  // Prompt and wait for SSID input
  while (newSSID.length() == 0) {
    Serial.print("Enter SSID: ");
    while (Serial.available() == 0) {
      delay(100);
    }
    newSSID = Serial.readStringUntil('\n');
    newSSID.trim();
  }
  
  // Prompt and wait for Password input
  while (newPassword.length() == 0) {
    Serial.print("Enter Password: ");
    while (Serial.available() == 0) {
      delay(100);
    }
    newPassword = Serial.readStringUntil('\n');
    newPassword.trim();
  }

  // Save credentials
  preferences.putString("ssid", newSSID);
  preferences.putString("password", newPassword);
  
  // Attempt to connect with new credentials
  Serial.println("Trying to connect with new credentials...");
  WiFi.disconnect();  // Ensure no lingering connection attempts
  WiFi.begin(newSSID.c_str(), newPassword.c_str());
  
  unsigned long startAttemptTime = millis();
  while (WiFi.status() != WL_CONNECTED && millis() - startAttemptTime < 10000) {
    delay(500);
    Serial.print(".");
  }
  Serial.println();

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("Connected to Wi-Fi");
    Serial.print("ESP32 IP Address: ");
    Serial.println(WiFi.localIP());
    updateDisplayWithIP();
  } else {
    Serial.println("Failed to connect with new credentials.");
  }
}

// Function to update display with new IP
void updateDisplayWithIP() {
  lcd.fillScreen(TFT_BLACK);
  lcd.drawRect(0, 0, SCR_WD, SCR_HT, TFT_YELLOW);
  lcd.setTextColor(TFT_WHITE);
  lcd.setTextSize(2);
  lcd.setCursor(24, 100);
  lcd.println("WAITING FOR DATA");
  lcd.setTextColor(TFT_GREEN);
  lcd.setCursor(34, 120);
  lcd.println(WiFi.localIP());
}

// Function to process BMP data from client
void process_bmp() {
  int i = 0, j = 239;
  uint8_t r, g, b;
  int header = 54;
  unsigned long ms;
  char buf[30];

  unsigned long start_time = millis();

  // Read and discard the BMP header (first 54 bytes)
  while (header > 0) {
    while (client.available() > 0 && header > 0) {
      client.read();
      header--;
    }
  }

  // Process pixel data
  while (client.available() > 0) {
    b = client.read();
    g = client.read();
    r = client.read();

    // Draw pixel
    lcd.drawPixel(i, j, lcd.color565(r, g, b));
    i++;
    if (i >= 240) {
      i = 0;
      j--;
      if (j < 0) {
        j = 239;
        snprintf(buf, 30, " Upload time: %d s ", (millis() - start_time) / 1000);
        client.println(buf);  // Sending data back to the client
      }
    }
  }

  // Disconnect client after processing
  client.stop();
  Serial.println("Client disconnected");
}
