# Mock Exam Simulator

A Python-based application for simulating exams with multiple-choice questions for macOS and Windows using a Tkinter GUI by AI.

## Prerequisites
- Python 3.x
- Tkinter (GUI library)
- Virtual environment (recommended)

## Setup Instructions
- For macOS
   1. **Install Tkinter**
      ```bash
      brew install python-tk
      ```
      *Note*: For non-macOS systems, Tkinter is typically included with Python. Check your Python installation or refer to your package manager.

   2. **Create a Virtual Environment**
      ```bash
      python3 -m venv mock-venv
      deactivate
      ```

   3. **Install Dependencies**
      ```bash
      ./run_app.sh -b
      ```
- For Windows
   1. **Install Dependencies**
      > Using virtual environment is the best way but I'm lazy to do it yourself
      ```bash
      .\run_app.bat -b
      ```


## Usage
- For macOS users
   Just run the application using the provided shell script:
   ```bash
   ./run_app.sh -s
   ```
- For Windows users
   Run from terminal
   ```bash
   .\run_app.bat -s
   ```

## CSV File Format
- Supports up to 6 answer options per question.
- You should always use double quote to avoid error:
    ```csv
    question,options,correct
    "What is 2 + 2?","[""3"",""4"",""5"",""6""]","1"
    "How do you list a folder with path /home/test?","[""pwd"",""ls -al '/home/test'"",""rm -rf '/home/test'"",""cat '/home/test'""]","2"
    ```
- Refer to example CSV files in the `csv/` directory for formatting details.

## Notes
- Ensure CSV files are correctly formatted to avoid errors during exam simulation.
- The virtual environment (`mock-venv`) must be activated when installing dependencies or running the app manually.
