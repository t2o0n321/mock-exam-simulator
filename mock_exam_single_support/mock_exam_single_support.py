import tkinter as tk
from tkinter import filedialog, messagebox, Toplevel, ttk
import pandas as pd
from dataclasses import dataclass
from typing import List, Optional
import random
from pathlib import Path

@dataclass
class Question:
    text: str
    options: List[str]
    correct_answer: str
    user_answer: Optional[str] = None

class QuestionBank:
    def __init__(self):
        self.questions: List[Question] = []

    def load_from_csv(self, file_path: str) -> bool:
        try:
            df = pd.read_csv(file_path)
            required_columns = ["question", "option1", "option2", "option3", "option4", "correct_answer"]
            if not all(col in df.columns for col in required_columns):
                raise ValueError("CSV missing required columns")
            
            self.questions = [
                Question(
                    text=row["question"],
                    options=[row[f"option{i+1}"] for i in range(4)],
                    correct_answer=row["correct_answer"]
                ) for _, row in df.iterrows()
            ]
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Failed to import questions: {str(e)}")
            return False

    def get_random_questions(self, count: int) -> List[Question]:
        sample_size = min(len(self.questions), count)
        return random.sample(self.questions, sample_size)

class ExamState:
    def __init__(self):
        self.current_index: int = 0
        self.score: int = 0
        self.questions: List[Question] = []
        self.time_remaining: int = 0  # Time in seconds
        self.timer_id: Optional[str] = None

    def reset(self):
        self.current_index = 0
        self.score = 0
        self.questions = []
        self.time_remaining = 0
        self.timer_id = None

