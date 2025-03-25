import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import tkinter as tk
from tkinter import scrolledtext, ttk, filedialog, messagebox, BooleanVar, Checkbutton
from utils.commit_message import generate_CM, improve_CM
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
        
        title_label = ttk.Label(self, text="Commit message generator", font=("Arial", 16))
        title_label.grid(row=0, column=0, pady=(20, 10))  # Reduced pady for title

        description_label = ttk.Label(self, text="\n- Click on the \"Current\" button to edit the commit message for the current commit. \n- Click on the \"History\" button to view and edit past commit messages.", font=("Arial", 14))
        description_label.grid(row=1, column=0, pady=(10, 10))  # Row 1, increased pady for description

        self.button1 = ttk.Button(self, text="Current", command=self.open_screen1)
        self.button1.grid(row=2, column=0, pady=(10, 10))

        self.button2 = ttk.Button(self, text="History", command=self.open_screen2)
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
        self.update_content(History_CM)
        self.adjust_root_size()

    def update_content(self, content_class):
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        if content_class == Current_CM:
            Current_CM(self.content_frame, self.repo)
        else:
            History_CM(self.content_frame)

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

        for file in self.modified_files:
            var = BooleanVar(parent)
            var.set(True)
            self.file_vars[file] = var
            Checkbutton(self.left_frame, text=file, variable=var, command=self.update_diff_view).pack(anchor="w")

        # Commit message entry
        self.commit_text = scrolledtext.ScrolledText(self.left_frame, width=50, height=10)
        self.commit_text.pack(pady=10)

        # buttons
        generate_btn = tk.Button(self.left_frame, text="Generate", command=self.generate_commit_message)
        commit_btn = tk.Button(self.left_frame, text="Commit", command=self.commit_changes)
        push_btn = tk.Button(self.left_frame, text="Push", command=self.push_changes)
        generate_btn.pack(side="left", expand=True, fill="x", padx=5)
        commit_btn.pack(side="left", expand=True, fill="x", padx=5)
        push_btn.pack(side="left", expand=True, fill="x", padx=5)

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
        # Update code diff once click files
        # But if integrated, it displayed strangely, need to be fixed.
        selected_files = [file for file, var in self.file_vars.items() if var.get()]

        if not selected_files:
            diff_content = "No file selected."
        else:
            diff_content = self.get_git_diff(selected_files)

        self.diff_text.config(state=tk.NORMAL)
        self.diff_text.delete(1.0, tk.END)
        self.diff_text.insert(tk.END, diff_content)

        # Highlight
        lines = diff_content.splitlines()
        for line_number, line in enumerate(lines, 1):
            if line.startswith('+'):
                self.diff_text.tag_add("added", f"{line_number}.0", f"{line_number}.end")
            elif line.startswith('-'):
                self.diff_text.tag_add("removed", f"{line_number}.0", f"{line_number}.end")

        self.diff_text.config(state=tk.DISABLED)

    def get_git_diff(self, filenames):
        # get multiple files to list
        if isinstance(filenames, str):
            filenames = [filenames] 

        result = []

        for filename in filenames:
             # Get unstaged changes (modified)
            diff = subprocess.run(["git", "diff", filename], capture_output=True, text=True, encoding="utf-8", cwd=self.repo).stdout
            
            # Get staged changes (including newly added)
            staged_diff = subprocess.run(["git", "diff", "--cached", filename], capture_output=True, text=True, encoding="utf-8", cwd=self.repo).stdout
            
            # Get untracked files (new files that haven't been added)
            untracked_files = subprocess.run(["git", "ls-files", "--others", "--exclude-standard"], capture_output=True, text=True, encoding="utf-8", cwd=self.repo).stdout.splitlines()

            # If the file is untracked, show its content before adding
            if filename in untracked_files:
                try:
                    with open(filename, "r", encoding="utf-8") as file:
                        new_file_content = file.read()
                    result.append(f"### New file (Untracked) - {filename} ###\n{new_file_content}\n")
                except FileNotFoundError:
                    result.append(f"Error: File {filename} not found.")

            # If there are any modifications or staged changes, append those as well
            if diff or staged_diff:
                result.append(f"### Diff for {filename} ###")
                if diff:
                    result.append(f"Modified:\n{diff}")
                if staged_diff:
                    result.append(f"Newly Added or Staged:\n{staged_diff}")

        return "\n".join(result) if result else "No changes found."

    def get_git_modified_files(self):
        result = subprocess.run(["git", "status", "--short"], capture_output=True, text=True, encoding="utf-8", cwd=self.repo)
        files = result.stdout.splitlines() if result.stdout else []

        # Extract the file names (remove the first two characters e.g. 'M app/gui-dev/readme_automatic.py', '?? app/prompts/commit_message.yaml')
        file_names = [file[3:] for file in files]

        # Print the cleaned-up file names
        return file_names

    def generate_commit_message(self):
        self.commit_text.delete("1.0", "end")
        content = self.diff_text.get("1.0", tk.END)
        commit_message = generate_CM(content)
        self.commit_text.insert(tk.END, commit_message)

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
            subprocess.run(["git", "add"] + selected_files, check=True, cwd=self.repo)
            subprocess.run(["git", "commit", "-m", commit_msg], check=True, cwd=self.repo)
            print("Changes committed successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Git commit failed: {e}")

    def push_changes(self):
            subprocess.run(['git', 'push'], cwd=self.repo)

