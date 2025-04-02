import tkinter as tk
from PIL import Image, ImageTk

class HelpPopup:
    def __init__(self, master, image_path):
        '''
        Guide user to use this tab by image
        '''
        popup = tk.Toplevel(master)
        popup.title("Help")

        # Load image
        img = Image.open(image_path)
        
        # Resize image
        img = img.resize((1600, 900), Image.Resampling.LANCZOS)  
        img_tk = ImageTk.PhotoImage(img)

        # image 
        label = tk.Label(popup, image=img_tk)
        label.image = img_tk 
        label.pack(padx=10, pady=10)

        # close button
        close_btn = tk.Button(popup, text="Close", command=popup.destroy)
        close_btn.pack(pady=5)