# Calmio Meditation App

Prototype breathing exercise built with **PySide6**. A central circle expands while you hold the space bar (or press the circle), and contracts when released. Each completed inhale+exhale cycle increments the breath counter and slightly increases the duration of the next cycle.

The application now features a dynamic animated background that gently cycles through chakra-inspired gradients during a session. The colors transition roughly every four minutes, creating a relaxing atmosphere without interfering with on-screen elements.

## Requirements

- Python 3.8+
- PySide6

Install dependencies in a virtual environment with the provided batch script.

## Usage

On Windows:

```bat
run_app.bat
```

The script creates a `venv` folder if missing, installs dependencies, pulls the latest code, and runs the app.

On other systems, manually create a virtual environment and run `python main.py`.
