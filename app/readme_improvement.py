import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import tkinter as tk
from tkinter import messagebox, filedialog, ttk
from app.improvement_main_window import split_sections, improve_part
from app.utils.creation import create_part, create_feature, structure_markdown
from app.utils.repo_structure import generate_file_tree, convert_repo_to_txt
from app.utils.utils import configure_genai_api, get_local_repo_path, clone_remote_repo
import sv_ttk
import google.generativeai as genai
from app.utils.help_popup import HelpPopup
from pathlib import Path


class ReadmeImprovementTab(tk.Frame):
    def __init__(self, root, shared_vars, *args, **kwargs):
        super().__init__(root)
        self.shared_vars = shared_vars
        self.grid(row=0, column=0, sticky='nsew')

        self.root = root.winfo_toplevel()  # Get the top-level Tk window, not the notebook
        self.file = None  # Variable to store the selected file
        
        # Centering the grid content
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(4, weight=1)  # Allow content_frame to expand vertically
        title_label = ttk.Label(self, text="This is the Readme Improvement Generator", font=("Arial", 16))
        title_label.grid(row=0, column=0, pady=(20, 10))  # Reduced pady for title

        description_label = ttk.Label(self, text="\n- Click on ReadMe Improvement button to improve the file section by section. \n- Click on ReadMe Creation button to create every section manually. \n- Then, Click on the \"Help\" to get guide of this tab.", font=("Arial", 14))
        description_label.grid(row=1, column=0, pady=(10, 10))  # Row 1, increased pady for description

        self.button1 = ttk.Button(self, text="ReadMe improvement", command=self.open_screen1)
        self.button1.grid(row=2, column=0, pady=(10, 10))

        self.button2 = ttk.Button(self, text="ReadMe Creation", command=self.open_screen2)
        self.button2.grid(row=3, column=0, pady=(10, 10)) #changed to 3, to allow content frame to be row 4.

        self.content_frame = ttk.Frame(self)
        self.content_frame.grid(row=4, column=0, sticky='nsew') #changed to 4
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
        self.update_content(Improvement)
        self.adjust_root_size()

    def open_screen2(self):
        self.update_content(Creation)
        self.adjust_root_size()

    def update_content(self, content_class):
        repo_input = self.shared_vars.get("repo_path_var").get().strip()
        repo_type = self.shared_vars.get("repo_type_var").get()
        api_key = self.shared_vars.get("api_gemini_key").get().strip()
        model_name = self.shared_vars.get("default_gemini_model").get()

        repo_path = ""
        if repo_type == "local":
            repo_path = str(get_local_repo_path(repo_input))
        else:
            repo_path = str(clone_remote_repo(repo_input))

        configure_genai_api(api_key)
        model = genai.GenerativeModel(model_name)

        for widget in self.content_frame.winfo_children():
            widget.destroy()
        if content_class == Improvement:
            Improvement(self.content_frame, repo_path, model)
        else:
            Creation(self.content_frame, repo_path, model)

