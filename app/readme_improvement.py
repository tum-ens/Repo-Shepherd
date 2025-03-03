import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import tkinter as tk
from tkinter import messagebox, filedialog, ttk
from app.improvement_main_window import split_sections, improve_part
from app.utils.creation import create_part, create_feature
from app.utils.repo_structure import generate_file_tree, convert_repo_to_txt
import sv_ttk

class ReadmeImprovementTab(tk.Frame):
    def __init__(self, root, shared_vars, *args, **kwargs):
        super().__init__(root)
        self.shared_vars = shared_vars
        self.grid(row=0, column=0, sticky='nsew')

        self.root = root.winfo_toplevel()  # Get the top-level Tk window, not the notebook
        self.file = None  # Variable to store the selected file
        
        # Centering the grid content
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)  # Allow content_frame to expand vertically
        
        title_label = ttk.Label(self, text="Select a function", font=("Arial", 16))
        title_label.grid(row=0, column=0, pady=(20, 20))  

        self.button1 = ttk.Button(self, text="ReadMe improvement", command=self.open_screen1)
        self.button1.grid(row=1, column=0, pady=(10, 10))  

        self.button2 = ttk.Button(self, text="ReadMe creation", command=self.open_screen2)
        self.button2.grid(row=2, column=0, pady=(10, 10))  

        # Create a frame for the content
        self.content_frame = ttk.Frame(self)
        self.content_frame.grid(row=3, column=0, sticky='nsew')
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)

    def adjust_root_size(self):
        self.root.update_idletasks()
        req_width = self.winfo_reqwidth()
        req_height = self.winfo_reqheight()
        min_width, min_height = 800, 600
        max_width, max_height = self.root.winfo_screenwidth() * 0.8, self.root.winfo_screenheight() * 0.8
        width = min(max(req_width, min_width), max_width)
        height = min(max(req_height, min_height), max_height)
        self.root.geometry(f"{int(width)}x{int(height)}")
        self.root.minsize(min_width, min_height)

    def open_screen1(self):
        file = filedialog.askopenfilename(title="Select File", filetypes=[("Markdown Files", "*.md *.markdown")])
        if not file or not file.lower().endswith(('.md', '.markdown')):
            messagebox.showwarning("Invalid File", "Please select a valid Markdown file (.md or .markdown).")
        else:
            self.file = file
            self.update_content(Improvement)
            self.adjust_root_size()

    def open_screen2(self):
        self.update_content(Creation)
        self.adjust_root_size()

    def update_content(self, content_class):
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        if content_class == Improvement:
            Improvement(self.content_frame, self.file)
        else:
            Creation(self.content_frame)

