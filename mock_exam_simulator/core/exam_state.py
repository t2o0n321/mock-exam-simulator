from typing import List, Optional
from ..models.question import Question


class ExamState:
    """Manages the state of an ongoing exam."""
    
    def __init__(self, config: dict):
        self.current_index: int = 0
        self.score: int = 0
        self.penalties: int = 0
        self.questions: List[Question] = []
        self.time_remaining: int = config["exam"]["default_time_limit_minutes"] * 60
        self.timer_id: Optional[str] = None

    def reset(self) -> None:
        """Reset the exam state to initial values."""
        self.current_index = 0
        self.score = 0
        self.penalties = 0
        self.questions = []
        self.time_remaining = 0
        self.timer_id = None