class Improvement(tk.Frame):
    def __init__(self, parent, repo_path, model):
        super().__init__(parent)
        self.parent = parent
        self.repo_path = repo_path
        self.model = model

        readme_files = [f for f in Path(self.repo_path).iterdir() if f.is_file() and f.name.lower() == "readme.md"]

        if readme_files:
            file = readme_files[0]  
            self.file = file
        else:
            messagebox.showwarning("Invalid File", "No valid Markdown file (.md or .markdown) found.")

        self.grid(row=0, column=0, sticky='nsew')
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.label = ttk.Label(self, text="ReadMe Improvement", font=("Helvetica", 16, "bold"), foreground="#333333")
        self.label.grid(row=0, column=1, pady=10)

        self.left_frame = tk.Frame(self)
        self.left_frame.grid(row=0, column=0, sticky='nsew', padx=5)
        canvas = tk.Canvas(self.left_frame, highlightthickness=0)
        scrollbar = tk.Scrollbar(self.left_frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)

        def resize_scrollable_frame(event):
            canvas.itemconfig(window, width=event.width)

        # Add a scroll bar to avoid too many buttons
        window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.bind("<Configure>", resize_scrollable_frame)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.section_text = split_sections(self.file)
        self.generated_section_text = tk.StringVar()
        self.generated_section_title = tk.StringVar()
        self.saved_text = {}
        self.file_tree = tk.StringVar()
        self.repo_txt = tk.StringVar()
        self.text_updated = False
        self.last_button_pressed = tk.StringVar()

        style = ttk.Style()
        style.configure("Section.TButton", font=("Helvetica", 11), padding=8)

        ####### Sections buttons #######
        section_separator = ttk.Separator(scrollable_frame, orient="horizontal")
        section_separator.pack(fill="x", padx=10, pady=(10, 5))

        section_info_label = ttk.Label(scrollable_frame, text="Sections", font=("TkDefaultFont", 9))
        section_info_label.pack(pady=(0, 10))
        
        self.sections = list(self.section_text.keys())
        for section in self.sections:
            btn = ttk.Button(scrollable_frame, text=section, command=lambda s=section: self.show_original_text(s), style="Section.TButton")
            btn.pack(pady=5, padx=10)
        
        ####### File management buttons #######
        fm_separator = ttk.Separator(scrollable_frame, orient="horizontal")
        fm_separator.pack(fill="x", padx=10, pady=(10, 5))

        fm_info_label = ttk.Label(scrollable_frame, text="File management", font=("TkDefaultFont", 9))
        fm_info_label.pack(pady=(0, 10))

        repo_btn = ttk.Button(scrollable_frame, text="Repo", command=self.select_repo, style="Section.TButton")
        repo_btn.pack(pady=5, padx=10)

        export_btn = ttk.Button(scrollable_frame, text="Export", command=self.export, style="Section.TButton")
        export_btn.pack(pady=5, padx=10)

        ####### Navigation buttons #######
        navi_separator = ttk.Separator(scrollable_frame, orient="horizontal")
        navi_separator.pack(fill="x", padx=10, pady=(10, 5))

        navi_info_label = ttk.Label(scrollable_frame, text="Navigation", font=("TkDefaultFont", 9))
        navi_info_label.pack(pady=(0, 10))

        help_button = ttk.Button(scrollable_frame, text="Help", command=self.help, style="Section.TButton")
        help_button.pack(pady=5, padx=10)

        back_button = ttk.Button(scrollable_frame, text="Back", command=self.go_back, style="Section.TButton")
        back_button.pack(pady=5, padx=10)

        ####### Middle frame #######
        self.middle_frame = tk.Frame(self, relief="solid", bd=1)
        self.middle_frame.grid(row=0, column=1, sticky='nsew', padx=5)
        self.middle_frame.grid_columnconfigure(0, weight=1)
        self.middle_frame.grid_rowconfigure(1, weight=1)

        middle_label = ttk.Label(self.middle_frame, text="Original", font=("Helvetica", 14, "bold"))
        middle_label.pack(pady=5)

        self.middle_text = tk.Text(self.middle_frame, wrap="word", bg="white", fg="black", font=("Helvetica", 12))
        self.middle_text.pack(padx=10, pady=5, fill="both", expand=True)

        ####### Right frame #######
        self.right_frame = tk.Frame(self,relief="solid", bd=1)
        self.right_frame.grid(row=0, column=2, sticky='nsew', padx=5)
        self.right_frame.grid_columnconfigure(0, weight=1)
        self.right_frame.grid_rowconfigure(0, weight=0)  # Label not extendable
        self.right_frame.grid_rowconfigure(1, weight=1)  # Text extendable
        self.right_frame.grid_rowconfigure(2, weight=0)  # Buttons not extendable

        right_label = ttk.Label(self.right_frame, text="Suggestions", font=("Helvetica", 14, "bold"))
        right_label.grid(row=0, column=0, pady=5)

        self.right_text = tk.Text(self.right_frame, wrap="word", bg="white", fg="black", font=("Helvetica", 12))
        self.right_text.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")

        btn_frame = tk.Frame(self.right_frame)
        btn_frame.grid(row=2, column=0, pady=5, sticky="ew") 
        btn_frame.grid_columnconfigure(0, weight=1)
        btn_frame.grid_columnconfigure(1, weight=1)

        generate_btn = ttk.Button(btn_frame, text="Generate", command=lambda: self.show_improved_text(self.right_text, self.last_button_pressed.get()), style="Section.TButton")
        generate_btn.grid(row=0, column=0, padx=5, sticky="ew")

        save_btn = ttk.Button(btn_frame, text="Save", command=self.save_text, style="Section.TButton")
        save_btn.grid(row=0, column=1, padx=5, sticky="ew")

    def show_original_text(self, section):
        '''
        Click section and show original text
        '''
        # If generated text is unsaved, pop this window
        if self.text_updated:
            WarningIfTextUpdated(self)
        content = self.section_text.get(section, "No original text.")
        self.middle_text.delete("1.0", tk.END)
        self.right_text.delete("1.0", tk.END)
        self.middle_text.insert(tk.END, content)
        self.last_button_pressed.set(section)
        if section in self.saved_text:
            self.right_text.insert(tk.END, self.saved_text[section])

    def save_text(self):
        '''
        Save improved text by LLM
        '''
        key = self.generated_section_title.get()
        value = self.generated_section_text.get()
        self.saved_text[key] = value
        self.text_updated = False
        messagebox.showinfo("Info", "Text saved.")

    def show_improved_text(self, text, section):
        '''
        Display improved text if it exists
        '''
        text.delete("1.0", tk.END)
        original = self.section_text.get(section, "No original text.")
        improved = improve_part(section, original, self.file_tree.get(), self.model)
        text.insert(tk.END, improved)
        self.generated_section_title.set(section)
        self.generated_section_text.set(improved)
        self.text_updated = True

    def export(self):
        '''
        Export markdown file
        '''
        ExportWindow(self, self.saved_text)

    def select_repo(self):
        '''
        Select repo location and import file tree
        '''
        FileTreePopup(self, self.repo_path)

    def help(self):
        HelpPopup("app/guide/Readme_improvement.png", 1200, 800)

    def go_back(self):
        '''
        Back to main page
        '''
        for widget in self.parent.winfo_children():
            widget.destroy()

