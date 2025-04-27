import ast
import random
from typing import List
import pandas as pd
from tkinter import messagebox
from ..models.question import Question


class QuestionBank:
    """Manages a collection of exam questions."""
    
    def __init__(self):
        self.questions: List[Question] = []

    def load_from_csv(self, file_path: str) -> bool:
        """Load questions from a CSV file."""
        try:
            df = pd.read_csv(file_path)
            required_columns = ["question", "options", "correct"]
            if not all(col in df.columns for col in required_columns):
                raise ValueError("CSV missing required columns: 'question', 'options', 'correct'")

            self.questions = []
            for _, row in df.iterrows():
                options = self._parse_options(row["question"], row["options"])
                correct_answers = self._parse_correct_answers(row["question"], options, row["correct"])
                self.questions.append(
                    Question(
                        text=str(row["question"]),
                        options=options,
                        correct_answers=correct_answers,
                        is_multiple_choice=len(correct_answers) > 1,
                    )
                )
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Failed to import questions: {str(e)}")
            return False

    def _parse_options(self, question: str, options_str: str) -> List[str]:
        """Parse options from a string representation."""
        try:
            options = ast.literal_eval(options_str)
            if not isinstance(options, list) or not all(isinstance(opt, str) for opt in options):
                raise ValueError("Options must be a list of strings")
            if not options:
                raise ValueError("No valid options provided")
            return options
        except (ValueError, SyntaxError) as e:
            raise ValueError(f"Invalid options format for question: {question}: {str(e)}")

    def _parse_correct_answers(self, question: str, options: List[str], correct_str: str) -> List[str]:
        """Parse correct answer indices and convert to answer strings."""
        try:
            if pd.isna(correct_str):
                raise ValueError("Correct answer indices cannot be empty")
            correct_indices = [int(idx.strip()) for idx in str(correct_str).split(",")]
            for idx in correct_indices:
                if idx < 0 or idx >= len(options):
                    raise ValueError(f"Correct index {idx} out of range for options")
            correct_indices = list(set(correct_indices))
            if len(correct_indices) > 6:
                raise ValueError("Maximum 6 correct answers allowed")
            if not correct_indices:
                raise ValueError("At least one correct answer required")
            return [options[idx] for idx in correct_indices]
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid correct answer indices for question: {question}: {str(e)}")

    def get_random_questions(self, count: int) -> List[Question]:
        """Retrieve a random sample of questions."""
        sample_size = min(len(self.questions), count)
        selected_questions = random.sample(self.questions, sample_size)
        for q in selected_questions:
            q.user_answers = None
            q.answer_viewed = False
            q.flagged = False
            q.translated_text = None
            q.translated_options = None
        return selected_questions