class Improvement(tk.Frame):
    def __init__(self, parent, file):
        super().__init__(parent)
        self.parent = parent
        self.grid(row=0, column=0, sticky='nsew')
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.label = ttk.Label(self, text="ReadMe Improvement", font=("Helvetica", 16, "bold"), foreground="#333333")
        self.label.grid(row=0, column=1, pady=10)

        self.left_frame = tk.Frame(self)
        self.left_frame.grid(row=0, column=0, sticky='ns', padx=5)

        self.section_text = split_sections(file)
        self.generated_section_text = tk.StringVar()
        self.generated_section_title = tk.StringVar()
        self.saved_text = {}
        self.file_tree = tk.StringVar()
        self.repo_path = tk.StringVar()
        self.repo_txt = tk.StringVar()
        self.text_updated = False
        self.last_button_pressed = tk.StringVar()

        style = ttk.Style()
        style.configure("Section.TButton", font=("Helvetica", 11), padding=8)
        
        self.sections = list(self.section_text.keys())
        for section in self.sections:
            btn = ttk.Button(self.left_frame, text=section, command=lambda s=section: self.show_original_text(s), style="Section.TButton")
            btn.pack(pady=5, padx=10)
        
        repo_btn = ttk.Button(self.left_frame, text="Repo", command=self.select_repo, style="Section.TButton")
        repo_btn.pack(pady=(20, 5), padx=10)

        export_btn = ttk.Button(self.left_frame, text="Export", command=self.export, style="Section.TButton")
        export_btn.pack(pady=5, padx=10)

        back_button = ttk.Button(self.left_frame, text="Back", command=self.go_back, style="Section.TButton")
        back_button.pack(pady=10)

        self.middle_frame = tk.Frame(self, relief="solid", bd=1)
        self.middle_frame.grid(row=0, column=1, sticky='nsew', padx=5)
        self.middle_frame.grid_columnconfigure(0, weight=1)
        self.middle_frame.grid_rowconfigure(1, weight=1)

        middle_label = ttk.Label(self.middle_frame, text="Original", font=("Helvetica", 14, "bold"))
        middle_label.pack(pady=5)

        self.middle_text = tk.Text(self.middle_frame, wrap="word", bg="white", fg="black", font=("Helvetica", 12))
        self.middle_text.pack(padx=10, pady=5, fill="both", expand=True)

        self.right_frame = tk.Frame(self,relief="solid", bd=1)
        self.right_frame.grid(row=0, column=2, sticky='nsew', padx=5)
        self.right_frame.grid_columnconfigure(0, weight=1)
        self.right_frame.grid_rowconfigure(1, weight=1)

        right_label = ttk.Label(self.right_frame, text="Suggestions", font=("Helvetica", 14, "bold"))
        right_label.pack(pady=5)

        self.right_text = tk.Text(self.right_frame, wrap="word", bg="white", fg="black", font=("Helvetica", 12))
        self.right_text.pack(padx=10, pady=5, fill="both", expand=True)

        generate_btn = ttk.Button(self.right_frame, text="Generate", command=lambda: self.show_improved_text(self.right_text, self.last_button_pressed.get()), style="Section.TButton")
        generate_btn.pack(pady=5)

        save_btn = ttk.Button(self.right_frame, text="Save", command=self.save_improved_text, style="Section.TButton")
        save_btn.pack(pady=5)

    def show_original_text(self, section):
        if self.text_updated:
            self.warning_before_saving()
        content = self.section_text.get(section, "No original text.")
        self.middle_text.delete("1.0", tk.END)
        self.right_text.delete("1.0", tk.END)
        self.middle_text.insert(tk.END, content)
        self.last_button_pressed.set(section)
        if section in self.saved_text:
            self.right_text.insert(tk.END, self.saved_text[section])

    def save_improved_text(self):
        key = self.generated_section_title.get()
        value = self.generated_section_text.get()
        self.saved_text[key] = value
        self.text_updated = False

    def show_improved_text(self, text, section):
        text.delete("1.0", tk.END)
        original = self.section_text.get(section, "No original text.")
        improved = improve_part(section, original, self.file_tree.get())
        text.insert(tk.END, improved)
        self.generated_section_title.set(section)
        self.generated_section_text.set(improved)
        self.text_updated = True

    def warning_before_saving(self):
        popup = tk.Toplevel(self.parent, bg="#f5f6f5")
        popup.title("Warning")
        popup.geometry("300x200")
        tk.Label(popup, text="You haven't saved generated text.", font=("Helvetica", 12), bg="#f5f6f5").pack(pady=20)
        ttk.Button(popup, text="Save", command=lambda: [self.save_improved_text(), popup.destroy()], style="Section.TButton").pack(pady=5)
        ttk.Button(popup, text="Abandon", command=lambda: [setattr(self, 'text_updated', False), popup.destroy()], style="Section.TButton").pack(pady=5)
        popup.grab_set()

    def export(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".md", filetypes=[("Markdown files", "*.md"), ("All files", "*.*")])
        if file_path:
            with open(file_path, "w", encoding="utf-8") as file:
                ordered_text = ''.join(self.saved_text[key] for key in self.sections if key in self.saved_text)
                file.write(ordered_text)
            messagebox.showinfo("Success", f"File saved at: {file_path}")

    def select_repo(self):
        repo = filedialog.askdirectory(title="Select Repository Folder")
        if repo:
            self.repo_path.set(repo)
            self.show_popup(repo)

    def show_popup(self, repo_path):
        popup = tk.Toplevel(self.parent, bg="#f5f6f5")
        popup.title("Repository Options")
        popup.geometry("300x150")
        def show_file_tree_options():
            for widget in popup.winfo_children():
                widget.destroy()
            tk.Label(popup, text=f"Repo: {repo_path}", font=("Helvetica", 11), bg="#f5f6f5").pack(pady=5)
            tk.Label(popup, text="Depth:", font=("Helvetica", 11), bg="#f5f6f5").pack()
            depth_entry = ttk.Entry(popup)
            depth_entry.pack(pady=5)
            only_folders_var = tk.BooleanVar()
            ttk.Checkbutton(popup, text="Only Folders", variable=only_folders_var).pack(pady=5)
            ttk.Button(popup, text="Import", command=lambda: self.import_file_tree(depth_entry.get(), only_folders_var.get()), style="Section.TButton").pack(pady=5)
        def import_file_tree(depth, show_files):
            messagebox.showinfo("Info", "Already Imported")
            file_tree = generate_file_tree(self.repo_path.get(), int(depth) if depth.isdigit() else 2, show_files)
            self.file_tree.set(file_tree)
            popup.destroy()
        tk.Label(popup, text=f"Repo: {repo_path}", font=("Helvetica", 11), bg="#f5f6f5").pack(pady=5)
        ttk.Button(popup, text="File Tree", command=show_file_tree_options, style="Section.TButton").pack(pady=5)
        ttk.Button(popup, text="Repo to TXT", command=lambda: [messagebox.showinfo("Info", "Already Imported"), popup.destroy()], style="Section.TButton").pack(pady=5)

    def go_back(self):
        for widget in self.parent.winfo_children():
            widget.destroy()

