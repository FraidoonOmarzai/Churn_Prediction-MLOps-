import os
import logging

logging.basicConfig(level=logging.INFO, format="[%(asctime)s]: %(message)s:")

dirs = [
    os.path.join("src", "components"),
    os.path.join("src", "constants"),
    os.path.join("src", "pipeline"),
    os.path.join("src", "utils"),
    os.path.join("data", "raw"),
    os.path.join("data", "processed"),
    os.path.join("artifacts", "models"),
    os.path.join("artifacts", "metrics"),
    os.path.join("artifacts", "preprocessors"),
    os.path.join("tests", "unit"),
    os.path.join("tests", "integration"),
    os.path.join("tests", "data"),
    os.path.join("tests", "models"),
    "configs",
    "notebook",
    "mlruns",
    "logs",
    "scripts",
]

for dir_ in dirs:
    os.makedirs(dir_, exist_ok=True)
    # To get Git to recognize an empty directory, the unwritten rule is to put a file named .gitkeep in it
    with open(os.path.join(dir_, ".gitkeep"), "w") as f:
        logging.info(f"Creating directory:{dir_}")
        pass


files = [
    os.path.join("src", "__init__.py"),
    os.path.join("src", "components", "__init__.py"),
    os.path.join("src", "constants", "__init__.py"),
    os.path.join("src", "pipeline", "__init__.py"),
    os.path.join("src", "utils", "__init__.py"),
    os.path.join("src", "exception.py"),
    os.path.join("src", "logger.py"),
    os.path.join("data", "raw", ".gitkeep"),
    os.path.join("data", "processed", ".gitkeep"),
    os.path.join("artifacts", ".gitkeep"),
    os.path.join("tests", "__init__.py"),
    os.path.join("notebook", "experiments.ipynb"),
    os.path.join("configs", "config.yaml"),
    os.path.join("configs", "model_config.yaml"),
    "Dockerfile",
    "setup.py",
    "app.py",
    "requirements.txt",
    ".env",
]

for file_ in files:
    with open(file_, "w") as f:
        logging.info(f"Creating file: {file_}")
        pass
