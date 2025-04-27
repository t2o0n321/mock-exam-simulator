import pandas as pd
import ast
from typing import List
from tkinter import messagebox
from ..models.question import Question
import random

class QuestionBank:
    def __init__(self):
        self.questions: List[Question] = []

    def load_from_csv(self, file_path: str) -> bool:
        try:
            # Try reading the CSV file
            try:
                df = pd.read_csv(file_path)
            except FileNotFoundError:
                messagebox.showerror("Error", f"CSV file not found: {file_path}")
                return False
            except pd.errors.EmptyDataError:
                messagebox.showerror("Error", "CSV file is empty")
                return False
            except pd.errors.ParserError:
                messagebox.showerror("Error", "Invalid CSV format")
                return False

            # Check for required columns
            required_columns = ["question", "options", "correct"]
            if not all(col in df.columns for col in required_columns):
                messagebox.showerror("Error", "CSV missing required columns: 'question', 'options', 'correct'")
                return False
            
            self.questions = []
            for _, row in df.iterrows():
                try:
                    # Parse options
                    try:
                        options = ast.literal_eval(row["options"])
                        if not isinstance(options, list) or not all(isinstance(opt, str) for opt in options):
                            raise ValueError("Options must be a list of strings")
                    except (ValueError, SyntaxError) as e:
                        messagebox.showerror("Error", f"Invalid options format for question: {row['question']}")
                        return False
                    
                    if not options:
                        messagebox.showerror("Error", f"No valid options for question: {row['question']}")
                        return False
                    
                    # Parse correct answers
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
                        messagebox.showerror("Error", f"Invalid correct answer indices for question: {row['question']}: {str(e)}")
                        return False
                    
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
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to process question: {row.get('question', 'Unknown')}: {str(e)}")
                    return False
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error while importing questions: {str(e)}")
            return False

    def get_random_questions(self, count: int) -> List[Question]:
        try:
            sample_size = min(len(self.questions), count)
            if sample_size <= 0:
                raise ValueError("No questions available or invalid count")
            selected_questions = random.sample(self.questions, sample_size)
            for q in selected_questions:
                q.user_answers = None
                q.answer_viewed = False
                q.flagged = False
                q.translated_text = None
                q.translated_options = None
            return selected_questions
        except ValueError as e:
            messagebox.showerror("Error", f"Cannot select questions: {str(e)}")
            return []
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error while selecting questions: {str(e)}")
            return []