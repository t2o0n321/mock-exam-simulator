from deep_translator import GoogleTranslator
from tkinter import messagebox
from ..models.question import Question


class Translator:
    """Handles translation of questions and options."""
    
    def __init__(self, from_lang: str, to_lang: str):
        self.translator = GoogleTranslator(source=from_lang, target=to_lang)

    def translate_question(self, question: Question) -> None:
        """Translate a question's text and options."""
        try:
            question.translated_text = self.translator.translate(question.text)
            question.translated_options = [self.translator.translate(opt) for opt in question.options]
            if not question.translated_options or None in question.translated_options or len(question.translated_options) != len(question.options):
                raise ValueError("Incomplete or invalid translation of options")
        except Exception as e:
            messagebox.showerror("Translation Error", f"Failed to translate: {str(e)}")
            question.translated_text = question.text
            question.translated_options = question.options.copy()