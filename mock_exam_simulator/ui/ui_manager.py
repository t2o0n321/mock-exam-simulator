import tkinter as tk
from tkinter import ttk
from typing import List, Dict, Callable
from ..models.question import Question
from .styles import Styles


class UIManager:
    """Manages the Tkinter UI for the mock exam simulator."""
    
    def __init__(self, root: tk.Tk, config: dict):
        self.root = root
        self.config = config
        self.styles = Styles(config)
        self.is_translated = False
        self.main_frame = tk.Frame(root, bg=config["window"]["background"])
        self.quiz_frame = tk.Frame(root, bg=config["window"]["background"])
        self.selected_answer = tk.StringVar()
        self.selected_answers: Dict[str, tk.BooleanVar] = {}
        self.option_widgets: List[ttk.Radiobutton | ttk.Checkbutton] = []
        self.option_frames: List[tk.Frame] = []
        self.nav_buttons: List[ttk.Button | "MacButton"] = []
        self.options_frame: tk.Frame | None = None
        self.options_canvas: tk.Canvas | None = None
        self.options_inner_frame: tk.Frame | None = None
        self.options_scrollbar: ttk.Scrollbar | None = None
        self.question_canvas: tk.Canvas | None = None
        self.question_inner_frame: tk.Frame | None = None
        self.question_scrollbar: ttk.Scrollbar | None = None
        self.timer_label: tk.Label | None = None
        self.progress_bar: ttk.Progressbar | None = None
        self.nav_frame: tk.Frame | None = None
        self.nav_visible = config["navigation"]["default_visible"]
        self.toggle_button: ttk.Button | "MacButton" | None = None
        self.nav_container: tk.Frame | None = None
        self.nav_canvas: tk.Canvas | None = None
        self.nav_scrollbar: ttk.Scrollbar | None = None
        self.translate_button: ttk.Button | "MacButton" | None = None
        self.question_label: tk.Label | None = None
        self.num_questions_entry: ttk.Entry | None = None
        self.time_limit_entry: ttk.Entry | None = None
        self.setup_ui()

    def setup_ui(self) -> None:
        """Initialize the UI components."""
        self.styles.configure_styles(self.root)
        window_config = self.config["window"]

        self.root.title(window_config["title"])
        self.root.geometry(f"{window_config['width']}x{window_config['height']}")
        self.root.configure(bg=window_config["background"])
        self.root.bind("<Configure>", self.update_wraplength)

        self._setup_main_frame()
        self._setup_quiz_frame()

    def _setup_main_frame(self) -> None:
        """Set up the main frame for exam configuration."""
        self.main_frame.pack(pady=50, padx=50, fill="both", expand=True)
        main_card = tk.Frame(
            self.main_frame,
            bg=self.config["window"]["background"],
            relief="solid",
            borderwidth=1,
            highlightbackground="#dee2e6",
            highlightthickness=1,
        )
        main_card.pack(pady=20, padx=20, fill="both", expand=True)

        tk.Label(
            main_card,
            text="Mock Exam Simulator",
            font=("Segoe UI", 28, "bold"),
            bg=self.config["window"]["background"],
            fg="#2d2d2d",
        ).pack(pady=30)

        settings_frame = tk.Frame(main_card, bg=self.config["window"]["background"])
        settings_frame.pack(pady=10)

        tk.Label(
            settings_frame,
            text="Number of Questions:",
            font=("Segoe UI", 14),
            bg=self.config["window"]["background"],
            fg="#2d2d2d",
        ).grid(row=0, column=0, padx=10, pady=10)
        self.num_questions_entry = ttk.Entry(settings_frame, width=10, font=("Segoe UI", 12), style="Custom.TEntry")
        self.num_questions_entry.grid(row=0, column=1, padx=10, pady=10)
        self.num_questions_entry.insert(0, str(self.config["exam"]["default_questions"]))

        tk.Label(
            settings_frame,
            text="Time Limit (minutes):",
            font=("Segoe UI", 14),
            bg=self.config["window"]["background"],
            fg="#2d2d2d",
        ).grid(row=1, column=0, padx=10, pady=10)
        self.time_limit_entry = ttk.Entry(settings_frame, width=10, font=("Segoe UI", 12), style="Custom.TEntry")
        self.time_limit_entry.grid(row=1, column=1, padx=10, pady=10)
        self.time_limit_entry.insert(0, str(self.config["exam"]["default_time_limit_minutes"]))

    def _setup_quiz_frame(self) -> None:
        """Set up the quiz frame for exam questions."""
        content_frame = tk.Frame(self.quiz_frame, bg=self.config["window"]["background"])
        content_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.timer_label = tk.Label(
            content_frame,
            text="Time Remaining: 00:00",
            font=("Segoe UI", 16, "bold"),
            bg=self.config["window"]["background"],
            fg="#e63946",
        )
        self.timer_label.pack(pady=15)

        self.progress_bar = ttk.Progressbar(content_frame, orient="horizontal", mode="determinate")
        self.progress_bar.pack(fill="x", padx=30, pady=10)

        self.translate_button = self.styles.create_button(
            content_frame,
            text=f"Translate to {self.config['translator']['to_lang']}",
            command=self.toggle_translation,
        )
        self.translate_button.pack(pady=1)

        question_card = tk.Frame(
            content_frame,
            bg=self.config["window"]["background"],
            relief="solid",
            borderwidth=1,
            highlightbackground="#dee2e6",
            highlightthickness=1,
        )
        question_card.pack(pady=10, padx=30, fill="both", expand=True)

        self._setup_question_area(question_card)
        self._setup_options_area(question_card)
        self._setup_navigation(content_frame)

    def _setup_question_area(self, parent: tk.Frame) -> None:
        """Set up the question display area with scrollbar."""
        header_frame = tk.Frame(parent, bg=self.config["window"]["background"])
        header_frame.pack(fill="x", padx=20, pady=10)

        self.question_canvas = tk.Canvas(
            header_frame,
            bg=self.config["window"]["background"],
            highlightthickness=0,
            height=self.config["question_bar"]["height"],
        )
        self.question_scrollbar = ttk.Scrollbar(header_frame, orient="vertical", command=self.question_canvas.yview)
        self.question_inner_frame = tk.Frame(self.question_canvas, bg=self.config["window"]["background"])

        self.question_inner_frame.bind(
            "<Configure>",
            lambda e: self.question_canvas.configure(scrollregion=self.question_canvas.bbox("all")),
        )
        self.question_canvas.create_window((0, 0), window=self.question_inner_frame, anchor="nw")
        self.question_canvas.configure(yscrollcommand=self.question_scrollbar.set)

        self.question_canvas.pack(side="left", fill="both", expand=True)
        self.question_scrollbar.pack(side="right", fill="y")
        self.question_canvas.bind("<Configure>", lambda e: self.update_question_scrollbar_visibility())

        self.question_label = tk.Label(
            self.question_inner_frame,
            text="",
            font=("Segoe UI", self.config["question_bar"]["font_size"], "bold"),
            bg=self.config["window"]["background"],
            fg="#2d2d2d",
            wraplength=300,
            justify="left",
        )
        self.question_label.pack(anchor="w")
        self.root.after(100, self.update_wraplength)

    def _setup_options_area(self, parent: tk.Frame) -> None:
        """Set up the options display area with scrollbar."""
        self.options_canvas = tk.Canvas(parent, bg=self.config["window"]["background"], highlightthickness=0)
        self.options_scrollbar = ttk.Scrollbar(parent, orient="vertical", command=self.options_canvas.yview)
        self.options_inner_frame = tk.Frame(self.options_canvas, bg=self.config["window"]["background"])

        self.options_inner_frame.bind(
            "<Configure>",
            lambda e: self.options_canvas.configure(scrollregion=self.options_canvas.bbox("all")),
        )
        self.options_canvas.create_window((0, 0), window=self.options_inner_frame, anchor="nw")
        self.options_canvas.configure(yscrollcommand=self.options_scrollbar.set)

        self.options_canvas.pack(side="left", fill="both", expand=True, padx=20, pady=10)
        self.options_scrollbar.pack(side="right", fill="y")
        self.options_canvas.bind("<Configure>", lambda e: self.update_scrollbar_visibility())

        if self.styles.is_macos:
            self.options_canvas.bind_all("<MouseWheel>", self._on_options_mousewheel)
            self.options_canvas.bind_all("<Shift-MouseWheel>", lambda event: None)
        else:
            self.options_canvas.bind_all("<MouseWheel>", self._on_options_mousewheel)

    def _setup_navigation(self, parent: tk.Frame) -> None:
        """Set up the navigation bar."""
        self.toggle_button = self.styles.create_button(
            parent,
            text="Show Navigation" if not self.nav_visible else "Hide Navigation",
            command=self.toggle_navigation,
        )
        self.toggle_button.pack(side="bottom", pady=5)

        self.nav_frame = tk.Frame(parent, bg=self.config["navigation"]["background"])
        if self.nav_visible:
            self.nav_frame.pack(side="bottom", fill="x", padx=10, pady=5)

        tk.Label(
            self.nav_frame,
            text="Quiz Navigation",
            font=("Segoe UI", 8, "bold"),
            bg=self.config["navigation"]["background"],
            fg="#2d2d2d",
        ).pack(pady=3)

        self.nav_canvas = tk.Canvas(
            self.nav_frame,
            bg=self.config["navigation"]["background"],
            height=self.config["navigation"]["canvas_height"],
            highlightthickness=0,
        )
        self.nav_scrollbar = ttk.Scrollbar(self.nav_frame, orient="horizontal", command=self.nav_canvas.xview)
        self.nav_container = tk.Frame(self.nav_canvas, bg=self.config["navigation"]["background"])

        self.nav_container.bind(
            "<Configure>",
            lambda e: self.nav_canvas.configure(scrollregion=self.nav_canvas.bbox("all")),
        )
        self.nav_canvas.create_window((0, 0), window=self.nav_container, anchor="nw")
        self.nav_canvas.configure(xscrollcommand=self.nav_scrollbar.set)

        self.nav_scrollbar.pack(side="bottom", fill="x")
        self.nav_canvas.pack(side="top", fill="x", expand=True)
        self.nav_canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def update_wraplength(self, event: tk.Event | None = None) -> None:
        """Update the wrap length of the question label based on window size."""
        if not self.question_label:
            return
        window_width = self.root.winfo_width()
        padding = 2 * 30 + 2 * 20 + 25
        available_width = max(window_width - padding, 300)
        wraplength = int(available_width * 0.9)
        self.question_label.config(wraplength=wraplength)

    def _on_mousewheel(self, event: tk.Event) -> None:
        """Handle mouse wheel scrolling for navigation."""
        if event.delta > 0:
            self.nav_canvas.xview_scroll(-1, "units")
        elif event.delta < 0:
            self.nav_canvas.xview_scroll(1, "units")

    def _on_options_mousewheel(self, event: tk.Event) -> None:
        """Handle mouse wheel scrolling for options."""
        scroll_direction = -1 if event.delta > 0 else 1
        if self.styles.is_macos:
            scroll_direction *= -1
        self.options_canvas.yview_scroll(scroll_direction, "units")

    def toggle_navigation(self) -> None:
        """Toggle the visibility of the navigation bar."""
        self.nav_visible = not self.nav_visible
        if self.nav_visible:
            self.nav_frame.pack(side="bottom", fill="x", padx=10, pady=5)
            self.toggle_button.config(text="Hide Navigation")
        else:
            self.nav_frame.pack_forget()
            self.toggle_button.config(text="Show Navigation")

    def toggle_translation(self) -> None:
        """Toggle between original and translated question text."""
        self.is_translated = not self.is_translated
        self.translate_button.config(
            text=f"Translate to {self.config['translator']['to_lang']}"
            if not self.is_translated
            else f"Show Original ({self.config['translator']['from_lang']})"
        )
        self.root.event_generate("<<TranslateQuestion>>" if self.is_translated else "<<UpdateQuestionDisplay>>")

    def show_main_frame(self) -> None:
        """Show the main configuration frame."""
        self.quiz_frame.pack_forget()
        self.main_frame.pack(pady=50, padx=50, fill="both", expand=True)

    def show_quiz_frame(self) -> None:
        """Show the quiz frame."""
        self.main_frame.pack_forget()
        self.quiz_frame.pack(pady=20, padx=20, fill="both", expand=True)

    def update_timer_display(self, seconds: int) -> None:
        """Update the timer display."""
        if not self.timer_label:
            return
        minutes = seconds // 60
        seconds = seconds % 60
        self.timer_label.config(text=f"Time Remaining: {minutes:02d}:{seconds:02d}")

    def update_progress(self, current: int, total: int) -> None:
        """Update the progress bar."""
        if not self.progress_bar:
            return
        self.progress_bar["maximum"] = total
        self.progress_bar["value"] = current + 1

    def clear_options(self) -> None:
        """Clear existing option widgets."""
        for widget in self.option_widgets:
            widget.destroy()
        for frame in self.option_frames:
            frame.destroy()
        self.option_widgets = []
        self.option_frames = []

    def display_question(self, question: Question, current_index: int) -> None:
        """Display a question and its options."""
        if not self.question_label:
            return

        # Determine text and options based on translation state
        if self.is_translated and question.translated_text and question.translated_options:
            question_text = f"Question {current_index + 1}\n{question.translated_text}"
            options = question.translated_options
        else:
            question_text = f"Question {current_index + 1}\n{question.text}"
            options = question.options

        self.question_label.config(text=question_text)
        self.clear_options()

        # Clear UI state
        self.selected_answers.clear()
        if not question.is_multiple_choice:
            self.selected_answer.set("")

        # Map user answers to displayed options
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

        # Create option widgets
        for option in options:
            option_frame = tk.Frame(
                self.options_inner_frame,
                bg=self.config["window"]["background"],
                relief="solid",
                borderwidth=1,
                highlightbackground="#dee2e6",
                highlightthickness=1,
            )
            option_frame.pack(fill="x", pady=5)
            option_frame.bind("<Enter>", lambda e, f=option_frame: f.config(bg="#f8f9fa"))
            option_frame.bind("<Leave>", lambda e, f=option_frame: f.config(bg=self.config["window"]["background"]))

            if question.is_multiple_choice:
                var = tk.BooleanVar(value=option in displayed_selections)
                self.selected_answers[option] = var
                widget = ttk.Checkbutton(option_frame, text=option, variable=var, style="Option.TCheckbutton")
            else:
                widget = ttk.Radiobutton(
                    option_frame, text=option, variable=self.selected_answer, value=option, style="Option.TRadiobutton"
                )
                if option in displayed_selections:
                    self.selected_answer.set(option)

            widget.pack(anchor="w", padx=15, pady=10)
            self.option_widgets.append(widget)
            self.option_frames.append(option_frame)

        self.update_scrollbar_visibility()
        self.update_question_scrollbar_visibility()

    def update_scrollbar_visibility(self) -> None:
        """Update the visibility of the options scrollbar."""
        if not self.options_canvas or not self.options_inner_frame or not self.options_scrollbar:
            return
        self.root.update_idletasks()
        canvas_height = self.options_canvas.winfo_height()
        content_height = self.options_inner_frame.winfo_reqheight()
        if content_height <= canvas_height:
            self.options_scrollbar.pack_forget()
        else:
            self.options_scrollbar.pack(side="right", fill="y")

    def update_question_scrollbar_visibility(self) -> None:
        """Update the visibility of the question scrollbar."""
        if not self.question_canvas or not self.question_inner_frame or not self.question_scrollbar:
            return
        self.root.update_idletasks()
        canvas_height = self.question_canvas.winfo_height()
        content_height = self.question_inner_frame.winfo_reqheight()
        if content_height <= canvas_height:
            self.question_scrollbar.pack_forget()
        else:
            self.question_scrollbar.pack(side="right", fill="y")

    def create_navigation_buttons(self, num_questions: int, go_to_question_callback: Callable[[int], None]) -> None:
        """Create navigation buttons for each question."""
        for btn in self.nav_buttons:
            btn.destroy()
        self.nav_buttons = []

        for i in range(num_questions):
            btn = self.styles.create_button(
                self.nav_container,
                text=str(i + 1),
                command=lambda idx=i: go_to_question_callback(idx),
                width=40 if self.styles.is_macos else 4,
            )
            btn.grid(row=0, column=i, padx=0, pady=0)
            self.nav_buttons.append(btn)

    def update_navigation_buttons(self, questions: List[Question], current_index: int) -> None:
        """Update the style and text of navigation buttons."""
        style_config = self.config["styles"]
        for i, btn in enumerate(self.nav_buttons):
            question = questions[i]
            if self.styles.is_macos:
                if i == current_index:
                    btn.config(
                        background=style_config["active_button"]["background"],
                        foreground=style_config["button"]["active_foreground"],
                    )
                elif question.flagged:
                    btn.config(
                        background=style_config["flagged_button"]["background"],
                        foreground=style_config["button"]["default_foreground"],
                    )
                elif question.user_answers:
                    btn.config(
                        background=style_config["answered_button"]["background"],
                        foreground=style_config["button"]["default_foreground"],
                    )
                elif question.answer_viewed:
                    btn.config(
                        background=style_config["viewed_button"]["background"],
                        foreground=style_config["button"]["default_foreground"],
                    )
                else:
                    btn.config(
                        background=style_config["button"]["default_background"],
                        foreground=style_config["button"]["default_foreground"],
                    )
            else:
                btn.config(
                    style=(
                        "Active.TButton"
                        if i == current_index
                        else "Flagged.TButton"
                        if question.flagged
                        else "Answered.TButton"
                        if question.user_answers
                        else "Viewed.TButton"
                        if question.answer_viewed
                        else "TButton"
                    )
                )
            btn.config(text=f"{i+1} ⚑" if question.flagged else str(i + 1))