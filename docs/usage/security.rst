Security Features
=================

The application includes security scanning capabilities.

Security Scanner
----------------

The core logic resides in `app/security_scanner_gemini_all_code_withsecondpass.py`.

* **Functionality:** Scans code files (identified by extensions like `.py`, `.js`, etc.) within the repository for potential security vulnerabilities.
* **Analysis Process:**
    * **First Pass:** Performs an initial analysis using a configured Gemini model (default `gemini-2.0-flash-thinking-exp-01-21` or user-selected) to identify potential issues. It extracts vulnerability details like name, description, location, remediation, threat level, and CWE ID. Results are saved to `security_vulnerabilities.json`.
    * **Second Pass (Optional):** If selected by the user, a second Gemini model (default `gemini-2.0-flash-thinking-exp-01-21` or user-selected) refines the initial findings. It uses the full repository context (uploaded as a text file) to filter out likely false positives and improve the accuracy of the reports. Refined results are saved to `improved_security_vulnerabilities.json`.
* **Output:** Generates JSON files containing lists of vulnerabilities found, including threat summaries. The format includes fields specified in the analysis prompts.
* **Rate Limiting:** Includes delays (`time.sleep`) to manage API rate limits.

SECURITY.md Generator
---------------------

The `app/gui/security_generator.py` module provides a GUI tab to create a `SECURITY.md` file.

* It prompts the user for policy details like reporting methods, disclosure timelines, preferred languages, and contact information.
* It uses a template prompt and potentially information from the `README.md` and `LICENSE` files to generate the content using an LLM.
* The generated file is saved to the repository.