class History_CM(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.grid(row=0, column=0, sticky='nsew')
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.repo = tk.StringVar()
        self.branch = tk.StringVar()
        # I don't know why, but it seems that if variables are not correctly updated, put parent frame as an initial value will solve the problem :(
        self.selected_option = tk.IntVar(parent)
        self.number = tk.StringVar(parent)

        self.label = ttk.Label(self, text="History Commit", font=("Helvetica", 16, "bold"), foreground="#333333")
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
        tk.Button(button_frame, text="Refine All", command=self.refine_all_commits).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Push All", command=self.push_all_commits).pack(side=tk.LEFT, padx=5)

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
        self.commit_list = []
        self.improved_commit_list = []

        # Saved refined commit messages
        self.refined_messages = {}

        # Create a window inside the canvas to hold the commit_list_frame
        self.canvas.create_window((0, 0), window=self.commit_list_frame, anchor="nw")

        # Configure scrollbar
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(fill="both", expand=True)

        # Update the scrollable region of the canvas
        self.commit_list_frame.bind("<Configure>", self.on_frame_configure)

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
        self.commit_list.clear()
        if (option == 1):
            self.commit_list.extend(all_commits[:int(self.number.get())])
        elif (option == 2):
            self.commit_list.extend(all_commits[-int(self.number.get()):])
        elif (option == 3):
            self.commit_list.extend(all_commits)
        else:
            tk.messagebox.showwarning("Warning", "Invalid commit selection")

        for commit in self.commit_list:
            commit_button = tk.Button(
                self.commit_list_frame, 
                text=f"{commit.hexsha[:7]} - {commit.message.splitlines()[0]}",
                command=lambda c=commit: self.show_commit_details(c),
                anchor="w",
                relief="ridge"
            )
            commit_button.pack(fill="x", padx=5, pady=2)

    def refine_all_commits(self):
        for commit in self.commit_list:
            code_diff = "\n".join([patch.diff.decode("utf-8") for patch in commit.diff("HEAD~1", create_patch=True)])
            original_CM = commit.message.strip()
            commit_hash =commit.hexsha
            refined_CM = improve_CM(code_diff, original_CM)
            self.refined_messages.update({commit_hash: refined_CM})

    def has_unstashed_changes(self):
        unstashed_query = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True, cwd=self.repo.get())
        result = bool(unstashed_query.stdout.strip())

        def stash_changes():
            '''
            git stash
            '''
            subprocess.run(["git", "stash"], check=True, cwd=self.repo.get())

        def reset_changes():
            '''
            git reset --hard
            '''
            subprocess.run(["git", "reset", "--hard"], check=True, cwd=self.repo.get())

        if result:
            result = messagebox.askquestion("Detect unstashed changes", "Press 'yes' to stash or 'no' to reset?\n\n")
            if result == 'yes':
                stash_changes()
            else:
                reset_changes()

    def push_all_commits(self):
        if not self.refined_messages:
            print("No commits to process.")
            return
        
        self.has_unstashed_changes()

        def get_commit_range(commit_hashes):
            '''
            Get commit range (from earlist to latest) from given commit_hashes
            '''
            git_repo = git.Repo(self.repo.get())

            sorted_hashes = sorted(commit_hashes, key=lambda h: git_repo.commit(h).committed_datetime)

            earliest_commit = sorted_hashes[0]  
            # latest_commit = sorted_hashes[-1] 

            # Best case, saving time, avoiding iterating from HEAD to earlist commit
            # but it seems that git filter-branch can't use this phrase... 
            # commit_range = f"{earliest_commit}^..{latest_commit}"
            commit_range = f"{earliest_commit}^..HEAD"

            return commit_range

        msg_filter_script_if = """if [ "$GIT_COMMIT" = "{commit}" ]; then
                    echo "{title}"
        {body}
                """
        msg_filter_script_elif = """elif [ "$GIT_COMMIT" = "{commit}" ]; then
                    echo "{title}"
        {body}
                """

        script_lines = []
        for i, (commit, message) in enumerate(self.refined_messages.items()):
            # If " or ' exists in bash code, they will occur instruction interrupt. Delete them.
            message = message.replace('"', '').replace("'", "")

            title, *body_lines = message.split("\n")
            body = "\n".join(f"            echo \"{line}\"" for line in body_lines)
            
            if i == 0:
                script_lines.append(msg_filter_script_if.format(commit=commit, title=title, body=body))
            else:
                script_lines.append(msg_filter_script_elif.format(commit=commit, title=title, body=body))

        msg_filter = "\n".join(script_lines)
                
        commit_range = get_commit_range(list(self.refined_messages.keys()))

        full_script = ("git filter-branch --msg-filter '" + "\n" 
                        + msg_filter + "\n"
                        + "else cat" + "\n"
                        + "fi' " + commit_range + " && rm -fr \"$(git rev-parse --git-dir)/refs/original/\""
                        )

        try:
            # Windows need to run bash code on git-bash, not shell
            if sys.platform.startswith("win"):  # Windows
                # Should ask user to configurate git bash position
                subprocess.run(
                ["C:/Program Files/Git/bin/bash.exe", "-c", full_script],
                check=True, cwd=self.repo.get()
            )
            elif sys.platform.startswith("darwin"):  # macOS
                script_path = "/tmp/git_script.sh"
                with open(script_path, "w") as file:
                    file.write("#!/bin/bash" + "\n" + full_script)
                os.chmod(script_path, 0o755)  # Make it executable
                

                subprocess.run([script_path], shell=False, check=True, cwd=self.repo.get())
                os.remove(script_path)
            else:
                print("Only support Windows & macOS.")


            subprocess.run(['git', 'push', '--force'], cwd=self.repo.get())

        except subprocess.CalledProcessError as e:
            print(f"Error: {e}")


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

        # I don't know why, but it seems that if variables are not correctly updated, put parent frame as an initial value will solve the problem :(
        branch_var = tk.StringVar(self)
        
        for branch in branches:
            ttk.Radiobutton(branch_window, text=branch, variable=branch_var, value=branch).pack(anchor="w", padx=10, pady=2)
        
        def confirm_selection():
            self.branch_label.config(text=branch_var.get())
            self.branch.set(branch_var.get())     
            branch_window.destroy()
        
        tk.Button(branch_window, text="OK", command=confirm_selection).pack(pady=10)

    def show_commit_details(self, commit):
        commit_window = tk.Toplevel(self)
        commit_window.title("Commit Details")
        commit_window.geometry("800x400")
        
        tk.Label(commit_window, text=f"Commit: {commit.hexsha}", font=("Arial", 10, "bold")).grid(row=0, column=0, columnspan=2, pady=5)

        tk.Label(commit_window, text="original", font=("Arial", 10, "bold")).grid(row=1, column=0, pady=5)
        tk.Label(commit_window, text="refined", font=("Arial", 10, "bold")).grid(row=1, column=1, pady=5)
        # Left Text Area (Original Commit Message)
        text_area = tk.Text(commit_window, wrap=tk.WORD, height=20, width=50)
        text_area.grid(row=2, column=0, padx=10, pady=5, sticky="nsew")
        text_area.insert(tk.END, commit.message.strip())
        text_area.config(state=tk.DISABLED)

        def refine_message():
            improved_text_area.delete("1.0", "end")
            code_diff = "\n".join([patch.diff.decode("utf-8") for patch in commit.diff("HEAD~1", create_patch=True)])
            original_CM = commit.message.strip()
            commit_message = improve_CM(code_diff, original_CM)
            improved_text_area.insert(tk.END, commit_message)

        def save_refined_message():
            """
            Save refined message
            """
            commit_hash = commit.hexsha
            refined_CM = improved_text_area.get(1.0, tk.END)
            self.refined_messages.update({commit_hash: refined_CM})
                    
        # Right Improved Text Area
        improved_text_area = tk.Text(commit_window, wrap=tk.WORD, height=20, width=50)
        improved_text_area.grid(row=2, column=1, padx=10, pady=5, sticky="nsew")
        if commit.hexsha in self.refined_messages:
            improved_text_area.insert(tk.END, self.refined_messages[commit.hexsha])

        # Buttons at the Bottom of the Right Area
        refine_button = tk.Button(commit_window, text="Refine", command=refine_message)
        refine_button.grid(row=3, column=1, padx=10, pady=5, sticky="sw")
        
        clear_button = tk.Button(commit_window, text="Clear", command=lambda: improved_text_area.delete(1.0, tk.END))
        clear_button.grid(row=3, column=1, padx=10, pady=5, sticky="s")

        push_button = tk.Button(commit_window, text="Save", command=save_refined_message)
        push_button.grid(row=3, column=1, padx=10, pady=5, sticky="se")
        
        # Diff Button at the Bottom of the Left Area
        diff_button = tk.Button(commit_window, text="Code Diff", command=lambda: self.show_code_diff(commit))
        diff_button.grid(row=3, column=0, padx=10, pady=5)

        # Grid configuration to make sure layout behaves correctly
        commit_window.grid_rowconfigure(1, weight=1)
        commit_window.grid_columnconfigure(0, weight=1)
        commit_window.grid_columnconfigure(1, weight=1)

    def show_code_diff(self, commit):
        diff_window = tk.Toplevel(self)
        diff_window.title("Code Diff")
        diff_window.geometry("600x400")
        
        text_area = tk.Text(diff_window, wrap=tk.WORD, height=20, width=70)
        text_area.tag_configure("added", foreground="green")
        text_area.tag_configure("removed", foreground="red")
        text_area.tag_configure("normal", foreground="black")
        text_area.pack(padx=10, pady=5, fill="both", expand=True)

        diff_content = "\n".join([patch.diff.decode("utf-8") for patch in commit.diff("HEAD~1", create_patch=True)])

        for line in diff_content.splitlines():

            if line.startswith("+"):
                text_area.insert(tk.END, line + "\n", "added")
            elif line.startswith("-"):
                text_area.insert(tk.END, line + "\n", "removed")
            else:
                text_area.insert(tk.END, line + "\n", "normal")

        text_area.config(state=tk.DISABLED)
        
        close_button = tk.Button(diff_window, text="Close", command=diff_window.destroy)
        close_button.pack(pady=10)

    def select_commits(self):
        popup = tk.Toplevel(self)
        popup.title("Select Commits")
        popup.geometry("300x150")

        # Choose lateset, oldest, or all
        ttk.Radiobutton(popup, text="Latest", variable=self.selected_option, value=1).grid(row=0, column=0, padx=5, pady=5)
        ttk.Radiobutton(popup, text="Oldest", variable=self.selected_option, value=2).grid(row=0, column=1, padx=5, pady=5)
        ttk.Radiobutton(popup, text="All", variable=self.selected_option, value=3).grid(row=0, column=2, padx=5, pady=5)

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
            else:
                selection = "Select commits"
            
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