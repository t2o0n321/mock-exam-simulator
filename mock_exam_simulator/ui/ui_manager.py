# mock_exam_simulator/ui/ui_manager.py
import tkinter as tk
from tkinter import ttk
import platform
from typing import List, Optional
from .styles import configure_styles
try:
    if platform.system() == "Darwin":
        from tkmacosx import Button as MacButton
    else:
        MacButton = None
except ImportError:
    MacButton = None
from ..models.question import Question

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
        configure_styles(self.config)
        nav_config = self.config['navigation']
        question_bar_config = self.config['question_bar']
        style_config = self.config['styles']

        self.root.title(window_config['title'])
        self.root.geometry(f"{window_config['width']}x{window_config['height']}")
        self.root.configure(bg=window_config['background'])

        self.root.bind("<Configure>", self.update_wraplength)

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
        ttk.Style().configure("Custom.TEntry", 
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
        if self.is_translated and question.translated_text and question.translated_options:
            question_text = f"Question {current_index + 1}\n{question.translated_text}"
            options = question.translated_options
        else:
            question_text = f"Question {current_index + 1}\n{question.text}"
            options = question.options

        self.question_label.config(text=question_text)
        self.clear_options()

        self.selected_answers.clear()
        if not question.is_multiple_choice:
            self.selected_answer.set("")

        displayed_selections = []
        if question.user_answers:
            for ans in question.user_answers:
                try:
                    idx = question.options.index(ans)
                    if self.is_translated and question.translated_options and idx < len(question.translated_options):
                        displayed_selections.append(question.translated_options[idx])
                    else:
                        displayed_selections.append(ans)
                except (ValueError, IndexError):
                    continue

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