# mock_exam_simulator/app.py
import tkinter as tk
from tkinter import filedialog, messagebox, Toplevel, ttk
import platform
from typing import Optional
from .ui.ui_manager import UIManager
from .core.question_bank import QuestionBank
from .core.exam_state import ExamState
from .core.translator import Translator
from .config.config_loader import load_config
try:
    if platform.system() == "Darwin":
        from tkmacosx import Button as MacButton
    else:
        MacButton = None
except ImportError:
    MacButton = None

class MockExamApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.config = load_config()
        self.is_macos = platform.system() == "Darwin" and MacButton is not None
        self.ui = UIManager(root, self.config)
        self.question_bank = QuestionBank()
        self.exam_state = ExamState(self.config)
        self.translator = Translator(
            source_lang=self.config['translator']['from_lang'], 
            target_lang=self.config['translator']['to_lang'])
        self.setup_controls()
        self.root.bind("<<UpdateQuestionDisplay>>", lambda e: self.display_question())
        self.root.bind("<<TranslateQuestion>>", self.handle_translate_question)

    def setup_controls(self):
        style_config = self.config['styles']
        
        if self.is_macos:
            self.import_button = MacButton(self.ui.main_frame, 
                                         text="Import Questions (CSV)",
                                         command=self.import_questions,
                                         font=tuple(style_config['button']['font']),
                                         background=style_config['button']['default_background'],
                                         foreground=style_config['button']['default_foreground'],
                                         activebackground=style_config['button']['active_background'],
                                         activeforeground=style_config['button']['active_foreground'],
                                         borderwidth=style_config['button']['borderwidth'],
                                         relief=style_config['button']['relief'])
        else:
            self.import_button = ttk.Button(self.ui.main_frame, 
                                          text="Import Questions (CSV)", 
                                          command=self.import_questions)
        self.import_button.pack(pady=10)
        
        if self.is_macos:
            self.start_button = MacButton(self.ui.main_frame, 
                                        text="Start Mock Exam",
                                        command=self.start_exam,
                                        state="disabled",
                                        font=tuple(style_config['button']['font']),
                                        background=style_config['button']['default_background'],
                                        foreground=style_config['button']['default_foreground'],
                                        activebackground=style_config['button']['active_background'],
                                        activeforeground=style_config['button']['active_foreground'],
                                        disabledbackground=style_config['button']['disabled_background'],
                                        disabledforeground=style_config['button']['disabled_foreground'],
                                        borderwidth=style_config['button']['borderwidth'],
                                        relief=style_config['button']['relief'])
        else:
            self.start_button = ttk.Button(self.ui.main_frame, 
                                         text="Start Mock Exam", 
                                         command=self.start_exam, 
                                         state="disabled")
        self.start_button.pack(pady=10)
        
        self.button_frame = tk.Frame(self.ui.quiz_frame, bg=self.config['window']['background'])
        self.button_frame.pack(pady=20, side="bottom")

        if self.is_macos:
            self.prev_button = MacButton(self.button_frame, 
                                       text="Prev",
                                       command=self.prev_question,
                                       state="disabled",
                                       font=tuple(style_config['button']['font']),
                                       background=style_config['button']['default_background'],
                                       foreground=style_config['button']['default_foreground'],
                                       activebackground=style_config['button']['active_background'],
                                       activeforeground=style_config['button']['active_foreground'],
                                       disabledbackground=style_config['button']['disabled_background'],
                                       disabledforeground=style_config['button']['disabled_foreground'],
                                       borderwidth=style_config['button']['borderwidth'],
                                       relief=style_config['button']['relief'])
        else:
            self.prev_button = ttk.Button(self.button_frame, 
                                        text="Prev", 
                                        command=self.prev_question, 
                                        state="disabled")
        self.prev_button.pack(side="left", padx=8)
        
        if self.is_macos:
            self.next_button = MacButton(self.button_frame, 
                                       text="Next",
                                       command=self.next_question,
                                       state="disabled",
                                       font=tuple(style_config['button']['font']),
                                       background=style_config['button']['default_background'],
                                       foreground=style_config['button']['default_foreground'],
                                       activebackground=style_config['button']['active_background'],
                                       activeforeground=style_config['button']['active_foreground'],
                                       disabledbackground=style_config['button']['disabled_background'],
                                       disabledforeground=style_config['button']['disabled_foreground'],
                                       borderwidth=style_config['button']['borderwidth'],
                                       relief=style_config['button']['relief'])
        else:
            self.next_button = ttk.Button(self.button_frame, 
                                        text="Next", 
                                        command=self.next_question, 
                                        state="disabled")
        self.next_button.pack(side="left", padx=8)
        
        if self.is_macos:
            self.skip_button = MacButton(self.button_frame, 
                                       text="Skip",
                                       command=self.skip_question,
                                       state="disabled",
                                       font=tuple(style_config['button']['font']),
                                       background=style_config['button']['default_background'],
                                       foreground=style_config['button']['default_foreground'],
                                       activebackground=style_config['button']['active_background'],
                                       activeforeground=style_config['button']['active_foreground'],
                                       disabledbackground=style_config['button']['disabled_background'],
                                       disabledforeground=style_config['button']['disabled_foreground'],
                                       borderwidth=style_config['button']['borderwidth'],
                                       relief=style_config['button']['relief'])
        else:
            self.skip_button = ttk.Button(self.button_frame, 
                                        text="Skip", 
                                        command=self.skip_question, 
                                        state="disabled")
        self.skip_button.pack(side="left", padx=8)
        
        if self.is_macos:
            self.view_answer_button = MacButton(self.button_frame, 
                                              text="View Answer",
                                              command=self.view_answer,
                                              state="disabled",
                                              font=tuple(style_config['button']['font']),
                                              background=style_config['button']['default_background'],
                                              foreground=style_config['button']['default_foreground'],
                                              activebackground=style_config['button']['active_background'],
                                              activeforeground=style_config['button']['active_foreground'],
                                              disabledbackground=style_config['button']['disabled_background'],
                                              disabledforeground=style_config['button']['disabled_foreground'],
                                              borderwidth=style_config['button']['borderwidth'],
                                              relief=style_config['button']['relief'])
        else:
            self.view_answer_button = ttk.Button(self.button_frame, 
                                               text="View Answer", 
                                               command=self.view_answer, 
                                               state="disabled")
        self.view_answer_button.pack(side="left", padx=8)

        if self.is_macos:
            self.flag_button = MacButton(self.button_frame, 
                                       text="Flag Question",
                                       command=self.flag_question,
                                       state="disabled",
                                       font=tuple(style_config['button']['font']),
                                       background=style_config['button']['default_background'],
                                       foreground=style_config['button']['default_foreground'],
                                       activebackground=style_config['button']['active_background'],
                                       activeforeground=style_config['button']['active_foreground'],
                                       disabledbackground=style_config['button']['disabled_background'],
                                       disabledforeground=style_config['button']['disabled_foreground'],
                                       borderwidth=style_config['button']['borderwidth'],
                                       relief=style_config['button']['relief'])
        else:
            self.flag_button = ttk.Button(self.button_frame, 
                                        text="Flag Question", 
                                        command=self.flag_question, 
                                        state="disabled")
        self.flag_button.pack(side="left", padx=8)
        
        if self.is_macos:
            self.review_button = MacButton(self.button_frame, 
                                         text="Review Answers",
                                         command=self.review_answers,
                                         state="disabled",
                                         font=tuple(style_config['button']['font']),
                                         background=style_config['button']['default_background'],
                                         foreground=style_config['button']['default_foreground'],
                                         activebackground=style_config['button']['active_background'],
                                         activeforeground=style_config['button']['active_foreground'],
                                         disabledbackground=style_config['button']['disabled_background'],
                                         disabledforeground=style_config['button']['disabled_foreground'],
                                         borderwidth=style_config['button']['borderwidth'],
                                         relief=style_config['button']['relief'])
        else:
            self.review_button = ttk.Button(self.button_frame, 
                                          text="Review Answers", 
                                          command=self.review_answers, 
                                          state="disabled")
        self.review_button.pack(side="left", padx=8)
        
        if self.is_macos:
            self.submit_button = MacButton(self.button_frame, 
                                         text="Submit",
                                         command=self.submit_exam,
                                         state="disabled",
                                         font=tuple(style_config['button']['font']),
                                         background=style_config['button']['default_background'],
                                         foreground=style_config['button']['default_foreground'],
                                         activebackground=style_config['button']['active_background'],
                                         activeforeground=style_config['button']['active_foreground'],
                                         disabledbackground=style_config['button']['disabled_background'],
                                         disabledforeground=style_config['button']['disabled_foreground'],
                                         borderwidth=style_config['button']['borderwidth'],
                                         relief=style_config['button']['relief'])
        else:
            self.submit_button = ttk.Button(self.button_frame, 
                                          text="Submit", 
                                          command=self.submit_exam, 
                                          state="disabled")
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
        self.exam_state.time_remaining = time_limit * 60
        
        self.ui.show_quiz_frame()
        
        for btn in [self.next_button, self.skip_button, self.review_button, 
                   self.submit_button, self.view_answer_button, self.flag_button]:
            btn.config(state="normal")
            
        self.ui.create_navigation_buttons(len(self.exam_state.questions), self.go_to_question)
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

    def handle_translate_question(self, event):
        question = self.exam_state.questions[self.exam_state.current_index]
        if not question.translated_text or not question.translated_options:
            try:
                question.translated_text = self.translator.translate(question.text)
                question.translated_options = [self.translator.translate(opt) for opt in question.options]
                if not question.translated_options or None in question.translated_options or len(question.translated_options) != len(question.options):
                    raise ValueError("Incomplete or invalid translation of options")
            except Exception as e:
                messagebox.showerror("Translation Error", f"Failed to translate: {str(e)}")
                question.translated_text = question.text
                question.translated_options = question.options.copy()
        self.display_question()

    def display_question(self):
        question = self.exam_state.questions[self.exam_state.current_index]
        self.ui.display_question(question, self.exam_state.current_index)

        self.prev_button.config(state="normal" if self.exam_state.current_index > 0 else "disabled")
        self.next_button.config(state="normal" if self.exam_state.current_index < len(self.exam_state.questions) - 1 else "disabled")
        self.skip_button.config(state="normal")
        self.ui.update_progress(self.exam_state.current_index, len(self.exam_state.questions))
        self.ui.update_navigation_buttons(self.exam_state.questions, self.exam_state.current_index)

        self.flag_button.config(text="Unflag Question" if question.flagged else "Flag Question")

    def save_current_answer(self):
        question = self.exam_state.questions[self.exam_state.current_index]
        selected = []

        if question.is_multiple_choice:
            selected = [opt for opt, var in self.ui.selected_answers.items() if var.get()]
        else:
            answer = self.ui.selected_answer.get()
            selected = [answer] if answer else []

        if self.ui.is_translated and question.translated_options:
            english_selections = []
            for sel in selected:
                try:
                    idx = question.translated_options.index(sel)
                    english_selections.append(question.options[idx])
                except (ValueError, IndexError):
                    continue
            selected = english_selections

        question.user_answers = selected if selected else None

    def go_to_question(self, index: Optional[int] = None):
        self.save_current_answer()
        self.ui.update_navigation_buttons(self.exam_state.questions, self.exam_state.current_index)
        if index is None:
            self.submit_exam()
        else:
            self.exam_state.current_index = index
            self.display_question()

    def next_question(self):
        self.save_current_answer()
        self.ui.update_navigation_buttons(self.exam_state.questions, self.exam_state.current_index)
        
        if self.exam_state.current_index < len(self.exam_state.questions) - 1:
            self.exam_state.current_index += 1
            self.display_question()
        else:
            self.next_button.config(state="disabled")
            self.skip_button.config(state="disabled")
            messagebox.showinfo("Info", "This is the last question. Please submit the exam.")

    def prev_question(self):
        self.save_current_answer()
        self.ui.update_navigation_buttons(self.exam_state.questions, self.exam_state.current_index)
        self.exam_state.current_index -= 1
        self.display_question()

    def skip_question(self):
        self.exam_state.questions[self.exam_state.current_index].user_answers = None
        self.ui.update_navigation_buttons(self.exam_state.questions, self.exam_state.current_index)
        self.next_question()

    def flag_question(self):
        question = self.exam_state.questions[self.exam_state.current_index]
        self.save_current_answer()
        question.flagged = not question.flagged
        self.display_question()
        self.ui.update_navigation_buttons(self.exam_state.questions, self.exam_state.current_index)

    def view_answer(self):
        question = self.exam_state.questions[self.exam_state.current_index]
        if not question.answer_viewed:
            question.answer_viewed = True
            self.exam_state.penalties += 1
        question.user_answers = []
        correct_answers = ", ".join(question.correct_answers)
        messagebox.showinfo(
            "Correct Answer",
            f"Correct Answer(s):\n{correct_answers}\n\nNote: This question is marked as incorrect, and 1 point has been deducted from your score."
        )
        self.ui.update_navigation_buttons(self.exam_state.questions, self.exam_state.current_index)

    def review_answers(self):
        self.stop_timer()
        review_window = Toplevel(self.root)
        review_window.title("Review Answers")
        review_window.geometry("600x600")
        review_window.configure(bg=self.config['window']['background'])
        
        listbox = tk.Listbox(review_window, width=80, height=25, font=("Segoe UI", 12),
                             bg=self.config['window']['background'], fg="#2d2d2d", selectbackground="#007bff")
        listbox.pack(pady=15, padx=15)
        
        for i, q in enumerate(self.exam_state.questions):
            status = ", ".join(q.user_answers) if q.user_answers else "Skipped or Viewed"
            if q.answer_viewed:
                status += " (Marked incorrect; 1 point deducted)"
            if q.flagged:
                status += " ⚑"
            listbox.insert(tk.END, f"Q{i+1}: {q.text[:50]}... -> {status}")
        
        def go_to_question(event):
            if selection := listbox.curselection():
                self.exam_state.current_index = selection[0]
                self.display_question()
                review_window.destroy()
                self.start_timer()
        
        listbox.bind("<Double-1>", go_to_question)

        style_config = self.config['styles']
        if self.is_macos:
            close_button = MacButton(review_window, 
                                   text="Close",
                                   command=lambda: [review_window.destroy(), self.start_timer()],
                                   font=tuple(style_config['button']['font']),
                                   background=style_config['button']['default_background'],
                                   foreground=style_config['button']['default_foreground'],
                                   activebackground=style_config['button']['active_background'],
                                   activeforeground=style_config['button']['active_foreground'],
                                   borderwidth=style_config['button']['borderwidth'],
                                   relief=style_config['button']['relief'])
        else:
            close_button = ttk.Button(review_window, 
                                    text="Close", 
                                    command=lambda: [review_window.destroy(), self.start_timer()])
        close_button.pack(pady=10)

    def submit_exam(self):
        self.stop_timer()
        self.save_current_answer()
        self.ui.update_navigation_buttons(self.exam_state.questions, self.exam_state.current_index)
        
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
        
        flagged_questions = [
            {
                'question': q.text,
                'your_answers': ", ".join(q.user_answers) if q.user_answers else "Skipped or Viewed",
                'correct_answers': ", ".join(q.correct_answers),
                'answer_viewed': q.answer_viewed,
                'is_correct': q.user_answers and sorted(q.user_answers) == sorted(q.correct_answers)
            } for q in self.exam_state.questions if q.flagged
        ]
        
        incorrect_questions = [
            {
                'question': q.text,
                'your_answers': ", ".join(q.user_answers) if q.user_answers else "Skipped or Viewed",
                'correct_answers': ", ".join(q.correct_answers),
                'answer_viewed': q.answer_viewed,
                'flagged': q.flagged
            } for q in self.exam_state.questions
            if not q.user_answers or sorted(q.user_answers) != sorted(q.correct_answers)
        ]
        
        flagged_and_incorrect_questions = [
            {
                'question': q.text,
                'your_answers': ", ".join(q.user_answers) if q.user_answers else "Skipped or Viewed",
                'correct_answers': ", ".join(q.correct_answers),
                'answer_viewed': q.answer_viewed
            } for q in self.exam_state.questions
            if q.flagged and (not q.user_answers or sorted(q.user_answers) != sorted(q.correct_answers))
        ]
        
        total = len(self.exam_state.questions)
        percentage = (self.exam_state.score / total) * 100 if total > 0 else 0
        messagebox.showinfo("Results", 
                          f"Exam Completed!\n"
                          f"Correct Answers: {correct_count}/{total}\n"
                          f"Penalties for Viewing Answers: {self.exam_state.penalties}\n"
                          f"Final Score: {self.exam_state.score}/{total}\n"
                          f"Percentage: {percentage:.2f}%")
        
        if incorrect_questions or flagged_questions:
            feedback_window = Toplevel(self.root)
            feedback_window.title("Feedback: Incorrect/Skipped Questions")
            feedback_window.geometry("800x700")
            feedback_window.configure(bg=self.config['window']['background'])
            
            listbox = tk.Listbox(feedback_window, width=100, height=30, font=("Segoe UI", 12),
                               bg=self.config['window']['background'], fg="#2d2d2d")
            listbox.pack(pady=15, padx=15)
            
            for i, item in enumerate(incorrect_questions, 1):
                listbox.insert(tk.END, f"Q{i}: {item['question'][:100]}...")
                listbox.insert(tk.END, f"  Your Answers: {item['your_answers']}")
                if item['answer_viewed']:
                    listbox.insert(tk.END, f"  (Marked incorrect because answer was viewed; 1 point deducted)")
                if item['flagged']:
                    listbox.insert(tk.END, f"  (Flagged)")
                listbox.insert(tk.END, f"  Correct Answers: {item['correct_answers']}")
                listbox.insert(tk.END, "")
            
            scrollbar = tk.Scrollbar(feedback_window, orient="vertical")
            scrollbar.config(command=listbox.yview)
            scrollbar.pack(side="right", fill="y")
            listbox.config(yscrollcommand=scrollbar.set)
            
            style_config = self.config['styles']
            if self.is_macos:
                close_button = MacButton(feedback_window, 
                                       text="Close",
                                       command=feedback_window.destroy,
                                       font=tuple(style_config['button']['font']),
                                       background=style_config['button']['default_background'],
                                       foreground=style_config['button']['default_foreground'],
                                       activebackground=style_config['button']['active_background'],
                                       activeforeground=style_config['button']['active_foreground'],
                                       borderwidth=style_config['button']['borderwidth'],
                                       relief=style_config['button']['relief'])
            else:
                close_button = ttk.Button(feedback_window, 
                                        text="Close", 
                                        command=feedback_window.destroy)
            close_button.pack(pady=10)
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

                        f.write("## Flagged Questions\n\n")
                        if flagged_questions:
                            for i, item in enumerate(flagged_questions, 1):
                                f.write(f"### Question {i} (Flagged)\n")
                                f.write(f"- **Question**: {item['question']}\n")
                                f.write(f"- **Your Answers**: {item['your_answers']}\n")
                                if item['answer_viewed']:
                                    f.write(f"- **Note**: Marked incorrect because answer was viewed; 1 point deducted\n")
                                f.write(f"- **Correct Answers**: {item['correct_answers']}\n")
                                f.write(f"- **Status**: {'Correct' if item['is_correct'] else 'Incorrect'}\n\n")
                        else:
                            f.write("No questions were flagged.\n\n")

                        f.write("## Incorrect or Skipped Questions\n\n")
                        if incorrect_questions:
                            for i, item in enumerate(incorrect_questions, 1):
                                f.write(f"### Question {i} (Incorrect or Skipped)\n")
                                f.write(f"- **Question**: {item['question']}\n")
                                f.write(f"- **Your Answers**: {item['your_answers']}\n")
                                if item['answer_viewed']:
                                    f.write(f"- **Note**: Marked incorrect because answer was viewed; 1 point deducted\n")
                                if item['flagged']:
                                    f.write(f"- **Note**: This question was flagged\n")
                                f.write(f"- **Correct Answers**: {item['correct_answers']}\n\n")
                        else:
                            f.write("No incorrect or skipped questions.\n\n")

                        f.write("## Flagged and Incorrect Questions\n\n")
                        if flagged_and_incorrect_questions:
                            for i, item in enumerate(flagged_and_incorrect_questions, 1):
                                f.write(f"### Question {i} (Flagged and Incorrect)\n")
                                f.write(f"- **Question**: {item['question']}\n")
                                f.write(f"- **Your Answers**: {item['your_answers']}\n")
                                if item['answer_viewed']:
                                    f.write(f"- **Note**: Marked incorrect because answer was viewed; 1 point deducted\n")
                                f.write(f"- **Correct Answers**: {item['correct_answers']}\n\n")
                        else:
                            f.write("No questions were both flagged and incorrect.\n\n")

                        f.write("## Notes\n")
                        f.write("- Questions marked as 'Flagged' were highlighted by you during the exam for review.\n")
                        f.write("- Incorrect questions include those with wrong answers, skipped, or where the answer was viewed.\n")
                        f.write("- The 'Flagged and Incorrect' section lists questions that meet both criteria.\n")
                    messagebox.showinfo("Success", f"Feedback saved to {file_path}")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to save feedback: {str(e)}")
        
        self.ui.show_main_frame()
        for btn in [self.prev_button, self.next_button, self.skip_button, 
                   self.review_button, self.submit_button, self.view_answer_button, self.flag_button]:
            btn.config(state="disabled")