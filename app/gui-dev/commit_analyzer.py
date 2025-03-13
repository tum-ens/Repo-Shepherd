import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import tkinter as tk
from tkinter import scrolledtext, ttk, filedialog, messagebox, BooleanVar, Checkbutton, simpledialog
import sv_ttk
import subprocess
import git

class CommitAnalyzerTab(tk.Frame):
    def __init__(self, root, shared_vars):
        super().__init__(root)
        self.shared_vars = shared_vars
        self.grid(row=0, column=0, sticky='nsew')

        self.root = root.winfo_toplevel()  # Get the top-level Tk window, not the notebook
        self.file = None  # Variable to store the selected file
        
        # Centering the grid content
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(4, weight=1)  # Allow content_frame to expand vertically
        
        title_label = ttk.Label(self, text="This is the commit message generator", font=("Arial", 16))
        title_label.grid(row=0, column=0, pady=(20, 10))  # Reduced pady for title

        description_label = ttk.Label(self, text="\n- Click on 'Current' button to edit the current commit. \n- Click on 'Old' button to old commits.", font=("Arial", 14))
        description_label.grid(row=1, column=0, pady=(10, 10))  # Row 1, increased pady for description

        self.button1 = ttk.Button(self, text="Current", command=self.open_screen1)
        self.button1.grid(row=2, column=0, pady=(10, 10))

        self.button2 = ttk.Button(self, text="Old", command=self.open_screen2)
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
        repo = filedialog.askdirectory(title="Select Repo")
        if not repo:
            messagebox.showwarning("Invalid Repo", "Please select a valid Repo.")
        else:
            self.repo = repo
            self.update_content(Current_CM)
            self.adjust_root_size()

    def open_screen2(self):
        self.update_content(Old_CM)
        self.adjust_root_size()

    def update_content(self, content_class):
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        if content_class == Current_CM:
            Current_CM(self.content_frame, self.repo)
        else:
            Old_CM(self.content_frame)

class Current_CM(tk.Frame):
    def __init__(self, parent, repo):
        super().__init__(parent)
        self.parent = parent
        self.repo = repo
        self.grid(row=0, column=0, sticky='nsew')
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.label = ttk.Label(self, text="Current Commit", font=("Helvetica", 16, "bold"), foreground="#333333")
        self.label.grid(row=0, column=1, pady=10)

        style = ttk.Style()
        style.configure("Section.TButton", font=("Helvetica", 11), padding=8)

        # Left frame for file selection and CM submit
        self.left_frame = tk.Frame(self)
        self.left_frame.grid(row=0, column=0, sticky='ns', padx=10)

        # get modified files from git
        file_label = tk.Label(self.left_frame, text="Changed files", font=("Arial", 12, "bold"))
        file_label.pack(anchor="center")
        self.modified_files = self.get_git_modified_files()
        self.file_vars = {}

        # Listen to the change of file selection
        self.selected_file = tk.StringVar(value="")

        for file in self.modified_files:
            var = BooleanVar(value=True)
            self.file_vars[file] = var
            Checkbutton(self.left_frame, text=file, variable=var, command=self.update_diff_view).pack(anchor="w")

        # Commit message entry
        self.commit_text = scrolledtext.ScrolledText(self.left_frame, width=30, height=10)
        self.commit_text.pack(pady=10)

        # buttons
        generate_btn = tk.Button(self.left_frame, text="Generate", command=self.generate_commit_message)
        commit_btn = tk.Button(self.left_frame, text="Commit", command=self.commit_changes)
        generate_btn.pack(fill=tk.Y)
        commit_btn.pack(fill=tk.Y)

        # Right frame for code diff display
        self.right_frame = tk.Frame(self)
        self.right_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        diff_label = tk.Label(self.right_frame, text="Code diff", font=("Arial", 12, "bold"))
        diff_label.pack(anchor="center")

        # Tag configuration for added lines (green), Tag configuration for removed lines (red)
        self.diff_text = scrolledtext.ScrolledText(self.right_frame, width=100, height=20)
        self.diff_text.tag_configure("added", foreground="green")
        self.diff_text.tag_configure("removed", foreground="red")
        self.diff_text.pack(fill=tk.BOTH, expand=True)
        # Read-Only
        self.diff_text.config(state=tk.DISABLED)
        # Default: Display all the code diff
        self.update_diff_view()

    def update_diff_view(self):
        """更新 diff 视图，拼接所有选中文件的 diff"""
        selected_files = [file for file, var in self.file_vars.items() if var.get()]

        if not selected_files:
            diff_content = "No file selected."
        else:
            diff_content = self.get_git_diff(selected_files)

        # 更新显示
        self.diff_text.config(state=tk.NORMAL)
        self.diff_text.delete(1.0, tk.END)
        self.diff_text.insert(tk.END, diff_content)

        # 高亮标记添加和删除的行
        lines = diff_content.splitlines()
        for line_number, line in enumerate(lines, 1):
            if line.startswith('+'):
                self.diff_text.tag_add("added", f"{line_number}.0", f"{line_number}.end")
            elif line.startswith('-'):
                self.diff_text.tag_add("removed", f"{line_number}.0", f"{line_number}.end")

        self.diff_text.config(state=tk.DISABLED)

    def get_git_diff(self, filenames):
        """获取指定文件的 diff，支持多个文件"""
        if isinstance(filenames, str):
            filenames = [filenames]  # 转换为列表

        result = []
        for filename in filenames:
            diff = subprocess.run(["git", "diff", filename], capture_output=True, text=True, encoding="utf-8").stdout
            if diff:
                result.append(f"### Diff for {filename} ###\n{diff}")
        
        return "\n".join(result) if result else "No changes found."

    def get_git_modified_files(self):
        """获取被修改的文件列表"""
        result = subprocess.run(["git", "diff", "--name-only"], capture_output=True, text=True, encoding="utf-8")
        return result.stdout.strip().split("\n") if result.stdout else []

    def generate_commit_message(self):
        self.commit_text.insert(tk.END, "Auto-generated commit message\n")

    def commit_changes(self):
        commit_msg = self.commit_text.get("1.0", tk.END).strip()
        if not commit_msg:
            print("Commit message is empty!")
            return
        selected_files = [f for f, var in self.file_vars.items() if var.get()]
        if not selected_files:
            print("No files selected for commit!")
            return
        try:
            subprocess.run(["git", "add"] + selected_files, check=True)
            subprocess.run(["git", "commit", "-m", commit_msg], check=True)
            print("Changes committed successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Git commit failed: {e}")

