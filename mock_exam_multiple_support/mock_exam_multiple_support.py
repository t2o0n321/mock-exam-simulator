import tkinter as tk
from tkinter import filedialog, messagebox, Toplevel, ttk
import pandas as pd
from dataclasses import dataclass
from typing import List, Optional
import random
from pathlib import Path
import ast
import yaml
import platform
import os
from deep_translator import GoogleTranslator

# Conditionally import tkmacosx for macOS users
try:
    if platform.system() == "Darwin":
        from tkmacosx import Button as MacButton
    else:
        MacButton = None
except ImportError:
    MacButton = None

@dataclass
class Question:
    text: str
    options: List[str]
    correct_answers: List[str]
    is_multiple_choice: bool
    user_answers: Optional[List[str]] = None
    answer_viewed: bool = False
    flagged: bool = False
    translated_text: Optional[str] = None
    translated_options: Optional[List[str]] = None

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
                        is_multiple_choice=len(correct_answers) > 1,
                        user_answers=None,
                        answer_viewed=False,
                        flagged=False,
                        translated_text=None,
                        translated_options=None
                    )
                )
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Failed to import questions: {str(e)}")
            return False

    def get_random_questions(self, count: int) -> List[Question]:
        sample_size = min(len(self.questions), count)
        selected_questions = random.sample(self.questions, sample_size)
        for q in selected_questions:
            q.user_answers = None
            q.answer_viewed = False
            q.flagged = False
            q.translated_text = None
            q.translated_options = None
        return selected_questions

class ExamState:
    def __init__(self, config):
        self.current_index: int = 0
        self.score: int = 0
        self.penalties: int = 0
        self.questions: List[Question] = []
        self.time_remaining: int = 0
        self.timer_id: Optional[str] = None
        self.base_mark: float = config['exam']['base_mark']

    def reset(self):
        self.current_index = 0
        self.score = 0
        self.penalties = 0
        self.questions = []
        self.time_remaining = 0
        self.timer_id = None

