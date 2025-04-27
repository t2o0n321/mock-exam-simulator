import platform
import tkinter as tk
from tkinter import ttk
from typing import Optional, Tuple, Union

try:
    if platform.system() == "Darwin":
        from tkmacosx import Button as MacButton
    else:
        MacButton = None
except ImportError:
    MacButton = None


class Styles:
    """Manages UI styles and platform-specific button creation."""
    
    def __init__(self, config: dict):
        self.config = config
        self.is_macos = platform.system() == "Darwin" and MacButton is not None

    def configure_styles(self, root: tk.Tk) -> None:
        """Configure Tkinter styles."""
        style = ttk.Style()
        style_config = self.config["styles"]

        # Button styles
        style.configure(
            "TButton",
            font=tuple(style_config["button"]["font"]),
            padding=style_config["button"]["padding"],
            borderwidth=style_config["button"]["borderwidth"],
            relief=style_config["button"]["relief"],
        )
        style.map(
            "TButton",
            background=[
                ("active", style_config["button"]["active_background"]),
                ("!active", style_config["button"]["default_background"]),
                ("disabled", style_config["button"]["disabled_background"]),
            ],
            foreground=[
                ("active", style_config["button"]["active_foreground"]),
                ("!active", style_config["button"]["default_foreground"]),
                ("disabled", style_config["button"]["disabled_foreground"]),
            ],
        )

        # Non-macOS specific button styles
        if not self.is_macos:
            style.configure("Answered.TButton", background=style_config["answered_button"]["background"])
            style.configure("Active.TButton", background=style_config["active_button"]["background"])
            style.configure("Viewed.TButton", background=style_config["viewed_button"]["background"])
            style.configure("Flagged.TButton", background=style_config["flagged_button"]["background"])

        # Label, Entry, Radiobutton, Checkbutton, Progressbar
        style.configure("TLabel", background=style_config["label"]["background"], font=tuple(style_config["label"]["font"]))
        style.configure("TEntry", padding=style_config["entry"]["padding"])
        style.configure("TRadiobutton", background=style_config["radiobutton"]["background"], font=tuple(style_config["radiobutton"]["font"]))
        style.configure("TCheckbutton", background=style_config["checkbutton"]["background"], font=tuple(style_config["checkbutton"]["font"]))
        style.configure(
            "TProgressbar",
            thickness=style_config["progressbar"]["thickness"],
            background=style_config["progressbar"]["background"],
            troughcolor=style_config["progressbar"]["troughcolor"],
        )

        # Option-specific styles
        style.configure(
            "Option.TRadiobutton",
            background=style_config["radiobutton"]["background"],
            font=("Segoe UI", self.config["option_display"]["font_size"]),
        )
        style.configure(
            "Option.TCheckbutton",
            background=style_config["checkbutton"]["background"],
            font=("Segoe UI", self.config["option_display"]["font_size"]),
        )

        # Custom Entry style
        style.configure(
            "Custom.TEntry",
            bordercolor=style_config["entry"]["bordercolor"],
            relief=style_config["entry"]["relief"],
            borderwidth=style_config["entry"]["borderwidth"],
        )

    def create_button(
        self,
        parent: tk.Widget,
        text: str,
        command: Optional[callable] = None,
        state: str = "normal",
        width: Optional[int] = None
    ) -> Union[ttk.Button, "MacButton"]:
        """Create a platform-specific button."""
        style_config = self.config["styles"]["button"]
        if self.is_macos:
            return MacButton(
                parent,
                text=text,
                command=command,
                state=state,
                width=width,
                font=tuple(style_config["font"]),
                background=style_config["default_background"],
                foreground=style_config["default_foreground"],
                activebackground=style_config["active_background"],
                activeforeground=style_config["active_foreground"],
                disabledbackground=style_config["disabled_background"],
                disabledforeground=style_config["disabled_foreground"],
                borderwidth=style_config["borderwidth"],
                relief=style_config["relief"],
            )
        return ttk.Button(parent, text=text, command=command, state=state, width=width)