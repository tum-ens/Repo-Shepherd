import tkinter as tk
from tkinter import ttk

class ConfigTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.grid(row=0, column=0, sticky="nsew")
        
        self.create_widgets()
        
    def create_widgets(self):
        label_subtitle = ttk.Label(self, text="Subtitle")
        label_subtitle.pack(pady=(10, 0))
        self.text_subtitle = tk.Text(self, height=6, width=50)
        self.text_subtitle.pack(pady=(0, 10))
        
        label_suggestion = ttk.Label(self, text="Suggestion")
        label_suggestion.pack(pady=(10, 0))
        self.text_suggestion = tk.Text(self, height=6, width=50)
        self.text_suggestion.pack(pady=(0, 10))
        
        label_context = ttk.Label(self, text="Context")
        label_context.pack(pady=(10, 0))
        self.text_context = tk.Text(self, height=6, width=50)
        self.text_context.pack(pady=(0, 10))
        
        save_button = ttk.Button(self, text="save", command=self.save_data)
        save_button.pack(pady=(20, 0))

    def save_data(self):
        subtitle = self.text_subtitle.get("1.0", "end-1c")
        suggestion = self.text_suggestion.get("1.0", "end-1c")
        context = self.text_context.get("1.0", "end-1c")
        print(f"Subtitle: {subtitle}\nSuggestion: {suggestion}\nContext: {context}")

# To test the setup module independently
if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("500x600")
    app = ConfigTab(root)
    app.pack(fill="both", expand=True)
    root.mainloop()
