# mock_exam_simulator/core/exam_state.py
from typing import List, Optional
from ..models.question import Question

class ExamState:
    def __init__(self, config):
        self.current_index: int = 0
        self.score: int = 0
        self.penalties: int = 0
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