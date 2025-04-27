import os
import yaml
from tkinter import messagebox

def load_config():
    try:
        config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../config.yaml')
        with open(config_path, 'r') as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        messagebox.showerror("Error", "Configuration file 'config.yaml' not found!")
        # Return a default configuration as fallback
        return {
            'window': {
                'title': 'Mock Exam Simulator',
                'width': 800,
                'height': 600,
                'background': '#ffffff'
            },
            'exam': {
                'default_questions': 10,
                'default_time_limit_minutes': 60
            },
            'translator': {
                'from_lang': 'en',
                'to_lang': 'es'
            },
            'styles': {
                'button': {
                    'font': ['Segoe UI', 12],
                    'padding': 5,
                    'borderwidth': 1,
                    'relief': 'flat',
                    'default_background': '#007bff',
                    'default_foreground': '#ffffff',
                    'active_background': '#0056b3',
                    'active_foreground': '#ffffff',
                    'disabled_background': '#cccccc',
                    'disabled_foreground': '#666666'
                },
                'label': {'background': '#ffffff', 'font': ['Segoe UI', 14]},
                'entry': {'padding': 5, 'bordercolor': '#ced4da', 'relief': 'flat', 'borderwidth': 1},
                'radiobutton': {'background': '#ffffff', 'font': ['Segoe UI', 12]},
                'checkbutton': {'background': '#ffffff', 'font': ['Segoe UI', 12]},
                'progressbar': {'thickness': 20, 'background': '#007bff', 'troughcolor': '#dee2e6'},
                'active_button': {'background': '#007bff'},
                'viewed_button': {'background': '#6c757d'},
                'answered_button': {'background': '#a3e635'},
                'flagged_button': {'background': '#ff9500'}
            },
            'navigation': {
                'background': '#ffffff',
                'canvas_height': 50,
                'default_visible': True
            },
            'question_bar': {'height': 100, 'font_size': 16},
            'option_display': {'font_size': 12}
        }
    except yaml.YAMLError as e:
        messagebox.showerror("Error", f"Failed to parse config.yaml: {str(e)}")
        raise
    except Exception as e:
        messagebox.showerror("Error", f"Unexpected error loading configuration: {str(e)}")
        raise