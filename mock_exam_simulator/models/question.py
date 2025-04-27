# mock_exam_simulator/models/question.py
from dataclasses import dataclass
from typing import List, Optional

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