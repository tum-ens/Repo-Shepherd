import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import tkinter as tk
from tkinter import scrolledtext, ttk, messagebox, BooleanVar, Checkbutton
from utils.commit_message import generate_CM, improve_CM
from utils.utils import configure_genai_api, get_local_repo_path, clone_remote_repo
import sv_ttk
import subprocess
import git
import google.generativeai as genai
from utils.help_popup import HelpPopup
import threading

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

        description_label = ttk.Label(self, text="\n- Click on the \"Current\" button to edit the commit message for the current commit. \n- Click on the \"History\" button to view and edit past commit messages. \n- Then, Click on the \"Help\" to get guide of this tab.", font=("Arial", 14))
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
        self.update_content(Current_CM)
        self.adjust_root_size()

    def open_screen2(self):
        self.update_content(History_CM)
        self.adjust_root_size()

    def update_content(self, content_class):
        repo_input = self.shared_vars.get("repo_path_var").get().strip()
        repo_type = self.shared_vars.get("repo_type_var").get()
        api_key = self.shared_vars.get("api_gemini_key").get().strip()
        model_name = self.shared_vars.get("default_gemini_model").get()
    
        if repo_type == "local":
            self.repo_path = get_local_repo_path(repo_input)
        else:
            self.repo_path = clone_remote_repo(repo_input)

        configure_genai_api(api_key)
        self.model = genai.GenerativeModel(model_name)

        for widget in self.content_frame.winfo_children():
            widget.destroy()
        if content_class == Current_CM:
            Current_CM(self.content_frame, self.repo_path, self.model)
        else:
            History_CM(self.content_frame, self.repo_path, self.model)

class Current_CM(tk.Frame):
    def __init__(self, parent, repo_path, model):
        super().__init__(parent)
        self.parent = parent
        self.repo = str(repo_path)
        self.model = model
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
        self.committed = False

        for file in self.modified_files:
            var = BooleanVar(parent)
            var.set(True)
            self.file_vars[file] = var
            Checkbutton(self.left_frame, text=file, variable=var, command=self.update_diff_view).pack(anchor="w")

        # Commit message entry
        self.commit_text = scrolledtext.ScrolledText(self.left_frame, width=50, height=10)
        self.commit_text.pack(pady=10)

        # buttons        
        
        help_btn = tk.Button(self.left_frame, text="Help", command=self.help)
        generate_btn = tk.Button(self.left_frame, text="Generate", command=self.generate_commit_message)
        commit_btn = tk.Button(self.left_frame, text="Commit", command=self.commit_changes)
        push_btn = tk.Button(self.left_frame, text="Push", command=self.push_changes)
        help_btn.pack(side="left", expand=True, fill="x", padx=5)
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
        self.selected_files = [file for file, var in self.file_vars.items() if var.get()]

        if not self.selected_files:
            diff_content = "No file selected."
        else:
            diff_content = self.get_git_diff(self.selected_files)

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
        if not self.selected_files:
            messagebox.showwarning("Warning", "No files selected for commit!")
            return
        commit_message = generate_CM(content, self.model)
        self.commit_text.insert(tk.END, commit_message)

    def commit_changes(self):
        commit_msg = self.commit_text.get("1.0", tk.END).strip()
        if not commit_msg:
            messagebox.showwarning("Warning", "Commit message is empty!")
            return
        selected_files = [f for f, var in self.file_vars.items() if var.get()]
        if not selected_files:
            messagebox.showwarning("Warning", "No files selected for commit!")
            return
        try:
            subprocess.run(["git", "add"] + selected_files, check=True, cwd=self.repo)
            subprocess.run(["git", "commit", "-m", commit_msg], check=True, cwd=self.repo)
            messagebox.showinfo("Info", "Commit successfully")
            self.committed = True
        except subprocess.CalledProcessError as e:
            messagebox.showwarning("Warning", f"Git commit failed: {e}")
            

    def push_changes(self):
        if not self.committed:
            messagebox.showwarning("Warning", "You should commit first!")
            return
        try:
            subprocess.run(['git', 'push'], cwd=self.repo)
            self.committed = False
            messagebox.showinfo("Info", "Successfully pushed!")
        except subprocess.CalledProcessError as e:
            messagebox.showwarning("Warning", f"Git commit failed: {e}")

    def help(self):
        HelpPopup("app/guide/Current_CM.png", 1200, 800)


