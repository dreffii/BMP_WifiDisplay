import tkinter as tk
from tkinter import filedialog, messagebox, Entry
import socket
import struct
from PIL import Image, ImageTk
import time

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Send BMP to ESP32")
        
        # Label and Entry for ESP32 IP address
        self.ip_label = tk.Label(root, text="ESP32 IP Address:")
        self.ip_label.pack(pady=10)
        self.ip_entry = Entry(root)
        self.ip_entry.pack(pady=5)
        self.ip_entry.insert(0, '192.168.')  # Default IP
        
        # Label for BMP file selection
        self.label = tk.Label(root, text="Select BMP File:")
        self.label.pack(pady=10)
        
        # Button to choose file
        self.choose_file_button = tk.Button(root, text="Browse", command=self.choose_file)
        self.choose_file_button.pack(pady=5)
        
        # Frame for image preview
        self.image_frame = tk.Frame(root)
        self.image_frame.pack(pady=10)
        
        # Canvas for displaying image preview
        self.canvas = tk.Canvas(self.image_frame, width=240, height=240)
        self.canvas.pack()
        
        # Button to send file
        self.send_button = tk.Button(root, text="Send", command=self.send_bmp, state=tk.DISABLED)
        self.send_button.pack(pady=10)
        
        # File path variable
        self.file_path = tk.StringVar()
        
        # Selected file label
        self.selected_file_label = tk.Label(root, textvariable=self.file_path)
        self.selected_file_label.pack(pady=5)
        
        # Initialize file path to empty
        self.file_path.set("")
        self.img = None

    def choose_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("BMP files", "*.bmp")])
        if file_path:
            self.file_path.set(file_path)
            self.show_image_preview(file_path)
            self.send_button.config(state=tk.NORMAL)  # Enable send button

    def show_image_preview(self, file_path):
        try:
            image = Image.open(file_path)
            # Resize image to fit canvas
            image = image.resize((240, 240))
            self.img = ImageTk.PhotoImage(image)
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.img)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open image: {e}")
    
    def send_bmp(self):
        file_path = self.file_path.get()
        if not file_path:
            return
        
        esp32_ip = self.ip_entry.get()  # Get IP address from Entry widget
        
        try:
            bmp_header, pixel_data = read_bmp_file(file_path)
            send_bmp_to_esp32(esp32_ip, bmp_header, pixel_data)
        except Exception as e:
            print(f"Error sending BMP: {e}")

def read_bmp_file(file_path):
    with open(file_path, 'rb') as bmp_file:
        # Read the BMP header (first 54 bytes)
        bmp_header = bmp_file.read(54)
        
        # Verify it's a BMP file
        if bmp_header[:2] != b'BM':
            raise ValueError('Not a valid BMP file.')
        
        # Read width and height from the BMP header
        width, height = struct.unpack('<ii', bmp_header[18:26])
        print(f'Width: {width}, Height: {height}')
        
        # Read the rest of the image data
        pixel_data = bmp_file.read()
        return bmp_header, pixel_data

def send_bmp_to_esp32(esp32_ip, bmp_header, pixel_data):
    ESP32_PORT = 80  # Replace with your ESP32's server port
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        try:
            sock.connect((esp32_ip, ESP32_PORT))
            start_time = time.time()
            # Send the BMP header (54 bytes)
            sock.sendall(bmp_header)
            # Send the BMP pixel data
            sock.sendall(pixel_data)
            end_time = time.time()
            print(f'Sent BMP in {end_time - start_time:.2f} seconds')
            
            # Read response from ESP32
            response = sock.recv(1024)
            print('Response from ESP32:', response.decode())
        except Exception as e:
            print(f"Error sending BMP to ESP32: {e}")

if __name__ == '__main__':
    root = tk.Tk()
    app = App(root)
    root.mainloop()