class Old_CM(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.grid(row=0, column=0, sticky='nsew')
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.repo = tk.StringVar()
        self.branch = tk.StringVar()
        self.selected_option = tk.IntVar(value=0)
        self.number = tk.StringVar()

        self.label = ttk.Label(self, text="Old Commit", font=("Helvetica", 16, "bold"), foreground="#333333")
        self.label.grid(row=0, column=1, pady=10)

        style = ttk.Style()
        style.configure("Section.TButton", font=("Helvetica", 11), padding=8)

        # Left frame for file selection and CM submit
        self.left_frame = tk.Frame(self)
        self.left_frame.grid(row=0, column=0, sticky='ns', padx=10)

        # Select repo, either local or remote
        self.repo_label = tk.Label(self.left_frame, text="Select repo", font=("Arial", 12, "bold"))
        self.repo_label.pack(pady=10, anchor="center")
        repo_button = tk.Button(self.left_frame, text="Repo", command=self.select_repo)
        repo_button.pack(anchor="center")

        # Select branch
        self.branch_label = tk.Label(self.left_frame, text="Select branch", font=("Arial", 12, "bold"))
        self.branch_label.pack(pady=10, anchor="center")
        branch_button = tk.Button(self.left_frame, text="Branch", command=self.select_branch)
        branch_button.pack(anchor="center")

        # Select commits (number, time)
        self.select_label = tk.Label(self.left_frame, text="Select Commits", font=("Arial", 12, "bold"))
        self.select_label.pack(pady=10, anchor="center", padx=10)
        commits_button = tk.Button(self.left_frame, text="Commit messages", command=self.select_commits)
        commits_button.pack(anchor="center")

        # Git button
        button_frame = tk.Frame(self.left_frame)
        button_frame.pack(pady=20)

        tk.Button(button_frame, text="Fetch", command=self.fetch_commits).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Refine", command=self.refine_commits).pack(side=tk.LEFT, padx=5)

        # right frame for selected commits
        self.right_frame = tk.Frame(self)
        self.right_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        label_commit = tk.Label(self.right_frame, text="Commit message list", font=("Arial", 12, "bold"))
        label_commit.pack(anchor="center")

        # Create a canvas and a scrollbar
        self.canvas = tk.Canvas(self.right_frame)
        self.scrollbar = ttk.Scrollbar(self.right_frame, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Create a frame to put inside the canvas
        self.commit_list_frame = tk.Frame(self.canvas)

        # Create a window inside the canvas to hold the commit_list_frame
        self.canvas.create_window((0, 0), window=self.commit_list_frame, anchor="nw")

        # Configure scrollbar
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(fill="both", expand=True)

        # Update the scrollable region of the canvas
        self.commit_list_frame.bind("<Configure>", self.on_frame_configure)

        # TODO
        push_button = tk.Button(self.right_frame, text="Push", command=self.push_commits, bg="black", fg="white")
        push_button.pack(side=tk.BOTTOM, pady=10)

    def on_frame_configure(self, event=None):
        # Update scroll region when the frame is resized
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def fetch_commits(self):
        git_repo = git.Repo(self.repo.get())

        if not self.branch:
            tk.messagebox.showwarning("Warning", "No branch selected. Please select a branch first.")
            return
        
        for widget in self.commit_list_frame.winfo_children():
            widget.destroy()

        option = self.selected_option.get()
        all_commits = list(git_repo.iter_commits(self.branch.get()))
        if (option == 1):
            commits = all_commits[:5]
        elif (option == 2):
            commits = all_commits[-5:]
        elif (option == 3):
            commits = all_commits
        else:
            tk.messagebox.showwarning("Warning", "Invalid commit selection")
        
        for commit in commits:
            commit_button = tk.Button(
                self.commit_list_frame, 
                text=f"{commit.hexsha[:7]} - {commit.message.splitlines()[0]}",
                command=lambda c=commit: self.show_commit_details(c),
                anchor="w",
                relief="ridge"
            )
            commit_button.pack(fill="x", padx=5, pady=2)

    def refine_commits(self):
        pass

    def push_commits(self):
        pass

    def select_repo(self):
        popup = tk.Toplevel(self)
        popup.title("Select Repository")
        popup.geometry("200x100")

        def choose_local():
            folder_selected = filedialog.askdirectory()
            if folder_selected:
                self.repo_label.config(text=folder_selected)
                self.repo.set(folder_selected)
            popup.destroy()

        local_btn = tk.Button(popup, text="Local", command=choose_local)
        local_btn.pack(pady=5)

        # TODO remote
        remote_btn = tk.Button(popup, text="Remote") 
        remote_btn.pack(pady=5)

    def select_branch(self):
        git_repo = git.Repo(self.repo.get())
        branches = [branch.name for branch in git_repo.branches]
        if not branches:
            self.commit_list.insert(tk.END, "No branches found.\n")
            return
        
        branch_window = tk.Toplevel(self)
        branch_window.title("Select Branch")
        branch_window.geometry("300x300")
        
        self.branch_var = tk.StringVar(value=branches[0])
        
        for branch in branches:
            ttk.Radiobutton(branch_window, text=branch, variable=self.branch_var, value=branch).pack(anchor="w", padx=10, pady=2)
        
        def confirm_selection():
            self.branch_label.config(text=self.branch_var.get())
            self.branch.set(self.branch_var.get())     
            branch_window.destroy()
        
        tk.Button(branch_window, text="OK", command=confirm_selection).pack(pady=10)

    def show_commit_details(self, commit):
        commit_window = tk.Toplevel(self)
        commit_window.title("Commit Details")
        commit_window.geometry("400x300")
        
        tk.Label(commit_window, text=f"Commit: {commit.hexsha}", font=("Arial", 10, "bold")).pack(pady=5)
        
        text_area = tk.Text(commit_window, wrap=tk.WORD, height=10, width=50)
        text_area.pack(padx=10, pady=5, fill="both", expand=True)
        text_area.insert(tk.END, commit.message.strip())
        text_area.config(state=tk.DISABLED)
        
        diff_button = tk.Button(commit_window, text="Code Diff", command=lambda: self.show_code_diff(commit))
        diff_button.pack(side="left", padx=10, pady=10)
        
        close_button = tk.Button(commit_window, text="Close", command=commit_window.destroy)
        close_button.pack(side="right", padx=10, pady=10)
    
    def show_code_diff(self, commit):
        diff_window = tk.Toplevel(self)
        diff_window.title("Code Diff")
        diff_window.geometry("600x400")
        
        text_area = tk.Text(diff_window, wrap=tk.WORD, height=20, width=70)
        text_area.pack(padx=10, pady=5, fill="both", expand=True)
        text_area.insert(tk.END, commit.diff("HEAD~1", create_patch=True))
        text_area.config(state=tk.DISABLED)
        
        close_button = tk.Button(diff_window, text="Close", command=diff_window.destroy)
        close_button.pack(pady=10)

    def select_commits(self):
        popup = tk.Toplevel(self)
        popup.title("Select Commits")
        popup.geometry("300x150")

        # Choose lateset, oldest, or all
        ttk.Checkbutton(popup, text="Latest", variable=self.selected_option, onvalue=1, offvalue=0).grid(row=0, column=0, padx=5, pady=5)
        ttk.Checkbutton(popup, text="Oldest", variable=self.selected_option, onvalue=2, offvalue=0).grid(row=0, column=1, padx=5, pady=5)
        ttk.Checkbutton(popup, text="All", variable=self.selected_option, onvalue=3, offvalue=0).grid(row=0, column=2, padx=5, pady=5)

        # Choose number
        ttk.Label(popup, text="Number:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        entry = ttk.Entry(popup, textvariable=self.number)
        entry.grid(row=1, column=1, columnspan=2, padx=5, pady=5, sticky="we")

        def save():
            option = self.selected_option.get()
            if (option == 1):
                selection = "Latest " + self.number.get()
            elif (option == 2):
                selection = "Oldest " + self.number.get()
            elif (option == 3):
                selection = "All"
            
            self.select_label.config(text=selection)     
            popup.destroy()

        save_button = tk.Button(popup, text="Save", command=save)
        save_button.grid(row=2, column=1, columnspan=2, padx=5, pady=5, sticky="we")

# For test, delete later
if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("800x700")
    shared_vars = {}  # Placeholder for shared_vars
    tab = CommitAnalyzerTab(root, shared_vars)
    sv_ttk.set_theme("light")  # Optional: Apply Sun Valley theme
    root.mainloop()