class History_CM(tk.Frame):
    def __init__(self, parent, repo_path, model):
        super().__init__(parent)
        self.parent = parent
        self.grid(row=0, column=0, sticky='nsew')
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.repo = str(repo_path)
        self.model = model
        self.branch = tk.StringVar()
        self.bash_path = tk.StringVar()
        self.bash_path.set("C:/Program Files/Git/bin/bash.exe")
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

        # # Select repo, either local or remote
        # self.repo_label = tk.Label(self.left_frame, text="Select repo", font=("Arial", 12, "bold"))
        # self.repo_label.pack(pady=10, anchor="center")
        # repo_button = tk.Button(self.left_frame, text="Repo", command=self.select_repo)
        # repo_button.pack(anchor="center")

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
        git_button_frame = tk.Frame(self.left_frame)
        git_button_frame.pack(pady=20)

        tk.Button(git_button_frame, text="Fetch", command=self.fetch_commits).pack(side=tk.LEFT, padx=5)
        tk.Button(git_button_frame, text="Refine All", command=self.refine_all_commits).pack(side=tk.LEFT, padx=5)
        tk.Button(git_button_frame, text="Push", command=self.push_all_commits).pack(side=tk.LEFT, padx=5)

        # Navigation button
        self.navi_label = tk.Label(self.left_frame, text="Navigation", font=("Arial", 12, "bold"))
        self.navi_label.pack(pady=10, anchor="center")
        navi_button_frame = tk.Frame(self.left_frame)
        navi_button_frame.pack(pady=10)
        tk.Button(navi_button_frame, text="Help", command=self.help).pack(side=tk.LEFT, padx=5)
        tk.Button(navi_button_frame, text="Bash", command=self.change_bash_path).pack(side=tk.LEFT, padx=5)

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
    
        self.clear()

        git_repo = git.Repo(self.repo)

        if not self.branch.get():
            messagebox.showwarning("Warning", "No branch selected. Please select a branch first.")
            return
        
        if not self.number.get().isdigit():
            messagebox.showwarning("Warning", "Invalid commit selection.")
            return
        
        for widget in self.commit_list_frame.winfo_children():
            widget.destroy()

        option = self.selected_option.get()
        all_commits = list(git_repo.iter_commits(self.branch.get()))[:-1]
        count_of_commits = len(all_commits)
        if (option == 1):
            available_commits = min(int(self.number.get()), count_of_commits)
            self.commit_list.extend(all_commits[:available_commits])
        elif (option == 2):
            available_commits = min(int(self.number.get()), count_of_commits)
            self.commit_list.extend(all_commits[-available_commits:])
        elif (option == 3):
            self.commit_list.extend(all_commits)
        else:
            messagebox.showwarning("Warning", "Invalid commit selection.")

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

        '''
        refine all commits on right frame
        '''
        if not self.commit_list:
            messagebox.showwarning("Warning", "No commits fetched")
            return
        
        # progress_window
        progress_window = tk.Toplevel(self)
        progress_window.title("Processing Commits")
        progress_label = tk.Label(progress_window, text="Processing commits...")
        progress_label.pack(pady=10)
        
        progress = ttk.Progressbar(progress_window, orient=tk.HORIZONTAL, length=300, mode='determinate')
        progress.pack(pady=20)
        
        total_commits = len(self.commit_list)
        progress["maximum"] = total_commits

        def refine_commits():
            for i, commit in enumerate(self.commit_list):
                # Refining Merge commits is useless
                if commit.message.startswith("Merge branch"):
                    continue  

                code_diff = "\n".join([patch.diff.decode("utf-8") for patch in commit.diff(commit.parents[0], create_patch=True)])

                original_CM = commit.message.strip()
                commit_hash = commit.hexsha
                refined_CM = improve_CM(code_diff, original_CM, self.model)
                self.refined_messages.update({commit_hash: refined_CM})

                def update_progress():
                # update progress bar (GUI update must be in main thread)
                    progress["value"] = i + 1
                    progress_window.update_idletasks()
                progress_window.after(0, update_progress)

            def on_finish():
                messagebox.showinfo("Info", "All commits refined successfully!")
                progress_window.destroy()
            progress_window.after(0, on_finish)
            
        threading.Thread(target=refine_commits).start()


    def has_unstashed_changes(self):
        unstashed_query = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True, cwd=self.repo)
        result = bool(unstashed_query.stdout.strip())

        def stash_changes():
            '''
            git stash
            '''
            subprocess.run(["git", "stash"], check=True, cwd=self.repo)

        def reset_changes():
            '''
            git reset --hard
            '''
            subprocess.run(["git", "reset", "--hard"], check=True, cwd=self.repo)

        if result:
            result = messagebox.askquestion("Detect unstashed changes", "Press 'yes' to stash or 'no' to reset?\n\n")
            if result == 'yes':
                stash_changes()
            else:
                reset_changes()

    def push_all_commits(self):
        if not self.refined_messages:
            messagebox.showwarning("Warning", "No edited commits to process.")
            return
        
        self.has_unstashed_changes()

        msg_filter_script_if = """
        if test "$GIT_COMMIT" = "{commit}"; then
            echo "{title}"
        {body}
                """
    
        git_repo = git.Repo(self.repo)
        commit_messages = self.refined_messages.items()
        bash_path = self.bash_path.get() 

        # sort by commit time
        sorted_messages = sorted(
            commit_messages, 
            key=lambda item: git_repo.commit(item[0]).committed_datetime, 
            reverse=True
        )

        # return to dict
        self.refined_messages = dict(sorted_messages)

        # progress_window
        progress_window = tk.Toplevel(self)
        progress_window.title("Editing history")
        progress_label = tk.Label(progress_window, text="Editing history...")
        progress_label.pack(pady=10)
        
        progress = ttk.Progressbar(progress_window, orient=tk.HORIZONTAL, length=300, mode='determinate')
        progress.pack(pady=20)
        
        total_edit = len(self.refined_messages)
        progress["maximum"] = total_edit

        bash_scripts = []

        for i, (commit, message) in enumerate(self.refined_messages.items()):
            # If " or ' exists in bash code, they will occur instruction interrupt. Delete them.
            message = message.replace('"', '').replace("'", "")

            title, *body_lines = message.split("\n")
            body = "\n".join(f"    echo \"{line}\"" for line in body_lines)
            
            script_lines = msg_filter_script_if.format(commit=commit, title=title, body=body)
            # else:
            #     script_lines.append(msg_filter_script_elif.format(commit=commit, title=title, body=body))

            full_script = ("git filter-branch -f --msg-filter '" + "\n" 
                        + script_lines + "\n"
                        + "else cat" + "\n"
                        + "fi' " + commit + "^..HEAD"
                        )

            bash_scripts.append(full_script)

        def run_scripts():
            try:
                # Windows need to run bash code on git-bash, not shell
                if sys.platform.startswith("win"):  # Windows
                    # Should ask user to configurate git bash position
                    for idx, script in enumerate(bash_scripts):
                        subprocess.run(
                            [bash_path, "-c", script], check=True, cwd=self.repo
                        )

                        def update_progress(i=idx):
                            progress["value"] = i + 1
                            progress_window.update_idletasks()

                        progress_window.after(0, update_progress)

                    subprocess.run(
                            [bash_path, "-c", "rm -fr \"$(git rev-parse --git-dir)/refs/original/\""],
                            check=True, cwd=self.repo
                    )
                        
                elif sys.platform.startswith("darwin"):  # macOS
                    for idx, script in enumerate(bash_scripts):
                        script_path = "/tmp/git_script.sh"
                        with open(script_path, "w") as file:
                            file.write("#!/bin/bash" + "\n" + script)
                        os.chmod(script_path, 0o755)  # Make it executable
                        subprocess.run([script_path], shell=False, check=True, cwd=self.repo)
                        os.remove(script_path)

                        def update_progress(i=idx):
                            progress["value"] = i + 1
                            progress_window.update_idletasks()

                        progress_window.after(0, update_progress)

                    subprocess.run("rm -fr $(git rev-parse --git-dir)/refs/original/", shell=True, check=True, cwd=self.repo)
                        
                else:
                    progress_window.after(0, lambda: messagebox.showwarning("Warning", "Only support Windows & macOS."))
                    return

                subprocess.run(['git', 'push', '--force'], cwd=self.repo)

                def on_success():
                    progress_window.destroy()
                    messagebox.showinfo("Info", "Push succeeded. You can check them in the remote repo!")
                    # Refresh fetched commits
                    self.clear()
                    self.fetch_commits()

                progress_window.after(0, on_success)

            except subprocess.CalledProcessError as e:
                def on_error():
                    progress_window.destroy()
                    messagebox.showerror("Error", f"An error occurred:\n{e}")
                progress_window.after(0, on_error)

        threading.Thread(target=run_scripts).start()

    def clear(self):
        '''
        Clear fetched commits in right frame.
        '''
        self.commit_list.clear()  
        self.improved_commit_list.clear()  
        self.refined_messages.clear()
        for widget in self.commit_list_frame.winfo_children():
            widget.destroy()

    # def select_repo(self):
    #     popup = tk.Toplevel(self)
    #     popup.title("Select Repository")
    #     popup.geometry("200x100")

    #     def choose_local():
    #         folder_selected = filedialog.askdirectory()
    #         if folder_selected:
    #             self.repo_label.config(text=folder_selected)
    #             self.repo.set(folder_selected)
    #         popup.destroy()

    #     local_btn = tk.Button(popup, text="Local", command=choose_local)
    #     local_btn.pack(pady=5)

    #     # TODO remote
    #     remote_btn = tk.Button(popup, text="Remote") 
    #     remote_btn.pack(pady=5)

    #     self.clear()

    def select_branch(self):
        git_repo = git.Repo(self.repo)
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

        self.clear()

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
            code_diff = "\n".join([patch.diff.decode("utf-8") for patch in commit.parents[0].diff(commit, create_patch=True)])
            original_CM = commit.message.strip()
            commit_message = improve_CM(code_diff, original_CM, self.model)
            improved_text_area.insert(tk.END, commit_message)

        def save_refined_message():
            """
            Save refined message
            """
            commit_hash = commit.hexsha
            refined_CM = improved_text_area.get(1.0, tk.END)
            if (refined_CM):
                self.refined_messages.update({commit_hash: refined_CM})
                messagebox.showinfo("Info", "Refined message saved!")
            else:
                messagebox.showwarning("Warning", "Refined message is empty!")
                    
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

        diff_content = "\n".join([patch.diff.decode("utf-8") for patch in commit.parents[0].diff(commit, create_patch=True)])

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
    
    def help(self):
        HelpPopup("app/guide/History_CM.png", 1400, 600)

    def change_bash_path(self):
        '''
        Change path of git bash.
        Git filter-branch must use git bash.
        '''
        popup = tk.Toplevel(self)
        popup.title("Bash path")

        tk.Label(popup, text="Git bash path:", font=("Helvetica", 11), bg="#f5f6f5").pack(pady=5)
        entry = ttk.Entry(popup, font=("Helvetica", 11), width=50)
        entry.pack(pady=5)

        if self.bash_path.get():
            entry.insert(0, self.bash_path.get())

        def save_path():
            '''
            Save information users give
            '''
            self.bash_path.set(entry.get().strip())
            messagebox.showinfo("Info", "Path saved!")
            popup.destroy()
        ttk.Button(popup, text="Save", command=save_path, style="Section.TButton").pack(pady=10)

# For test, delete later
if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("800x700")
    shared_vars = {}  # Placeholder for shared_vars
    tab = CommitAnalyzerTab(root, shared_vars)
    sv_ttk.set_theme("light")  # Optional: Apply Sun Valley theme
    root.mainloop()