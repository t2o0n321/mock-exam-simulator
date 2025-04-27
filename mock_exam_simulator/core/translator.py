from deep_translator import GoogleTranslator
from tkinter import messagebox

class Translator:
    def __init__(self, source_lang: str, target_lang: str):
        try:
            self.translator = GoogleTranslator(source=source_lang, target=target_lang)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to initialize translator: {str(e)}")
            raise

    def translate(self, text: str) -> str:
        try:
            if not text or not isinstance(text, str):
                raise ValueError("Invalid text for translation")
            return self.translator.translate(text)
        except Exception as e:
            messagebox.showerror("Translation Error", f"Failed to translate text: {str(e)}")
            return text  # Return original text as fallback