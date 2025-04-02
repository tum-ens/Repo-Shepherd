import tkinter as tk
from tkinter import ttk, messagebox
import threading
import tempfile
from pathlib import Path

# Import necessary functions from your utils module.
from app.utils.utils import (
    get_local_repo_path,
    get_remote_repo_url,
    clone_remote_repo,
    convert_repo_to_txt,
    upload_file_to_gemini,
    configure_genai_api,
)

import google.generativeai as genai

# You can change this if you have a different model for chat.
MODEL_NAME = "gemini-1.5-flash" # Default model if 'auto' is selected

class GeminiChatTab(ttk.Frame):
    def __init__(self, parent, shared_vars):
        super().__init__(parent)
        self.shared_vars = shared_vars
        self.uploaded_file = None
        self.repo_path = None
        self.temp_dir = None  # Will hold the temporary directory reference
        self.create_widgets()

    def create_widgets(self):
        # Header frame for title and description
        header_frame = ttk.Frame(self)
        header_frame.pack(fill=tk.X, pady=5)
        
        title_label = ttk.Label(header_frame, text="Gemini Chat", font=("Helvetica", 16, "bold"))
        title_label.pack(pady=(0, 2))
        
        desc_label = ttk.Label(
            header_frame,
            text=(
            "With this chat bot, you can talk with your AI assistant about selected repository. "
            "Ask questions, get tailored insights, or request help based on project's content. "
            "Simply initialize your repository context, then start chatting to explore and understand selected repo better. "
            "You can use this feature in any language, reducing language barriers for foreign projects as well."
        ),
            wraplength=500,
            justify="left"
        )
        desc_label.pack(pady=(0, 10))
        
        # Top frame with initialization and clear chat buttons
        top_frame = ttk.Frame(self)
        top_frame.pack(fill=tk.X, pady=5)

        self.init_button = ttk.Button(
            top_frame, text="Initialize Repository Context", command=self.initialize_repo_context
        )
        self.init_button.pack(side=tk.LEFT, padx=5)

        self.clear_button = ttk.Button(
            top_frame, text="Clear Chat", command=self.clear_chat
        )
        self.clear_button.pack(side=tk.LEFT, padx=5)

        # Chat display text widget with vertical scrollbar
        text_frame = ttk.Frame(self)
        text_frame.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)

        self.chat_text = tk.Text(text_frame, wrap=tk.WORD, state='normal')
        self.chat_text.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

        scrollbar = ttk.Scrollbar(text_frame, command=self.chat_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.chat_text.config(yscrollcommand=scrollbar.set)

        # Configure tags: user messages in red, gemini messages in dark blue
        self.chat_text.tag_config("user", foreground="red")
        self.chat_text.tag_config("gemini", foreground="dark blue")

        # Bottom frame for input entry and send button
        bottom_frame = ttk.Frame(self)
        bottom_frame.pack(fill=tk.X, pady=5)

        self.chat_entry = ttk.Entry(bottom_frame)
        self.chat_entry.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        # Bind the Enter key to send the message
        self.chat_entry.bind("<Return>", lambda event: self.send_message())

        send_button = ttk.Button(bottom_frame, text="Send", command=self.send_message)
        send_button.pack(side=tk.LEFT, padx=5)


    def clear_chat(self):
        self.chat_text.delete("1.0", tk.END)

    def initialize_repo_context(self):
        # Capture all necessary values on the main thread
        repo_input = self.shared_vars.get('repo_path_var').get().strip()
        repo_type = self.shared_vars.get('repo_type_var').get()
        api_key = self.shared_vars.get('api_gemini_key').get().strip()

        if not repo_input:
            self._append_text("Error: Repository path/URL is not set in the Setup tab.\n")
            return
        if not api_key:
            self._append_text("Error: API key is not set in the Setup tab.\n")
            return

        self._append_text("Initializing repository context...\n")
        # Start the background thread with captured values
        threading.Thread(
            target=self._initialize_repo_context_thread,
            args=(repo_input, repo_type, api_key),
            daemon=True
        ).start()

    def _initialize_repo_context_thread(self, repo_input, repo_type, api_key):
        try:
            # Determine repository path based on type
            if repo_type == 'local':
                repo_path = get_local_repo_path(repo_input)
            else:
                repo_path = clone_remote_repo(repo_input)
            self.repo_path = repo_path

            import tempfile
            temp_dir = tempfile.TemporaryDirectory()
            self.temp_dir = temp_dir  # Keep reference to avoid early cleanup
            output_txt_path = Path(temp_dir.name) / "repo_content.txt"

            # Convert repository to text
            convert_repo_to_txt(repo_path, output_txt_path)

            # Configure Gemini API using the passed API key
            # IMPORTANT: Ensure configure_genai_api is thread-safe if it does global config.
            # It's generally okay if it just calls genai.configure(api_key=...).
            try:
                configure_genai_api(api_key)
            except Exception as config_err:
                 # Use _append_text to safely update UI from this thread
                self._append_text(f"Error configuring Gemini API: {config_err}\n")
                return # Stop if API config fails

            # Upload the text file to Gemini
            self.uploaded_file = upload_file_to_gemini(output_txt_path)
            self._append_text("Repository context initialized successfully. You can now chat with Gemini.\n")
        except Exception as e:
            self._append_text(f"Error during initialization: {e}\n")

    def send_message(self):
        user_input = self.chat_entry.get().strip()
        if not user_input:
            return

        # --- Read shared variables in the main thread ---
        selected_model_config = self.shared_vars.get('default_gemini_model').get()
        api_key = self.shared_vars.get('api_gemini_key').get().strip() # Get API key again, in case it changed? Safer to re-read.

        if not api_key:
             self._append_text("Error: API key is not set in the Setup tab.\n")
             return

        # Determine the actual model name string to use
        model_name_to_use = MODEL_NAME # Default
        if selected_model_config != "auto" and selected_model_config:
            model_name_to_use = selected_model_config
        # -------------------------------------------------

        # Append user message in red with a blank line after it
        self._append_text(f"You: {user_input}\n\n", tag="user")
        self.chat_entry.delete(0, tk.END)

        prompt = (
            "You are a helpful assistant for using and developing the repository. Based on the repository content provided, answer the following question:\n\n"
            f"Question: {user_input}\n\nAnswer:"
        )

        # Pass the determined model name string and api_key to the background thread
        threading.Thread(
            target=self.generate_gemini_response,
            args=(prompt, model_name_to_use, api_key), # Pass model_name_to_use and api_key
            daemon=True
        ).start()

    # Modified to accept model_name and api_key as arguments
    def generate_gemini_response(self, prompt, model_name_to_use, api_key):
        try:
            if not self.uploaded_file:
                self._append_text("Error: Repository context not initialized. Please click 'Initialize Repository Context' first.\n")
                return

            # --- Configure API Key within the thread (safer for genai library) ---
            # Although configured during init, re-configuring might be safer depending on genai's implementation
            try:
                # It's often better to configure the API key just before use within the thread
                # if the library isn't explicitly documented as globally thread-safe.
                genai.configure(api_key=api_key)
            except Exception as config_err:
                self._append_text(f"Error re-configuring Gemini API in thread: {config_err}\n")
                return
            # --------------------------------------------------------------------

            # Use the model name passed as an argument
            model = genai.GenerativeModel(model_name_to_use)
            response = model.generate_content([self.uploaded_file, "\n\n", prompt])
            answer = response.text.strip()
            # Append Gemini response in dark blue with a blank line after it
            self._append_text(f"Gemini: {answer}\n\n", tag="gemini")
        except Exception as e:
            # Make sure the error message itself doesn't cause another error
            error_message = f"Error generating response: {e}\n\n"
            self._append_text(error_message) # Display the actual error


    def _append_text(self, text, tag=None):
        # Schedule the UI update to run on the main thread using self.after (original working version)
        # This assumes 'self' (the Frame widget) is still valid and attached to the main loop.
        try:
            self.after(0, lambda: self._update_text(text, tag))
        except tk.TclError as e:
            # Handle cases where the widget might have been destroyed
            print(f"Error scheduling UI update (_append_text): {e}")


    def _update_text(self, text, tag):
        # This function runs in the main thread
        try:
            if tag:
                self.chat_text.insert(tk.END, text, tag)
            else:
                self.chat_text.insert(tk.END, text)
            self.chat_text.see(tk.END)
        except tk.TclError as e:
            # Handle cases where the text widget might have been destroyed
             print(f"Error updating text widget (_update_text): {e}")