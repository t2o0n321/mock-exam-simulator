#!/Users/guo/Downloads/mock-exam/mock-venv/bin/python3

import tkinter as tk
from tkinter import filedialog, messagebox, Toplevel, ttk
import pandas as pd
from dataclasses import dataclass
from typing import List, Optional
import random
from pathlib import Path
import ast

@dataclass
class Question:
    text: str
    options: List[str]
    correct_answers: List[str]
    is_multiple_choice: bool
    user_answers: Optional[List[str]] = None
    answer_viewed: bool = False

class QuestionBank:
    def __init__(self):
        self.questions: List[Question] = []

    def load_from_csv(self, file_path: str) -> bool:
        try:
            df = pd.read_csv(file_path)
            required_columns = ["question", "options", "correct"]
            if not all(col in df.columns for col in required_columns):
                raise ValueError("CSV missing required columns: 'question', 'options', 'correct'")
            
            self.questions = []
            for _, row in df.iterrows():
                try:
                    options = ast.literal_eval(row["options"])
                    if not isinstance(options, list) or not all(isinstance(opt, str) for opt in options):
                        raise ValueError("Options must be a list of strings")
                except (ValueError, SyntaxError) as e:
                    raise ValueError(f"Invalid options format for question: {row['question']}")
                
                if not options:
                    raise ValueError(f"No valid options for question: {row['question']}")
                
                try:
                    if pd.isna(row["correct"]):
                        raise ValueError("Correct answer indices cannot be empty")
                    correct_indices = [int(idx.strip()) for idx in str(row["correct"]).split(",")]
                    for idx in correct_indices:
                        if idx < 0 or idx >= len(options):
                            raise ValueError(f"Correct index {idx} out of range for options")
                    correct_indices = list(set(correct_indices))
                    if len(correct_indices) > 6:
                        raise ValueError("Maximum 6 correct answers allowed")
                    if not correct_indices:
                        raise ValueError("At least one correct answer required")
                    correct_answers = [options[idx] for idx in correct_indices]
                except (ValueError, TypeError) as e:
                    raise ValueError(f"Invalid correct answer indices for question: {row['question']}: {str(e)}")
                
                self.questions.append(
                    Question(
                        text=str(row["question"]),
                        options=options,
                        correct_answers=correct_answers,
                        is_multiple_choice=len(correct_answers) > 1
                    )
                )
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
        self.penalties: int = 0  # Track penalties for viewing answers
        self.questions: List[Question] = []
        self.time_remaining: int = 0
        self.timer_id: Optional[str] = None

    def reset(self):
        self.current_index = 0
        self.score = 0
        self.penalties = 0
        self.questions = []
        self.time_remaining = 0
        self.timer_id = None

