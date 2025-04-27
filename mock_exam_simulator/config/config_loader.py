import os
from pathlib import Path
import yaml
from tkinter import messagebox


def load_config() -> dict:
    """Load and validate the configuration from config.yaml."""
    try:
        config_path = Path(__file__).parent.parent.parent / "config.yaml"
        with open(config_path, "r") as file:
            config = yaml.safe_load(file)
        if not config:
            raise ValueError("Configuration file is empty")
        return config
    except FileNotFoundError:
        messagebox.showerror("Error", "Configuration file 'config.yaml' not found!")
        raise
    except yaml.YAMLError as e:
        messagebox.showerror("Error", f"Failed to parse config.yaml: {str(e)}")
        raise