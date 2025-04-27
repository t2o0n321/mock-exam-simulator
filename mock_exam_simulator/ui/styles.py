# mock_exam_simulator/ui/styles.py
from tkinter import ttk

def configure_styles(config):
    style = ttk.Style()
    style_config = config['styles']
    window_config = config['window']
    nav_config = config['navigation']
    question_bar_config = config['question_bar']
    option_display_config = config['option_display']

    style.theme_use("clam")

    style.configure("TButton", 
                    font=tuple(style_config['button']['font']), 
                    padding=style_config['button']['padding'],
                    borderwidth=style_config['button']['borderwidth'],
                    relief=style_config['button']['relief'])
    style.map("TButton",
              background=[
                  ("active", style_config['button']['active_background']),
                  ("pressed", style_config['button']['active_background']),
                  ("!active", style_config['button']['default_background']),
                  ("disabled", style_config['button']['disabled_background'])
              ],
              foreground=[
                  ("active", style_config['button']['active_foreground']),
                  ("pressed", style_config['button']['active_foreground']),
                  ("!active", style_config['button']['default_foreground']),
                  ("disabled", style_config['button']['disabled_foreground'])
              ])
    style.configure("TLabel", 
                    background=style_config['label']['background'], 
                    font=tuple(style_config['label']['font']))
    style.configure("TEntry", padding=style_config['entry']['padding'])
    style.configure("TRadiobutton", 
                    background=style_config['radiobutton']['background'], 
                    font=tuple(style_config['radiobutton']['font']))
    style.configure("TCheckbutton", 
                    background=style_config['checkbutton']['background'], 
                    font=tuple(style_config['checkbutton']['font']))
    style.configure("TProgressbar", 
                    thickness=style_config['progressbar']['thickness'],
                    background=style_config['progressbar']['background'], 
                    troughcolor=style_config['progressbar']['troughcolor'])
    
    style.configure("Answered.TButton", background="#a3e635")
    style.map("Answered.TButton",
              background=[
                  ("active", "#90cc30"),
                  ("pressed", "#90cc30"),
                  ("!active", "#a3e635"),
                  ("disabled", "#d3d3d3")
              ])
    style.configure("Active.TButton", background=style_config['active_button']['background'])
    style.map("Active.TButton",
              background=[
                  ("active", style_config['active_button']['background']),
                  ("pressed", style_config['active_button']['background']),
                  ("!active", style_config['active_button']['background']),
                  ("disabled", "#d3d3d3")
              ])
    style.configure("Viewed.TButton", background=style_config['viewed_button']['background'])
    style.map("Viewed.TButton",
              background=[
                  ("active", style_config['viewed_button']['background']),
                  ("pressed", style_config['viewed_button']['background']),
                  ("!active", style_config['viewed_button']['background']),
                  ("disabled", "#d3d3d3")
              ])
    style.configure("Flagged.TButton", background="#ff9500")
    style.map("Flagged.TButton",
              background=[
                  ("active", "#e68500"),
                  ("pressed", "#e68500"),
                  ("!active", "#ff9500"),
                  ("disabled", "#d3d3d3")
              ])

    style.configure("Option.TRadiobutton", 
                    background=style_config['radiobutton']['background'], 
                    font=("Segoe UI", option_display_config['font_size']))
    style.configure("Option.TCheckbutton", 
                    background=style_config['checkbutton']['background'], 
                    font=("Segoe UI", option_display_config['font_size']))