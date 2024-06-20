import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

def open_image():
    global img, img_tk, cropped_img, img_path
    img_path = filedialog.askopenfilename(
        filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.tiff")]
    )
    if not img_path:
        return
    img = Image.open(img_path).convert("RGB")  # Convert to 24-bit RGB
    update_image_preview()

def save_image():
    global cropped_img
    if cropped_img is None:
        messagebox.showwarning("Warning", "No cropped image to save!")
        return
    save_path = filedialog.asksaveasfilename(
        defaultextension=".bmp",
        filetypes=[("BMP", "*.bmp")],
    )
    if save_path:
        cropped_img.save(save_path)
        messagebox.showinfo("Image Saved", f"Image saved to {save_path}")

def crop_and_resize_image():
    global img, cropped_img
    if img is None:
        messagebox.showwarning("Warning", "No image loaded!")
        return
    width, height = img.size
    # Determine the cropping box to get a square
    crop_size = min(width, height)
    left = (width - crop_size) // 2
    top = (height - crop_size) // 2
    right = left + crop_size
    bottom = top + crop_size
    cropped_img = img.crop((left, top, right, bottom))
    resized_img = cropped_img.resize((240, 240), Image.LANCZOS)
    cropped_img = resized_img  # Update cropped_img to the resized version
    update_image_preview(resized_img)

def update_image_preview(image=None):
    global img_tk, preview_label
    if image:
        img_tk = ImageTk.PhotoImage(image)
        preview_label.config(image=img_tk)
    elif img:
        # Get current size of the preview label
        preview_width = preview_label.winfo_width()
        preview_height = preview_label.winfo_height()

        # Resize the image to fit within the preview label, maintaining aspect ratio
        img.thumbnail((preview_width, preview_height), Image.LANCZOS)
        img_tk = ImageTk.PhotoImage(img)
        preview_label.config(image=img_tk)

# Initialize global variables
img = None
cropped_img = None
img_tk = None
img_path = ""

# Create the main window
root = tk.Tk()
root.title("Image Cropper and Resizer")
root.geometry("600x600")

# Create and place widgets
open_button = tk.Button(root, text="Open Image", command=open_image)
open_button.pack(pady=10)

crop_button = tk.Button(root, text="Crop and Resize to 240x240", command=crop_and_resize_image)
crop_button.pack(pady=10)

save_button = tk.Button(root, text="Save Image", command=save_image)
save_button.pack(pady=10)

preview_label = tk.Label(root)
preview_label.pack(pady=10, fill=tk.BOTH, expand=True)

# Run the application
root.mainloop()
