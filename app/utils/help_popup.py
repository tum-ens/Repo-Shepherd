import tkinter as tk
from PIL import Image, ImageTk

class HelpPopup:
    def __init__(self, image_path, height, width):
        '''
        Guide user to use this tab by image
        '''
        super().__init__()
        popup = tk.Toplevel()
        popup.title("Help")

        # Load image
        self.img = Image.open(image_path)
        
        # Resize image
        self.img = self.img.resize((height, width), Image.Resampling.LANCZOS)  
        self.img_tk = ImageTk.PhotoImage(self.img)

        # image 
        label = tk.Label(popup, image=self.img_tk)
        label.image = self.img_tk 
        label.pack(padx=10, pady=10)

        # close button
        close_btn = tk.Button(popup, text="Close", command=popup.destroy)
        close_btn.pack(pady=5)