class Creation(tk.Frame):
    def __init__(self, parent, repo_path, model):
        super().__init__(parent)
        self.parent = parent
        self.repo_path = str(repo_path)
        self.model = model
        self.grid(row=0, column=0, sticky='nsew')
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.label = ttk.Label(self, text="ReadMe Creation", font=("Helvetica", 16, "bold"), foreground="#333333")
        self.label.grid(row=0, column=1, pady=10)

        self.left_frame = tk.Frame(self)
        self.left_frame.grid(row=0, column=0, sticky='ns', padx=5)
        
        # Scroll bar
        canvas = tk.Canvas(self.left_frame, highlightthickness=0)
        scrollbar = tk.Scrollbar(self.left_frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)

        def resize_scrollable_frame(event):
            canvas.itemconfig(window, width=event.width)

        window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

        canvas.bind("<Configure>", resize_scrollable_frame)
        # Add a scroll bar to avoid too many buttons
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.saved_text = {}
        self.title_name = tk.StringVar()
        self.description = tk.StringVar()
        self.requirement = []
        self.installation = []
        self.usage = tk.StringVar()
        self.contact = []
        self.selected_license = tk.StringVar()
        self.features = []
        self.last_button_pressed = tk.StringVar(value="None")
        self.text_updated = False
        self.file_tree = tk.StringVar()

        style = ttk.Style()
        style.configure("Section.TButton", font=("Helvetica", 11), padding=8)

        ####### Sections buttons #######
        section_separator = ttk.Separator(scrollable_frame, orient="horizontal")
        section_separator.pack(fill="x", padx=10, pady=(10, 5))

        section_info_label = ttk.Label(scrollable_frame, text="Sections", font=("TkDefaultFont", 9))
        section_info_label.pack(pady=(0, 10))

        self.sections = ["title", "description", "feature", "requirement", "installation", "usage", "contact", "license"]
        for section in self.sections:
            btn = ttk.Button(scrollable_frame, text=section, command=lambda s=section: self.call_func(s), style="Section.TButton")
            btn.pack(pady=5, padx=10)

        ####### File management buttons #######
        fm_separator = ttk.Separator(scrollable_frame, orient="horizontal")
        fm_separator.pack(fill="x", padx=10, pady=(10, 5))

        fm_info_label = ttk.Label(scrollable_frame, text="File management", font=("TkDefaultFont", 9))
        fm_info_label.pack(pady=(0, 10))
        
        repo_btn = ttk.Button(scrollable_frame, text="Repo", command=self.select_repo, style="Section.TButton")
        repo_btn.pack(pady=(20, 5), padx=10)

        export_btn = ttk.Button(scrollable_frame, text="Export", command=self.export, style="Section.TButton")
        export_btn.pack(pady=5, padx=10)

        ####### Navigation buttons #######
        navi_separator = ttk.Separator(scrollable_frame, orient="horizontal")
        navi_separator.pack(fill="x", padx=10, pady=(10, 5))

        navi_info_label = ttk.Label(scrollable_frame, text="Navigation", font=("TkDefaultFont", 9))
        navi_info_label.pack(pady=(0, 10))

        help_button = ttk.Button(scrollable_frame, text="Help", command=self.help, style="Section.TButton")
        help_button.pack(pady=10)

        back_button = ttk.Button(scrollable_frame, text="Back", command=self.go_back, style="Section.TButton")
        back_button.pack(pady=10)

        ####### Right frame #######
        self.right_frame = tk.Frame(self, relief="solid", bd=1)
        self.right_frame.grid(row=0, column=1, sticky='nsew', padx=5)
        self.right_frame.grid_columnconfigure(0, weight=1)
        self.right_frame.grid_rowconfigure(0, weight=0)  # Label not extendable
        self.right_frame.grid_rowconfigure(1, weight=1)  # Text extendable
        self.right_frame.grid_rowconfigure(2, weight=0)  # Buttons not extendable

        right_label = ttk.Label(self.right_frame, text="Suggestions", font=("Helvetica", 14, "bold"))
        right_label.grid(row=0, column=0, pady=5)

        self.right_text = tk.Text(self.right_frame, wrap="word", bg="white", fg="black", font=("Helvetica", 12))
        self.right_text.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")

        btn_frame = tk.Frame(self.right_frame)
        btn_frame.grid(row=2, column=0, pady=5, sticky="ew") 
        btn_frame.grid_columnconfigure(0, weight=1)
        btn_frame.grid_columnconfigure(1, weight=1)

        generate_btn = ttk.Button(btn_frame, text="Generate", command=lambda: self.show_created_text(self.right_text, self.last_button_pressed.get()), style="Section.TButton")
        generate_btn.grid(row=0, column=0, padx=5, sticky="ew")

        save_btn = ttk.Button(btn_frame, text="Save", command=self.save_text, style="Section.TButton")
        save_btn.grid(row=0, column=1, padx=5, sticky="ew")

    def call_func(self, section):
        '''
        There are 3 different types of sections
        License: users can select one from three
        Text format: users input text information inside
        Dynamic entry format: users are able to add or delete columns for information
        '''
        # If generated text is unsaved, pop this window
        if self.text_updated:
            warning_popup = WarningIfTextUpdated(self)
            self.wait_window(warning_popup.popup)

        self.last_button_pressed.set(section)
        self.right_text.delete("1.0", tk.END)
        if section == "license":
            self.license()
        elif section in ("title", "description", "usage"):
            self.text_format(section)
        else:
            self.dynamic_entry_format(section)
        created_part = self.saved_text.get(section, "No text.")
        self.right_text.insert(tk.END, created_part)

    def save_text(self):
        '''
        Save created text by LLM
        '''
        key = self.last_button_pressed.get()
        value = self.right_text.get("1.0", tk.END).strip()
        self.saved_text[key] = value
        self.text_updated = False
        messagebox.showinfo("Info", "Text saved.")

    def show_created_text(self, text, section):
        '''
        Display created text if it exists.
        '''
        text.delete("1.0", tk.END)
        info = {
            'title': self.title_name.get(),
            'description': self.description.get(),
            'feature': ", ".join(self.features),
            'requirement': ", ".join(self.requirement),
            'installation': ", ".join(self.installation),
            'usage': self.usage.get(),
            'contact': ", ".join(self.contact),
            'license': self.selected_license.get()
        }.get(section)
        improved = create_part(section, info, self.file_tree.get(), self.model) if info else "No content provided."
        text.insert(tk.END, improved)
        self.text_updated = True

    def dynamic_entry_format(self, section):
        DynamicEntryApp(self, section)

    def text_format(self, section):
        '''
        UI for text format
        '''
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
            '''
            Save information users give
            '''
            if section == "title":
                self.title_name.set(entry.get())
            elif section == "description":
                self.description.set(entry.get("1.0", tk.END).strip())
            elif section == "usage":
                self.usage.set(entry.get("1.0", tk.END).strip())
            popup.destroy()
        ttk.Button(popup, text="Save", command=save_info, style="Section.TButton").pack(pady=10)

    def select_repo(self):
        '''
        Select repo location and import file tree
        '''
        FileTreePopup(self, self.repo_path)

    def export(self):
        '''
        Export markdown file
        '''
        ExportWindow(self, self.saved_text)

    def license(self):
        '''
        Select 1 license from 3
        '''
        popup = tk.Toplevel(self.parent, bg="#f5f6f5")
        popup.title("License")
        popup.geometry("300x200")
        tk.Label(popup, text="Select a License:", font=("Helvetica", 11), bg="#f5f6f5").pack(pady=5)
        for lic in ["MIT License", "GNU License", "Apache License"]:
            ttk.Button(popup, text=lic, command=lambda l=lic: [self.selected_license.set(l), popup.destroy()], style="Section.TButton").pack(pady=5)

    def help(self):
        HelpPopup("app/guide/Readme_Creation.png", 1200, 800)

    def go_back(self):
        '''
        Go back to main page
        '''
        for widget in self.parent.winfo_children():
            widget.destroy()