class Creation(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.grid(row=0, column=0, sticky='nsew')
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.label = ttk.Label(self, text="ReadMe Creation", font=("Helvetica", 16, "bold"), foreground="#333333")
        self.label.grid(row=0, column=1, pady=10)

        self.left_frame = tk.Frame(self)
        self.left_frame.grid(row=0, column=0, sticky='ns', padx=5)

        self.saved_text = {}
        self.title_name = tk.StringVar()
        self.description = tk.StringVar()
        self.softwares = tk.StringVar()
        self.ide = tk.StringVar()
        self.package_manager = tk.StringVar()
        self.address = tk.StringVar()
        self.usage = tk.StringVar()
        self.email_or_website = tk.StringVar()
        self.contact_name = tk.StringVar()
        self.selected_license = tk.StringVar()
        self.features = []
        self.last_button_pressed = tk.StringVar(value="None")

        style = ttk.Style()
        style.configure("Section.TButton", font=("Helvetica", 11), padding=8)

        self.sections = ["title", "description", "feature", "requirement", "installation", "usage", "contact", "license"]
        for section in self.sections:
            btn = ttk.Button(self.left_frame, text=section, command=lambda s=section: self.call_func(s), style="Section.TButton")
            btn.pack(pady=5, padx=10)
        
        repo_btn = ttk.Button(self.left_frame, text="Repo", style="Section.TButton")
        repo_btn.pack(pady=(20, 5), padx=10)

        export_btn = ttk.Button(self.left_frame, text="Export", command=self.export, style="Section.TButton")
        export_btn.pack(pady=5, padx=10)

        back_button = ttk.Button(self.left_frame, text="Back", command=self.go_back, style="Section.TButton")
        back_button.pack(pady=10)

        self.right_frame = tk.Frame(self, relief="solid", bd=1)
        self.right_frame.grid(row=0, column=1, sticky='nsew', padx=5)
        self.right_frame.grid_columnconfigure(0, weight=1)
        self.right_frame.grid_rowconfigure(1, weight=1)

        right_label = ttk.Label(self.right_frame, text="Suggestions", font=("Helvetica", 14, "bold"))
        right_label.pack(pady=5)

        self.right_text = tk.Text(self.right_frame, wrap="word", bg="white", fg="black", font=("Helvetica", 12))
        self.right_text.pack(padx=10, pady=5, fill="both", expand=True)

        generate_btn = ttk.Button(self.right_frame, text="Generate", command=lambda: self.show_created_text(self.right_text, self.last_button_pressed.get()), style="Section.TButton")
        generate_btn.pack(pady=5)

        save_btn = ttk.Button(self.right_frame, text="Save", command=lambda: self.save_created_text(self.last_button_pressed.get()), style="Section.TButton")
        save_btn.pack(pady=5)

    def call_func(self, section):
        self.last_button_pressed.set(section)
        self.right_text.delete("1.0", tk.END)
        if section == "feature":
            self.feature()
        elif section == "license":
            self.license()
        elif section in ("title", "description", "usage"):
            self.text_format(section)
        else:
            self.add_delete_format(section)
        created_part = self.saved_text.get(section, "No text.")
        self.right_text.insert(tk.END, created_part)

    def save_created_text(self, section):
        key = section
        value = self.right_text.get("1.0", tk.END).strip()
        self.saved_text[key] = value

    def show_created_text(self, text, section):
        text.delete("1.0", tk.END)
        info = {
            'title': self.title_name.get(),
            'description': self.description.get(),
            'requirement': self.softwares.get(),
            'installation': f"{self.ide.get()}, {self.package_manager.get()}, {self.address.get()}",
            'usage': self.usage.get(),
            'contact': f"{self.contact_name.get()}, {self.email_or_website.get()}",
            'license': self.selected_license.get()
        }.get(section)
        improved = create_part(section, info) if info else "No content provided."
        text.insert(tk.END, improved)

    def feature(self):
        popup = tk.Toplevel(self.parent, bg="#f5f6f5")
        popup.geometry("600x600")
        popup.title("Features")
        def generate():
            feature = create_feature(self.features, 4)
            self.features = feature
        for i in range(4):
            ttk.Label(popup, text=f"Feature {i + 1}:", font=("Helvetica", 11)).grid(row=i, column=0, padx=10, pady=5)
            feature_entry = tk.Text(popup, width=60, height=7, font=("Helvetica", 11), bg="#f8f9fa")
            feature_entry.grid(row=i, column=1, padx=10, pady=5)
            self.features.append(feature_entry.get("1.0", tk.END).strip())
            if i < len(self.features):
                feature_entry.insert("1.0", self.features[i])
        ttk.Button(popup, text="Generate", command=generate, style="Section.TButton").grid(row=4, column=0, columnspan=2, pady=20)

    def add_delete_format(self, section):
        popup = tk.Toplevel(self.parent, bg="#f5f6f5")
        popup.geometry("300x300")
        popup.title(section.capitalize())
        entries = {}
        if section == "requirement":
            tk.Label(popup, text="Softwares:", font=("Helvetica", 11), bg="#f5f6f5").pack(pady=5)
            entries["softwares"] = ttk.Entry(popup, font=("Helvetica", 11))
            entries["softwares"].pack(pady=5)
            if self.softwares.get():
                entries["softwares"].insert(0, self.softwares.get())
        elif section == "installation":
            for label, var in [("IDE:", self.ide), ("Package Manager:", self.package_manager), ("Git Address:", self.address)]:
                tk.Label(popup, text=label, font=("Helvetica", 11), bg="#f5f6f5").pack(pady=5)
                entry = ttk.Entry(popup, font=("Helvetica", 11))
                entry.pack(pady=5)
                if var.get():
                    entry.insert(0, var.get())
                entries[label.strip(":")] = entry
        elif section == "contact":
            for label, var in [("Name:", self.contact_name), ("Email or Website:", self.email_or_website)]:
                tk.Label(popup, text=label, font=("Helvetica", 11), bg="#f5f6f5").pack(pady=5)
                entry = ttk.Entry(popup, font=("Helvetica", 11))
                entry.pack(pady=5)
                if var.get():
                    entry.insert(0, var.get())
                entries[label.strip(":")] = entry
        def save_info():
            if section == "requirement":
                self.softwares.set(entries["softwares"].get())
            elif section == "installation":
                self.ide.set(entries["IDE"].get())
                self.package_manager.set(entries["Package Manager"].get())
                self.address.set(entries["Git Address"].get())
            elif section == "contact":
                self.contact_name.set(entries["Name"].get())
                self.email_or_website.set(entries["Email or Website"].get())
            popup.destroy()
        ttk.Button(popup, text="Save", command=save_info, style="Section.TButton").pack(pady=10)

    def text_format(self, section):
        popup = tk.Toplevel(self.parent, bg="#f5f6f5")
        popup.geometry("300x300")
        popup.title(section.capitalize())
        if section == "title":
            tk.Label(popup, text="Project Name:", font=("Helvetica", 11), bg="#f5f6f5").pack(pady=5)
            entry = ttk.Entry(popup, font=("Helvetica", 11))
            entry.pack(pady=5)
            if self.title_name.get():
                entry.insert(0, self.title_name.get())
        else:
            tk.Label(popup, text=f"{section.capitalize()}:", font=("Helvetica", 11), bg="#f5f6f5").pack(pady=5)
            entry = tk.Text(popup, width=20, height=5, font=("Helvetica", 11), bg="#f8f9fa")
            entry.pack(fill="both", expand=True, padx=10, pady=5)
            if section == "description" and self.description.get():
                entry.insert(tk.END, self.description.get())
            elif section == "usage" and self.usage.get():
                entry.insert(tk.END, self.usage.get())
        def save_info():
            if section == "title":
                self.title_name.set(entry.get())
            elif section == "description":
                self.description.set(entry.get("1.0", tk.END).strip())
            elif section == "usage":
                self.usage.set(entry.get("1.0", tk.END).strip())
            popup.destroy()
        ttk.Button(popup, text="Save", command=save_info, style="Section.TButton").pack(pady=10)

    def export(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".md", filetypes=[("Markdown files", "*.md"), ("All files", "*.*")])
        if file_path:
            with open(file_path, "w", encoding="utf-8") as file:
                ordered_text = ''.join(self.saved_text.get(key, '') for key in self.sections)
                file.write(ordered_text)
            messagebox.showinfo("Success", f"File saved at: {file_path}")

    def license(self):
        popup = tk.Toplevel(self.parent, bg="#f5f6f5")
        popup.title("License")
        popup.geometry("300x200")
        tk.Label(popup, text="Select a License:", font=("Helvetica", 11), bg="#f5f6f5").pack(pady=5)
        for lic in ["MIT License", "GNU License", "Apache License"]:
            ttk.Button(popup, text=lic, command=lambda l=lic: [self.selected_license.set(l), popup.destroy()], style="Section.TButton").pack(pady=5)

    def go_back(self):
        for widget in self.parent.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("800x700")
    shared_vars = {}  # Placeholder for shared_vars
    tab = ReadmeImprovementTab(root, shared_vars)
    sv_ttk.set_theme("light")  # Optional: Apply Sun Valley theme
    root.mainloop()