class UIManager:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.main_frame = tk.Frame(root, bg="#ffffff")
        self.quiz_frame = tk.Frame(root, bg="#ffffff")
        self.selected_answer = tk.StringVar()
        self.selected_answers = {}
        self.option_widgets: List[ttk.Radiobutton | ttk.Checkbutton] = []
        self.option_frames: List[tk.Frame] = []
        self.options_frame = None
        self.options_canvas = None
        self.options_inner_frame = None
        self.timer_label = None
        self.progress_bar = None
        self.setup_ui()

    def setup_ui(self):
        self.root.title("Mock Exam Simulator")
        self.root.geometry("900x700")
        self.root.configure(bg="#ffffff")

        style = ttk.Style()
        style.configure("TButton", font=("Segoe UI", 11, "bold"), padding=10)
        style.configure("TLabel", background="#ffffff", font=("Segoe UI", 12))
        style.configure("TEntry", padding=5)
        style.configure("TRadiobutton", background="#ffffff", font=("Segoe UI", 12))
        style.configure("TCheckbutton", background="#ffffff", font=("Segoe UI", 12))
        style.configure("TProgressbar", thickness=20)

        style.configure("TButton", borderwidth=0, relief="flat")
        style.map("TButton",
                 background=[("active", "#0056b3"), ("!active", "#007bff"), ("disabled", "#adb5bd")],
                 foreground=[("active", "white"), ("!active", "white"), ("disabled", "white")])
        style.configure("TProgressbar", background="#007bff", troughcolor="#e9ecef")

        self.main_frame.pack(pady=50, padx=50, fill="both", expand=True)
        main_card = tk.Frame(self.main_frame, bg="#ffffff", relief="solid", borderwidth=1,
                           highlightbackground="#dee2e6", highlightthickness=1)
        main_card.pack(pady=20, padx=20, fill="both", expand=True)
        
        tk.Label(main_card, text="Mock Exam Simulator", font=("Segoe UI", 28, "bold"),
                bg="#ffffff", fg="#2d2d2d").pack(pady=30)
        
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
        
        self.timer_label = tk.Label(self.quiz_frame, text="Time Remaining: 00:00", 
                                  font=("Segoe UI", 16, "bold"), bg="#ffffff", fg="#e63946")
        self.timer_label.pack(pady=15)
        
        self.progress_bar = ttk.Progressbar(self.quiz_frame, orient="horizontal", mode="determinate")
        self.progress_bar.pack(fill="x", padx=30, pady=10)
        
        question_card = tk.Frame(self.quiz_frame, bg="#ffffff", relief="solid", borderwidth=1,
                               highlightbackground="#dee2e6", highlightthickness=1)
        question_card.pack(pady=10, padx=30, fill="both", expand=True)
        
        self.question_label = tk.Label(question_card, text="", font=("Segoe UI", 16, "bold"),
                                     bg="#ffffff", fg="#2d2d2d", wraplength=700, justify="left")
        self.question_label.pack(pady=20, padx=20, anchor="w")
        
        self.options_canvas = tk.Canvas(question_card, bg="#ffffff", highlightthickness=0)
        scrollbar = ttk.Scrollbar(question_card, orient="vertical", command=self.options_canvas.yview)
        self.options_inner_frame = tk.Frame(self.options_canvas, bg="#ffffff")
        
        self.options_inner_frame.bind(
            "<Configure>",
            lambda e: self.options_canvas.configure(scrollregion=self.options_canvas.bbox("all"))
        )
        
        self.options_canvas.create_window((0, 0), window=self.options_inner_frame, anchor="nw")
        self.options_canvas.configure(yscrollcommand=scrollbar.set)
        
        self.options_canvas.pack(side="left", fill="both", expand=True, padx=20, pady=10)
        scrollbar.pack(side="right", fill="y")

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

    def clear_options(self):
        for widget in self.option_widgets:
            widget.destroy()
        for frame in self.option_frames:
            frame.destroy()
        self.option_widgets = []
        self.option_frames = []
        self.selected_answers.clear()

    def create_options(self, question: Question):
        self.clear_options()
        for option in question.options:
            option_frame = tk.Frame(self.options_inner_frame, bg="#ffffff", relief="solid", borderwidth=1,
                                  highlightbackground="#dee2e6", highlightthickness=1)
            option_frame.pack(fill="x", pady=5)
            option_frame.bind("<Enter>", lambda e, f=option_frame: f.config(bg="#f8f9fa"))
            option_frame.bind("<Leave>", lambda e, f=option_frame: f.config(bg="#ffffff"))
            
            if question.is_multiple_choice:
                var = tk.BooleanVar()
                self.selected_answers[option] = var
                widget = ttk.Checkbutton(option_frame, text=option, variable=var)
            else:
                widget = ttk.Radiobutton(option_frame, text=option, variable=self.selected_answer, value=option)
            
            widget.pack(anchor="w", padx=15, pady=10)
            self.option_widgets.append(widget)
            self.option_frames.append(option_frame)

class MockExamApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.ui = UIManager(root)
        self.question_bank = QuestionBank()
        self.exam_state = ExamState()
        self.setup_controls()

    def setup_controls(self):
        self.import_button = ttk.Button(self.ui.main_frame, text="Import Questions (CSV)", 
                                      command=self.import_questions)
        self.import_button.pack(pady=10)
        
        self.start_button = ttk.Button(self.ui.main_frame, text="Start Mock Exam", 
                                     command=self.start_exam, state="disabled")
        self.start_button.pack(pady=10)
        
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
        
        self.view_answer_button = ttk.Button(button_frame, text="View Answer", 
                                            command=self.view_answer, state="disabled")
        self.view_answer_button.pack(side="left", padx=8)
        
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
        for q in self.exam_state.questions:
            q.answer_viewed = False
        self.exam_state.time_remaining = time_limit * 60
        
        self.ui.show_quiz_frame()
        
        for btn in [self.next_button, self.skip_button, self.review_button, self.submit_button, self.view_answer_button]:
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
        
        self.ui.create_options(question)
        
        if question.is_multiple_choice:
            for option, var in self.ui.selected_answers.items():
                var.set(option in (question.user_answers or []))
        else:
            self.ui.selected_answer.set(question.user_answers[0] if question.user_answers else "")
        
        self.prev_button.config(state="normal" if self.exam_state.current_index > 0 else "disabled")
        self.next_button.config(state="normal")
        self.skip_button.config(state="normal")
        self.ui.update_progress(self.exam_state.current_index, len(self.exam_state.questions))

    def save_current_answer(self):
        question = self.exam_state.questions[self.exam_state.current_index]
        if question.is_multiple_choice:
            selected = [opt for opt, var in self.ui.selected_answers.items() if var.get()]
            question.user_answers = selected if selected else None
        else:
            answer = self.ui.selected_answer.get()
            question.user_answers = [answer] if answer else None

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
        self.exam_state.questions[self.exam_state.current_index].user_answers = None
        self.next_question()

    def view_answer(self):
        question = self.exam_state.questions[self.exam_state.current_index]
        if not question.answer_viewed:  # Only penalize once
            question.answer_viewed = True
            self.exam_state.penalties += 1
        question.user_answers = []
        correct_answers = ", ".join(question.correct_answers)
        messagebox.showinfo(
            "Correct Answer",
            f"Correct Answer(s):\n{correct_answers}\n\nNote: This question is marked as incorrect, and 1 point has been deducted from your score."
        )

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
            status = ", ".join(q.user_answers) if q.user_answers else "Skipped or Viewed"
            if q.answer_viewed:
                status += " (Marked incorrect; 1 point deducted)"
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
        
        unanswered = [i for i, q in enumerate(self.exam_state.questions) if not q.user_answers and not q.answer_viewed]
        if unanswered:
            if messagebox.askyesno("Unanswered Questions", 
                                 f"You have {len(unanswered)} unanswered questions. Review them now?"):
                self.review_answers()
                return
        
        correct_count = sum(
            1 for q in self.exam_state.questions
            if q.user_answers and sorted(q.user_answers) == sorted(q.correct_answers)
        )
        
        self.exam_state.score = correct_count - self.exam_state.penalties
        if self.exam_state.score < 0:
            self.exam_state.score = 0
        
        incorrect_questions = [
            {
                'question': q.text,
                'your_answers': ", ".join(q.user_answers) if q.user_answers else "Skipped or Viewed",
                'correct_answers': ", ".join(q.correct_answers),
                'answer_viewed': q.answer_viewed
            } for q in self.exam_state.questions
            if not q.user_answers or sorted(q.user_answers) != sorted(q.correct_answers)
        ]
        
        total = len(self.exam_state.questions)
        percentage = (self.exam_state.score / total) * 100 if total > 0 else 0
        messagebox.showinfo("Results", 
                          f"Exam Completed!\n"
                          f"Correct Answers: {correct_count}/{total}\n"
                          f"Penalties for Viewing Answers: {self.exam_state.penalties}\n"
                          f"Final Score: {self.exam_state.score}/{total}\n"
                          f"Percentage: {percentage:.2f}%")
        
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
                listbox.insert(tk.END, f"  Your Answers: {item['your_answers']}")
                if item['answer_viewed']:
                    listbox.insert(tk.END, f"  (Marked incorrect because answer was viewed; 1 point deducted)")
                listbox.insert(tk.END, f"  Correct Answers: {item['correct_answers']}")
                listbox.insert(tk.END, "")
            
            scrollbar = tk.Scrollbar(feedback_window, orient="vertical")
            scrollbar.config(command=listbox.yview)
            scrollbar.pack(side="right", fill="y")
            listbox.config(yscrollcommand=scrollbar.set)
            
            ttk.Button(feedback_window, text="Close", command=feedback_window.destroy).pack(pady=10)
        else:
            messagebox.showinfo("Feedback", "Congratulations! You answered all questions correctly!")
        
        if messagebox.askyesno("Save Feedback", "Would you like to save the feedback as a Markdown file?"):
            file_path = filedialog.asksaveasfilename(defaultextension=".md", 
                                                  filetypes=[("Markdown files", "*.md")])
            if file_path:
                try:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(f"# Mock Exam Feedback\n\n")
                        f.write(f"**Correct Answers**: {correct_count}/{total}\n")
                        f.write(f"**Penalties for Viewing Answers**: {self.exam_state.penalties}\n")
                        f.write(f"**Final Score**: {self.exam_state.score}/{total}\n")
                        f.write(f"**Percentage**: {percentage:.2f}%\n\n")
                        if incorrect_questions:
                            f.write("## Incorrect or Skipped Questions\n\n")
                            for i, item in enumerate(incorrect_questions, 1):
                                f.write(f"### Question {i}\n")
                                f.write(f"- **Question**: {item['question']}\n")
                                f.write(f"- **Your Answers**: {item['your_answers']}\n")
                                if item['answer_viewed']:
                                    f.write(f"- **Note**: Marked incorrect because answer was viewed; 1 point deducted\n")
                                f.write(f"- **Correct Answers**: {item['correct_answers']}\n\n")
                        else:
                            f.write("## Feedback\n\n")
                            f.write("Congratulations! You answered all questions correctly!\n")
                    messagebox.showinfo("Success", f"Feedback saved to {file_path}")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to save feedback: {str(e)}")
        
        self.ui.show_main_frame()
        for btn in [self.prev_button, self.next_button, self.skip_button, 
                   self.review_button, self.submit_button, self.view_answer_button]:
            btn.config(state="disabled")

if __name__ == "__main__":
    root = tk.Tk()
    app = MockExamApp(root)
    root.mainloop()