class ExportWindow:
    def __init__(self, master, saved_text):
        self.master = master
        self.saved_text = saved_text
        self.section_order = []
        
        self.window = tk.Toplevel(master)
        self.window.title("Export Sections")
        self.window.geometry("300x400")
        
        self.list_frame = tk.Frame(self.window)
        self.list_frame.pack(fill=tk.BOTH, expand=True)
        
        self.button_frame = tk.Frame(self.window)
        self.button_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.export_button = tk.Button(self.button_frame, text="Export", command=self.export)
        self.export_button.pack(side=tk.RIGHT, padx=10, pady=10)

        self.back_button = tk.Button(self.button_frame, text="Back", command=self.go_back)
        self.back_button.pack(side=tk.LEFT, padx=10, pady=10)
        
        self.selected_keys = list(self.saved_text.keys())
        self.buttons = []
        self.create_draggable_buttons()
        
    def create_draggable_buttons(self):
        '''
        Drag section buttons
        '''
        for key in self.selected_keys:
            btn = tk.Button(self.list_frame, text=key, relief=tk.RAISED)
            btn.bind("<Button-1>", self.start_drag)
            btn.bind("<B1-Motion>", self.on_drag)
            self.buttons.append(btn)
            btn.pack(fill=tk.X, pady=2)
        
    def start_drag(self, event):
        widget = event.widget
        self.drag_data = {'widget': widget, 'y': event.y_root}
    
    def on_drag(self, event):
        widget = self.drag_data['widget']
        index = self.buttons.index(widget)

        delta = event.y_root - self.drag_data['y']
        if (delta < 0):
            new_index = index - (abs(delta) // 30)
        else:
            new_index = index + (delta // 30)

        # check if index valid
        new_index = max(0, min(new_index, len(self.buttons) - 1))
        if new_index != index:
            self.buttons.insert(new_index, self.buttons.pop(index))
            self.refresh_buttons()
            self.drag_data['y'] = event.y_root
    
    def refresh_buttons(self):
        for btn in self.buttons:
            btn.pack_forget()
        for btn in self.buttons:
            btn.pack(fill=tk.X, pady=2)

    def go_back(self):
        '''
        Return to main page.
        '''
        self.window.destroy()
        
    def export(self):
        '''
        Export generated markdown.
        '''
        self.section_order.clear()
        self.section_order.extend([btn.cget("text") for btn in self.buttons])
        file_path = filedialog.asksaveasfilename(
        defaultextension=".md",
        filetypes=[("Markdown files", "*.md"), ("All files", "*.*")],
        title="Save Markdown File"
    )
        if file_path:
            with open(file_path, "w", encoding="utf-8") as file:
                # The sections should be in order like original one.
                ordered_text = ''.join(
                    self.master.saved_text[key] for key in self.section_order if key in self.master.saved_text and self.master.saved_text[key]
                    )
                structured_text = structure_markdown(ordered_text)
                file.write(structured_text)
            messagebox.showinfo(f"File saved at: {file_path}")

class DynamicEntryApp:
    def __init__(self, master, section):
        self.master = master

        self.window = tk.Toplevel(master)

        if (section == "requirement"):
            self.window.title("Requirements")
            tk.Label(self.window, text="Softwares:").pack(pady=5)
        elif (section == "installation"):
            tk.Label(self.window, text="IDE, Package manager, git address...").pack(pady=5)
            self.window.title("Installation")
        elif (section == "feature"):
            tk.Label(self.window, text="Features:")
            self.window.title("Feature")
        else:
            tk.Label(self.window, text="Name + Email address").pack(pady=5)
            self.window.title("Contact")
        
        self.entries = []
        
        self.frame = tk.Frame(self.window)
        self.frame.pack(padx=10, pady=10)
        
        if (section == "requirement"):
            if (len(self.master.requirement) == 0):
                self.add_entry("")
            else:
                for info in self.master.requirement:
                    self.add_entry(info)
        elif (section == "installation"):
            if (len(self.master.installation) == 0):
                self.add_entry("")
            else:
                for info in self.master.installation:
                    self.add_entry(info)
        elif (section == "feature"):
            if (len(self.master.features) == 0):
                self.add_feature("")
            else:
                for info in self.master.features:
                    self.add_feature(info)            
        else:
            if (len(self.master.contact) == 0):
                self.add_entry("")
            else:
                for info in self.master.contact:
                    self.add_entry(info)
        
        btn_frame = tk.Frame(self.window)
        btn_frame.pack(fill='x', pady=5)
        
        self.add_button = tk.Button(btn_frame, text="+", command=lambda: self.add_feature("") if section == "feature" else self.add_entry(""))
        self.add_button.pack(side='left', padx=5, pady=5)
        
        self.save_button = tk.Button(btn_frame, text="Save", command=lambda: self.save_entries(section))
        self.save_button.pack(side='right', padx=5, pady=5)

    
    def add_entry(self, info):
        '''
        Add column
        '''
        frame = tk.Frame(self.frame)
        frame.pack(fill='x', pady=2)
        
        entry = tk.Entry(frame, width=40)
        entry.pack(side='left', padx=5)
        entry.insert(0, info)

        del_button = tk.Button(frame, text="Delete", command=lambda: self.delete_entry(frame, entry))
        del_button.pack(side='right', padx=5)
        
        self.entries.append((frame, entry))
    
    def add_feature(self, info):
        '''
        Feature column have more buttons than normal one
        '''
        frame = tk.Frame(self.frame)
        frame.pack(fill='x', pady=2)

        entry = tk.Text(frame, width=40, height=5, font=("Helvetica", 11), bg="#f8f9fa")
        entry.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        entry.insert(tk.END, info)

        btn_frame = tk.Frame(frame)
        btn_frame.grid(row=0, column=1, padx=5, sticky="e")

        gen_button = tk.Button(btn_frame, text="Generate", command=lambda: self.generate(entry))
        gen_button.pack(side="top", fill="x", pady=2)
        
        del_button = tk.Button(btn_frame, text="Delete", command=lambda: self.delete_entry(frame, entry))
        del_button.pack(side="top", fill="x", pady=2)
        
        self.entries.append((frame, entry))
    
    def delete_entry(self, frame, entry):
        '''
        Delete column
        '''
        frame.destroy()
        self.entries = [(f, e) for f, e in self.entries if e != entry]
    
    def generate(self, entry):
        '''
        Generate features by LLM
        '''
        feature = create_feature(self.master.features, self.master.file_tree.get(), self.master.model)
        entry.delete("1.0", tk.END)
        entry.insert(tk.END, feature)
        self.save_entries("feature")

    def save_entries(self, section):
        if (section == "requirement"):
            self.master.requirement.clear()
            self.master.requirement.extend([entry.get() for _, entry in self.entries])
        elif (section == "installation"):
            self.master.installation.clear()
            self.master.installation.extend([entry.get() for _, entry in self.entries])
        elif (section == "feature"):
            self.master.features.clear()
            self.master.features.extend([entry.get("1.0", tk.END) for _, entry in self.entries])
        else:
            self.master.contact.clear()
            self.master.contact.extend([entry.get() for _, entry in self.entries])

class FileTreePopup:
     def __init__(self, master, repo_path):
        self.master = master
        self.popup = tk.Toplevel(master, bg="#f5f6f5")
        self.popup.title("Repository Options")
        self.popup.geometry("300x200")

        def show_file_tree_options():
            '''
            UI for file tree import
            '''
            for widget in self.popup.winfo_children():
                widget.destroy()
            tk.Label(self.popup, text=f"Repo: {repo_path}", font=("Helvetica", 11), bg="#f5f6f5").pack(pady=5)
            tk.Label(self.popup, text="Depth:", font=("Helvetica", 11), bg="#f5f6f5").pack()
            depth_entry = ttk.Entry(self.popup)
            depth_entry.pack(pady=5)
            only_folders_var = tk.BooleanVar()
            ttk.Checkbutton(self.popup, text="Only Folders", variable=only_folders_var).pack(pady=5)
            ttk.Button(self.popup, text="Import", command=lambda: import_file_tree(depth_entry.get(), only_folders_var.get()), style="Section.TButton").pack(pady=5)
        
        def import_file_tree(depth, show_files):
            if(int(depth) <= 0):
                messagebox.showwarning("Warning", "Depth should be positive!")
                return
            file_tree = generate_file_tree(repo_path, int(depth) if depth.isdigit() else 2, show_files)
            self.master.file_tree.set(file_tree)
            messagebox.showinfo("Info", "Already Imported")
            self.popup.destroy()

        tk.Label(self.popup, text=f"Repo: {repo_path}", font=("Helvetica", 11), bg="#f5f6f5").pack(pady=5)
        ttk.Button(self.popup, text="File Tree", command=show_file_tree_options, style="Section.TButton").pack(pady=5)
        # TODO
        # ttk.Button(popup, text="Repo to TXT", command=lambda: [messagebox.showinfo("Info", "Already Imported"), popup.destroy()], style="Section.TButton").pack(pady=5)

class WarningIfTextUpdated:
    def __init__(self, master):
        self.master = master
        self.popup = tk.Toplevel(master, bg="#f5f6f5")
        self.popup.title("Warning")
        self.popup.geometry("300x200")
        tk.Label(self.popup, text="You haven't saved generated text.", font=("Helvetica", 12), bg="#f5f6f5").pack(pady=20)
        ttk.Button(self.popup, text="Save", command=lambda: [self.master.save_text(), self.popup.destroy()], style="Section.TButton").pack(pady=5)
        ttk.Button(self.popup, text="Abandon", command=lambda: [setattr(self.master, 'text_updated', False), self.popup.destroy()], style="Section.TButton").pack(pady=5)
        self.popup.grab_set()



if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("800x700")
    shared_vars = {}  # Placeholder for shared_vars
    tab = ReadmeImprovementTab(root, shared_vars)
    sv_ttk.set_theme("light")  # Optional: Apply Sun Valley theme
    root.mainloop()