class UIManager:
    def __init__(self, root: tk.Tk, config):
        self.root = root
        self.config = config
        self.is_macos = platform.system() == "Darwin" and MacButton is not None
        self.main_frame = tk.Frame(root, bg=config['window']['background'])
        self.quiz_frame = tk.Frame(root, bg=config['window']['background'])
        self.selected_answer = tk.StringVar()
        self.selected_answers = {}
        self.option_widgets: List[ttk.Radiobutton | ttk.Checkbutton] = []
        self.option_frames: List[tk.Frame] = []
        self.nav_buttons: List = []
        self.options_frame = None
        self.options_canvas = None
        self.options_inner_frame = None
        self.options_scrollbar = None
        self.question_canvas = None
        self.question_inner_frame = None
        self.question_scrollbar = None
        self.timer_label = None
        self.progress_bar = None
        self.nav_frame = None
        self.nav_visible = config['navigation']['default_visible']
        self.toggle_button = None
        self.nav_container = None
        self.nav_canvas = None
        self.nav_scrollbar = None
        self.is_translated = False
        self.translate_button = None
        self.setup_ui()

    def update_wraplength(self, event=None):
        window_width = self.root.winfo_width()
        padding = 2 * 30 + 2 * 20 + 25
        available_width = max(window_width - padding, 300)
        wraplength = int(available_width * 0.9)
        self.question_label.config(wraplength=wraplength)

    def setup_ui(self):
        window_config = self.config['window']
        style_config = self.config['styles']
        nav_config = self.config['navigation']
        question_bar_config = self.config['question_bar']
        option_display_config = self.config['option_display']

        self.root.title(window_config['title'])
        self.root.geometry(f"{window_config['width']}x{window_config['height']}")
        self.root.configure(bg=window_config['background'])

        self.root.bind("<Configure>", self.update_wraplength)

        style = ttk.Style()
        style.configure("TButton", 
                       font=tuple(style_config['button']['font']), 
                       padding=style_config['button']['padding'],
                       borderwidth=style_config['button']['borderwidth'],
                       relief=style_config['button']['relief'])
        style.map("TButton",
                 background=[
                     ("active", style_config['button']['active_background']),
                     ("!active", style_config['button']['default_background']),
                     ("disabled", style_config['button']['disabled_background'])
                 ],
                 foreground=[
                     ("active", style_config['button']['active_foreground']),
                     ("!active", style_config['button']['default_foreground']),
                     ("disabled", style_config['button']['disabled_foreground'])
                 ])
        style.configure("TLabel", 
                       background=style_config['label']['background'], 
                       font=tuple(style_config['label']['font']))
        style.configure("TEntry", padding=style_config['entry']['padding'])
        style.configure("TRadiobutton", 
                       background=style_config['radiobutton']['background'], 
                       font=tuple(style_config['radiobutton']['font']))
        style.configure("TCheckbutton", 
                       background=style_config['checkbutton']['background'], 
                       font=tuple(style_config['checkbutton']['font']))
        style.configure("TProgressbar", 
                       thickness=style_config['progressbar']['thickness'],
                       background=style_config['progressbar']['background'], 
                       troughcolor=style_config['progressbar']['troughcolor'])
        
        if not self.is_macos:
            style.configure("Answered.TButton", background="#a3e635")
            style.configure("Active.TButton", background=style_config['active_button']['background'])
            style.configure("Viewed.TButton", background=style_config['viewed_button']['background'])
            style.configure("Flagged.TButton", background="#ff9500")

        style.configure("Option.TRadiobutton", 
                       background=style_config['radiobutton']['background'], 
                       font=("Segoe UI", option_display_config['font_size']))
        style.configure("Option.TCheckbutton", 
                       background=style_config['checkbutton']['background'], 
                       font=("Segoe UI", option_display_config['font_size']))

        self.main_frame.pack(pady=50, padx=50, fill="both", expand=True)
        main_card = tk.Frame(self.main_frame, bg=window_config['background'], relief="solid", borderwidth=1,
                           highlightbackground="#dee2e6", highlightthickness=1)
        main_card.pack(pady=20, padx=20, fill="both", expand=True)
        
        tk.Label(main_card, text="Mock Exam Simulator", font=("Segoe UI", 28, "bold"),
                bg=window_config['background'], fg="#2d2d2d").pack(pady=30)
        
        settings_frame = tk.Frame(main_card, bg=window_config['background'])
        settings_frame.pack(pady=10)
        
        tk.Label(settings_frame, text="Number of Questions:", font=("Segoe UI", 14), 
                bg=window_config['background'], fg="#2d2d2d").grid(row=0, column=0, padx=10, pady=10)
        self.num_questions_entry = ttk.Entry(settings_frame, width=10, font=("Segoe UI", 12))
        self.num_questions_entry.grid(row=0, column=1, padx=10, pady=10)
        self.num_questions_entry.insert(0, str(self.config['exam']['default_questions']))
        self.num_questions_entry.configure(style="Custom.TEntry")
        style.configure("Custom.TEntry", 
                       bordercolor=style_config['entry']['bordercolor'], 
                       relief=style_config['entry']['relief'], 
                       borderwidth=style_config['entry']['borderwidth'])
        
        tk.Label(settings_frame, text="Time Limit (minutes):", font=("Segoe UI", 14), 
                bg=window_config['background'], fg="#2d2d2d").grid(row=1, column=0, padx=10, pady=10)
        self.time_limit_entry = ttk.Entry(settings_frame, width=10, font=("Segoe UI", 12))
        self.time_limit_entry.grid(row=1, column=1, padx=10, pady=10)
        self.time_limit_entry.insert(0, str(self.config['exam']['default_time_limit_minutes']))
        self.time_limit_entry.configure(style="Custom.TEntry")

        content_frame = tk.Frame(self.quiz_frame, bg=window_config['background'])
        content_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.timer_label = tk.Label(content_frame, text="Time Remaining: 00:00", 
                                  font=("Segoe UI", 16, "bold"), bg=window_config['background'], fg="#e63946")
        self.timer_label.pack(pady=15)

        self.progress_bar = ttk.Progressbar(content_frame, orient="horizontal", mode="determinate")
        self.progress_bar.pack(fill="x", padx=30, pady=10)

        if self.is_macos:
            self.translate_button = MacButton(content_frame, 
                                            text="Translate to " + self.config['translator']['to_lang'],
                                            command=self.toggle_translation,
                                            font=tuple(style_config['button']['font']),
                                            background=style_config['button']['default_background'],
                                            foreground=style_config['button']['default_foreground'],
                                            activebackground=style_config['button']['active_background'],
                                            activeforeground=style_config['button']['active_foreground'],
                                            borderwidth=style_config['button']['borderwidth'],
                                            relief=style_config['button']['relief'])
        else:
            self.translate_button = ttk.Button(content_frame, 
                                             text="Translate to " + self.config['translator']['to_lang'], 
                                             command=self.toggle_translation)
        self.translate_button.pack(pady=1)

        question_card = tk.Frame(content_frame, bg=window_config['background'], relief="solid", borderwidth=1,
                               highlightbackground="#dee2e6", highlightthickness=1)
        question_card.pack(pady=10, padx=30, fill="both", expand=True)

        header_frame = tk.Frame(question_card, bg=window_config['background'])
        header_frame.pack(fill="x", padx=20, pady=10)

        self.question_canvas = tk.Canvas(header_frame, bg=window_config['background'], highlightthickness=0, height=question_bar_config['height'])
        self.question_scrollbar = ttk.Scrollbar(header_frame, orient="vertical", command=self.question_canvas.yview)
        self.question_inner_frame = tk.Frame(self.question_canvas, bg=window_config['background'])

        self.question_inner_frame.bind(
            "<Configure>",
            lambda e: self.question_canvas.configure(scrollregion=self.question_canvas.bbox("all"))
        )

        self.question_canvas.create_window((0, 0), window=self.question_inner_frame, anchor="nw")
        self.question_canvas.configure(yscrollcommand=self.question_scrollbar.set)

        self.question_canvas.pack(side="left", fill="both", expand=True)
        self.question_scrollbar.pack(side="right", fill="y")
        self.question_canvas.bind("<Configure>", lambda e: self.update_question_scrollbar_visibility())

        self.question_label = tk.Label(self.question_inner_frame, text="", font=("Segoe UI", question_bar_config['font_size'], "bold"),
                                     bg=window_config['background'], fg="#2d2d2d", wraplength=300, justify="left")
        self.question_label.pack(anchor="w")

        self.root.after(100, self.update_wraplength)

        self.options_canvas = tk.Canvas(question_card, bg=window_config['background'], highlightthickness=0)
        self.options_scrollbar = ttk.Scrollbar(question_card, orient="vertical", command=self.options_canvas.yview)
        self.options_inner_frame = tk.Frame(self.options_canvas, bg=window_config['background'])

        self.options_inner_frame.bind(
            "<Configure>",
            lambda e: self.options_canvas.configure(scrollregion=self.options_canvas.bbox("all"))
        )

        self.options_canvas.create_window((0, 0), window=self.options_inner_frame, anchor="nw")
        self.options_canvas.configure(yscrollcommand=self.options_scrollbar.set)

        self.options_canvas.pack(side="left", fill="both", expand=True, padx=20, pady=10)
        self.options_scrollbar.pack(side="right", fill="y")
        self.options_canvas.bind("<Configure>", lambda e: self.update_scrollbar_visibility())

        if self.is_macos:
            self.options_canvas.bind_all("<MouseWheel>", self._on_options_mousewheel)
            self.options_canvas.bind_all("<Shift-MouseWheel>", lambda event: None)
        else:
            self.options_canvas.bind_all("<MouseWheel>", self._on_options_mousewheel)

        if self.is_macos:
            self.toggle_button = MacButton(content_frame, 
                                         text="Show Navigation" if not self.nav_visible else "Hide Navigation",
                                         command=self.toggle_navigation,
                                         font=tuple(style_config['button']['font']),
                                         background=style_config['button']['default_background'],
                                         foreground=style_config['button']['default_foreground'],
                                         activebackground=style_config['button']['active_background'],
                                         activeforeground=style_config['button']['active_foreground'],
                                         borderwidth=style_config['button']['borderwidth'],
                                         relief=style_config['button']['relief'])
        else:
            self.toggle_button = ttk.Button(content_frame, 
                                          text="Show Navigation" if not self.nav_visible else "Hide Navigation", 
                                          command=self.toggle_navigation)
        self.toggle_button.pack(side="bottom", pady=5)

        self.nav_frame = tk.Frame(content_frame, bg=nav_config['background'])
        if self.nav_visible:
            self.nav_frame.pack(side="bottom", fill="x", padx=10, pady=5)

        tk.Label(self.nav_frame, text="Quiz Navigation", font=("Segoe UI", 8, "bold"),
                 bg=nav_config['background'], fg="#2d2d2d").pack(pady=3)

        self.nav_canvas = tk.Canvas(self.nav_frame, bg=nav_config['background'], height=nav_config['canvas_height'], highlightthickness=0)
        self.nav_scrollbar = ttk.Scrollbar(self.nav_frame, orient="horizontal", command=self.nav_canvas.xview)
        self.nav_container = tk.Frame(self.nav_canvas, bg=nav_config['background'])

        self.nav_container.bind(
            "<Configure>",
            lambda e: self.nav_canvas.configure(scrollregion=self.nav_canvas.bbox("all"))
        )

        self.nav_canvas.create_window((0, 0), window=self.nav_container, anchor="nw")
        self.nav_canvas.configure(xscrollcommand=self.nav_scrollbar.set)

        self.nav_scrollbar.pack(side="bottom", fill="x")
        self.nav_canvas.pack(side="top", fill="x", expand=True)

        self.nav_canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _on_mousewheel(self, event):
        if event.delta > 0:
            self.nav_canvas.xview_scroll(-1, "units")
        elif event.delta < 0:
            self.nav_canvas.xview_scroll(1, "units")

    def _on_options_mousewheel(self, event):
        scroll_direction = -1 if event.delta > 0 else 1
        if self.is_macos:
            scroll_direction *= -1
        self.options_canvas.yview_scroll(scroll_direction, "units")

    def toggle_navigation(self):
        self.nav_visible = not self.nav_visible
        if self.nav_visible:
            self.nav_frame.pack(side="bottom", fill="x", padx=10, pady=5)
            self.toggle_button.config(text="Hide Navigation")
        else:
            self.nav_frame.pack_forget()
            self.toggle_button.config(text="Show Navigation")

    def toggle_translation(self):
        self.is_translated = not self.is_translated
        self.translate_button.config(text="Translate to " + self.config['translator']['to_lang'] if not self.is_translated else "Show Original (" + self.config['translator']['from_lang'] + ")")
        
        if self.is_translated:
            self.root.event_generate("<<TranslateQuestion>>")
        else:
            self.root.event_generate("<<UpdateQuestionDisplay>>")

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

    def display_question(self, question: Question, current_index: int):
        # Determine which text and options to display based on translation state
        if self.is_translated and question.translated_text and question.translated_options:
            question_text = f"Question {current_index + 1}\n{question.translated_text}"
            options = question.translated_options
        else:
            question_text = f"Question {current_index + 1}\n{question.text}"
            options = question.options

        self.question_label.config(text=question_text)
        self.clear_options()

        # Clear UI state for new options
        self.selected_answers.clear()
        if not question.is_multiple_choice:
            self.selected_answer.set("")

        # Map stored user_answers (in English) to displayed options
        displayed_selections = []
        if question.user_answers:
            for ans in question.user_answers:
                try:
                    idx = question.options.index(ans)
                    # If translated, map to translated option; otherwise, use English option
                    if self.is_translated and question.translated_options and idx < len(question.translated_options):
                        displayed_selections.append(question.translated_options[idx])
                    else:
                        displayed_selections.append(ans)
                except (ValueError, IndexError):
                    continue

        # Create new option widgets
        for option in options:
            option_frame = tk.Frame(self.options_inner_frame, bg=self.config['window']['background'], relief="solid", borderwidth=1,
                                  highlightbackground="#dee2e6", highlightthickness=1)
            option_frame.pack(fill="x", pady=5)
            option_frame.bind("<Enter>", lambda e, f=option_frame: f.config(bg="#f8f9fa"))
            option_frame.bind("<Leave>", lambda e, f=option_frame: f.config(bg=self.config['window']['background']))

            if question.is_multiple_choice:
                var = tk.BooleanVar(value=option in displayed_selections)
                self.selected_answers[option] = var
                widget = ttk.Checkbutton(option_frame, text=option, variable=var, style="Option.TCheckbutton")
            else:
                widget = ttk.Radiobutton(option_frame, text=option, variable=self.selected_answer, value=option, style="Option.TRadiobutton")
                if option in displayed_selections:
                    self.selected_answer.set(option)

            widget.pack(anchor="w", padx=15, pady=10)
            self.option_widgets.append(widget)
            self.option_frames.append(option_frame)

        self.update_scrollbar_visibility()
        self.update_question_scrollbar_visibility()

    def update_scrollbar_visibility(self):
        self.root.update_idletasks()
        canvas_height = self.options_canvas.winfo_height()
        content_height = self.options_inner_frame.winfo_reqheight()
        if content_height <= canvas_height:
            self.options_scrollbar.pack_forget()
        else:
            self.options_scrollbar.pack(side="right", fill="y")

    def update_question_scrollbar_visibility(self):
        self.root.update_idletasks()
        canvas_height = self.question_canvas.winfo_height()
        content_height = self.question_inner_frame.winfo_reqheight()
        if content_height <= canvas_height:
            self.question_scrollbar.pack_forget()
        else:
            self.question_scrollbar.pack(side="right", fill="y")

    def create_navigation_buttons(self, num_questions: int, go_to_question_callback):
        for btn in self.nav_buttons:
            btn.destroy()
        self.nav_buttons = []
        style_config = self.config['styles']

        for i in range(num_questions):
            if self.is_macos:
                btn = MacButton(self.nav_container, 
                               text=str(i + 1), 
                               width=40,
                               font=tuple(style_config['button']['font']),
                               background=style_config['button']['default_background'],
                               foreground=style_config['button']['default_foreground'],
                               activebackground=style_config['button']['active_background'],
                               activeforeground=style_config['button']['active_foreground'],
                               borderwidth=style_config['button']['borderwidth'],
                               relief=style_config['button']['relief'],
                               command=lambda idx=i: go_to_question_callback(idx))
            else:
                btn = ttk.Button(self.nav_container, 
                                text=str(i + 1), 
                                width=4,
                                command=lambda idx=i: go_to_question_callback(idx))
            btn.grid(row=0, column=i, padx=0, pady=0)
            self.nav_buttons.append(btn)

    def update_navigation_buttons(self, questions: List[Question], current_index: int):
        style_config = self.config['styles']
        for i, btn in enumerate(self.nav_buttons):
            question = questions[i]
            
            if self.is_macos:
                if i == current_index:
                    btn.config(background=style_config['active_button']['background'],
                              foreground=style_config['button']['active_foreground'])
                elif question.flagged:
                    btn.config(background=style_config['flagged_button']['background'],
                              foreground=style_config['button']['default_foreground'])
                elif question.user_answers:
                    btn.config(background=style_config['answered_button']['background'],
                              foreground=style_config['button']['default_foreground'])
                elif question.answer_viewed:
                    btn.config(background=style_config['viewed_button']['background'],
                              foreground=style_config['button']['default_foreground'])
                else:
                    btn.config(background=style_config['button']['default_background'],
                              foreground=style_config['button']['default_foreground'])
            else:
                if i == current_index:
                    btn.config(style="Active.TButton")
                elif question.flagged:
                    btn.config(style="Flagged.TButton")
                elif question.user_answers:
                    btn.config(style="Answered.TButton")
                elif question.answer_viewed:
                    btn.config(style="Viewed.TButton")
                else:
                    btn.config(style="TButton")
            
            if question.flagged:
                btn.config(text=f"{i+1} ⚑")
            else:
                btn.config(text=str(i+1))

class MockExamApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.config = self.load_config()
        self.is_macos = platform.system() == "Darwin" and MacButton is not None
        self.ui = UIManager(root, self.config)
        self.question_bank = QuestionBank()
        self.exam_state = ExamState(self.config)
        self.translator = GoogleTranslator(
            source=self.config['translator']['from_lang'], 
            target=self.config['translator']['to_lang'])
        self.setup_controls()
        self.root.bind("<<UpdateQuestionDisplay>>", lambda e: self.display_question())
        self.root.bind("<<TranslateQuestion>>", self.handle_translate_question)

    def load_config(self):
        try:
            config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.yaml')
            with open(config_path, 'r') as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            messagebox.showerror("Error", "Configuration file 'config.yaml' not found!")
            raise
        except yaml.YAMLError as e:
            messagebox.showerror("Error", f"Failed to parse config.yaml: {str(e)}")
            raise

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
                # Validate that all options were translated successfully
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

        # Map selections to English if in translated mode
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

if __name__ == "__main__":
    root = tk.Tk()
    app = MockExamApp(root)
    root.mainloop()