class UIManager:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.main_frame = tk.Frame(root, bg="#ffffff")
        self.quiz_frame = tk.Frame(root, bg="#ffffff")
        self.selected_answer = tk.StringVar()
        self.option_buttons: List[ttk.Radiobutton] = []
        self.option_frames: List[tk.Frame] = []
        self.timer_label = None
        self.progress_bar = None
        self.setup_ui()

    def setup_ui(self):
        self.root.title("Mock Exam Simulator")
        self.root.geometry("850x650")
        self.root.configure(bg="#ffffff")

        # Configure style
        style = ttk.Style()
        style.configure("TButton", font=("Segoe UI", 11, "bold"), padding=10)
        style.configure("TLabel", background="#ffffff", font=("Segoe UI", 12))
        style.configure("TEntry", padding=5)
        style.configure("TRadiobutton", background="#ffffff", font=("Segoe UI", 12))
        style.configure("TProgressbar", thickness=20)

        # Button style with hover effect and rounded corners
        style.configure("TButton", borderwidth=0, relief="flat")
        style.map("TButton",
                 background=[("active", "#0056b3"), ("!active", "#007bff"), ("disabled", "#adb5bd")],
                 foreground=[("active", "white"), ("!active", "white"), ("disabled", "white")])
        
        style.configure("TProgressbar", background="#007bff", troughcolor="#e9ecef")

        # Main frame setup
        self.main_frame.pack(pady=50, padx=50, fill="both", expand=True)
        
        # Card-like container for main content
        main_card = tk.Frame(self.main_frame, bg="#ffffff", relief="solid", borderwidth=1,
                           highlightbackground="#dee2e6", highlightthickness=1)
        main_card.pack(pady=20, padx=20, fill="both", expand=True)
        
        tk.Label(main_card, text="Mock Exam Simulator", font=("Segoe UI", 28, "bold"),
                bg="#ffffff", fg="#2d2d2d").pack(pady=30)
        
        # Settings frame in main_card
        settings_frame = tk.Frame(main_card, bg="#ffffff")
        settings_frame.pack(pady=10)
        
        tk.Label(settings_frame, text="Number of Questions:", font=("Segoe UI", 14), 
                bg="#ffffff", fg="#2d2d2d").grid(row=0, column=0, padx=10, pady=10)
        self.num_questions_entry = ttk.Entry(settings_frame, width=10, font=("Segoe UI", 12))
        self.num_questions_entry.grid(row=0, column=1, padx=10, pady=10)
        self.num_questions_entry.insert(0, "100")
        self.num_questions_entry.configure(style="Custom.TEntry")
        style.configure("Custom.TEntry", bordercolor="#ced4da", relief="solid", borderwidth=1)
        
        tk.Label(settings_frame, text="Time Limit (minutes):", font=("Segoe UI", 14), 
                bg="#ffffff", fg="#2d2d2d").grid(row=1, column=0, padx=10, pady=10)
        self.time_limit_entry = ttk.Entry(settings_frame, width=10, font=("Segoe UI", 12))
        self.time_limit_entry.grid(row=1, column=1, padx=10, pady=10)
        self.time_limit_entry.insert(0, "60")
        self.time_limit_entry.configure(style="Custom.TEntry")
        
        # Quiz frame setup
        self.timer_label = tk.Label(self.quiz_frame, text="Time Remaining: 00:00", 
                                  font=("Segoe UI", 16, "bold"), bg="#ffffff", fg="#e63946")
        self.timer_label.pack(pady=15)
        
        self.progress_bar = ttk.Progressbar(self.quiz_frame, orient="horizontal", mode="determinate")
        self.progress_bar.pack(fill="x", padx=30, pady=10)
        
        # Question card with shadow effect
        question_card = tk.Frame(self.quiz_frame, bg="#ffffff", relief="solid", borderwidth=1,
                               highlightbackground="#dee2e6", highlightthickness=1)
        question_card.pack(pady=10, padx=30, fill="both", expand=True)
        
        self.question_label = tk.Label(question_card, text="", font=("Segoe UI", 16, "bold"),
                                     bg="#ffffff", fg="#2d2d2d", wraplength=700, justify="left")
        self.question_label.pack(pady=20, padx=20, anchor="w")
        
        # Option buttons frame
        options_frame = tk.Frame(question_card, bg="#ffffff")
        options_frame.pack(fill="x", padx=20, pady=10)
        
        for _ in range(4):
            # Create a frame for each option to style it like a card
            option_frame = tk.Frame(options_frame, bg="#ffffff", relief="solid", borderwidth=1,
                                  highlightbackground="#dee2e6", highlightthickness=1)
            option_frame.pack(fill="x", pady=5)
            
            # Bind hover effects
            option_frame.bind("<Enter>", lambda e, f=option_frame: f.config(bg="#f8f9fa"))
            option_frame.bind("<Leave>", lambda e, f=option_frame: f.config(bg="#ffffff"))
            
            rb = ttk.Radiobutton(option_frame, text="", variable=self.selected_answer, value="")
            rb.pack(anchor="w", padx=15, pady=10)
            self.option_buttons.append(rb)
            self.option_frames.append(option_frame)

    def show_main_frame(self):
        self.quiz_frame.pack_forget()
        self.main_frame.pack(pady=50, padx=50, fill="both", expand=True)

    def show_quiz_frame(self):
        self.main_frame.pack_forget()
        self.quiz_frame.pack(pady=20, padx=20, fill="both", expand=True)

    def update_timer_display(self, seconds: int):
        minutes = seconds // 60
        seconds = seconds % 60
        self.timer_label.config(text=f"Time Remaining: {minutes:02d}:{seconds:02d}")

    def update_progress(self, current: int, total: int):
        self.progress_bar["maximum"] = total
        self.progress_bar["value"] = current + 1

class MockExamApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.ui = UIManager(root)
        self.question_bank = QuestionBank()
        self.exam_state = ExamState()
        self.setup_controls()

    def setup_controls(self):
        # Main frame buttons
        self.import_button = ttk.Button(self.ui.main_frame, text="Import Questions (CSV)", 
                                      command=self.import_questions)
        self.import_button.pack(pady=10)
        
        self.start_button = ttk.Button(self.ui.main_frame, text="Start Mock Exam", 
                                     command=self.start_exam, state="disabled")
        self.start_button.pack(pady=10)
        
        # Quiz frame buttons
        button_frame = tk.Frame(self.ui.quiz_frame, bg="#ffffff")
        button_frame.pack(pady=20)
        
        self.prev_button = ttk.Button(button_frame, text="Previous", 
                                    command=self.prev_question, state="disabled")
        self.prev_button.pack(side="left", padx=8)
        
        self.next_button = ttk.Button(button_frame, text="Next", 
                                    command=self.next_question, state="disabled")
        self.next_button.pack(side="left", padx=8)
        
        self.skip_button = ttk.Button(button_frame, text="Skip", 
                                    command=self.skip_question, state="disabled")
        self.skip_button.pack(side="left", padx=8)
        
        self.review_button = ttk.Button(button_frame, text="Review Answers", 
                                      command=self.review_answers, state="disabled")
        self.review_button.pack(side="left", padx=8)
        
        self.submit_button = ttk.Button(button_frame, text="Submit Exam", 
                                      command=self.submit_exam, state="disabled")
        self.submit_button.pack(side="left", padx=8)

    def import_questions(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path and self.question_bank.load_from_csv(file_path):
            messagebox.showinfo("Success", f"Imported {len(self.question_bank.questions)} questions!")
            self.start_button.config(state="normal")

    def start_exam(self):
        try:
            num_questions = int(self.ui.num_questions_entry.get())
            time_limit = int(self.ui.time_limit_entry.get())
            if num_questions < 1 or time_limit < 1:
                raise ValueError("Invalid input")
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for questions and time limit")
            return

        if not self.question_bank.questions:
            messagebox.showerror("Error", "No questions imported!")
            return
            
        self.exam_state.reset()
        self.exam_state.questions = self.question_bank.get_random_questions(num_questions)
        self.exam_state.time_remaining = time_limit * 60  # Convert minutes to seconds
        
        self.ui.show_quiz_frame()
        
        # Enable quiz controls
        for btn in [self.next_button, self.skip_button, self.review_button, self.submit_button]:
            btn.config(state="normal")
            
        self.display_question()
        self.start_timer()

    def start_timer(self):
        if self.exam_state.time_remaining > 0:
            self.ui.update_timer_display(self.exam_state.time_remaining)
            self.exam_state.time_remaining -= 1
            self.exam_state.timer_id = self.root.after(1000, self.start_timer)
        else:
            messagebox.showinfo("Time's Up", "Time limit reached! Submitting exam...")
            self.submit_exam()

    def stop_timer(self):
        if self.exam_state.timer_id:
            self.root.after_cancel(self.exam_state.timer_id)
            self.exam_state.timer_id = None

    def display_question(self):
        question = self.exam_state.questions[self.exam_state.current_index]
        self.ui.question_label.config(text=f"Q{self.exam_state.current_index + 1}: {question.text}")
        
        for i, rb in enumerate(self.ui.option_buttons):
            rb.config(text=question.options[i], value=question.options[i])
        
        self.ui.selected_answer.set(question.user_answer or "")
        
        # Update navigation button states
        self.prev_button.config(state="normal" if self.exam_state.current_index > 0 else "disabled")
        self.next_button.config(state="normal")
        self.skip_button.config(state="normal")
        self.ui.update_progress(self.exam_state.current_index, len(self.exam_state.questions))

    def save_current_answer(self):
        current_answer = self.ui.selected_answer.get()
        if current_answer:
            self.exam_state.questions[self.exam_state.current_index].user_answer = current_answer

    def next_question(self):
        self.save_current_answer()
        
        if self.exam_state.current_index < len(self.exam_state.questions) - 1:
            self.exam_state.current_index += 1
            self.display_question()
        else:
            self.next_button.config(state="disabled")
            self.skip_button.config(state="disabled")
            messagebox.showinfo("Info", "This is the last question. Please submit the exam.")

    def prev_question(self):
        self.save_current_answer()
        self.exam_state.current_index -= 1
        self.display_question()

    def skip_question(self):
        self.exam_state.questions[self.exam_state.current_index].user_answer = None
        self.next_question()

    def review_answers(self):
        self.stop_timer()
        review_window = Toplevel(self.root)
        review_window.title("Review Answers")
        review_window.geometry("600x600")
        review_window.configure(bg="#ffffff")
        
        listbox = tk.Listbox(review_window, width=80, height=25, font=("Segoe UI", 12),
                           bg="#ffffff", fg="#2d2d2d", selectbackground="#007bff")
        listbox.pack(pady=15, padx=15)
        
        for i, q in enumerate(self.exam_state.questions):
            status = q.user_answer or "Skipped"
            listbox.insert(tk.END, f"Q{i+1}: {q.text[:50]}... -> {status}")
        
        def go_to_question(event):
            if selection := listbox.curselection():
                self.exam_state.current_index = selection[0]
                self.display_question()
                review_window.destroy()
                self.start_timer()
        
        listbox.bind("<Double-1>", go_to_question)
        ttk.Button(review_window, text="Close", 
                  command=lambda: [review_window.destroy(), self.start_timer()]).pack(pady=10)

    def submit_exam(self):
        self.stop_timer()
        self.save_current_answer()
        
        unanswered = [i for i, q in enumerate(self.exam_state.questions) if not q.user_answer]
        if unanswered:
            if messagebox.askyesno("Unanswered Questions", 
                                 f"You have {len(unanswered)} unanswered questions. Review them now?"):
                self.review_answers()
                return
        
        self.exam_state.score = sum(1 for q in self.exam_state.questions 
                                  if q.user_answer and q.user_answer == q.correct_answer)
        
        incorrect_questions = [
            {
                'question': q.text,
                'your_answer': q.user_answer or "Skipped",
                'correct_answer': q.correct_answer
            } for q in self.exam_state.questions if q.user_answer != q.correct_answer
        ]
        
        # Show results
        total = len(self.exam_state.questions)
        percentage = (self.exam_state.score / total) * 100
        messagebox.showinfo("Results", 
                          f"Exam Completed!\nYour Score: {self.exam_state.score}/{total}\n"
                          f"Percentage: {percentage:.2f}%")
        
        # Show feedback
        if incorrect_questions:
            feedback_window = Toplevel(self.root)
            feedback_window.title("Feedback: Incorrect/Skipped Questions")
            feedback_window.geometry("800x700")
            feedback_window.configure(bg="#ffffff")
            
            listbox = tk.Listbox(feedback_window, width=100, height=30, font=("Segoe UI", 12),
                               bg="#ffffff", fg="#2d2d2d")
            listbox.pack(pady=15, padx=15)
            
            for i, item in enumerate(incorrect_questions, 1):
                listbox.insert(tk.END, f"Q{i}: {item['question'][:100]}...")
                listbox.insert(tk.END, f"  Your Answer: {item['your_answer']}")
                listbox.insert(tk.END, f"  Correct Answer: {item['correct_answer']}")
                listbox.insert(tk.END, "")
            
            scrollbar = tk.Scrollbar(feedback_window, orient="vertical")
            scrollbar.config(command=listbox.yview)
            scrollbar.pack(side="right", fill="y")
            listbox.config(yscrollcommand=scrollbar.set)
            
            ttk.Button(feedback_window, text="Close", command=feedback_window.destroy).pack(pady=10)
        else:
            messagebox.showinfo("Feedback", "Congratulations! You answered all questions correctly!")
        
        # Optional Markdown export
        if messagebox.askyesno("Save Feedback", "Would you like to save the feedback as a Markdown file?"):
            file_path = filedialog.asksaveasfilename(defaultextension=".md", 
                                                  filetypes=[("Markdown files", "*.md")])
            if file_path:
                try:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(f"# Mock Exam Feedback\n\n")
                        f.write(f"**Score**: {self.exam_state.score}/{total}\n")
                        f.write(f"**Percentage**: {percentage:.2f}%\n\n")
                        if incorrect_questions:
                            f.write("## Incorrect or Skipped Questions\n\n")
                            for i, item in enumerate(incorrect_questions, 1):
                                f.write(f"### Question {i}\n")
                                f.write(f"- **Question**: {item['question']}\n")
                                f.write(f"- **Your Answer**: {item['your_answer']}\n")
                                f.write(f"- **Correct Answer**: {item['correct_answer']}\n\n")
                        else:
                            f.write("## Feedback\n\n")
                            f.write("Congratulations! You answered all questions correctly!\n")
                    messagebox.showinfo("Success", f"Feedback saved to {file_path}")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to save feedback: {str(e)}")
        
        # Reset UI
        self.ui.show_main_frame()
        for btn in [self.prev_button, self.next_button, self.skip_button, 
                   self.review_button, self.submit_button]:
            btn.config(state="disabled")

if __name__ == "__main__":
    root = tk.Tk()
    app = MockExamApp(root)
    root.mainloop()