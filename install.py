import subprocess
import sys
import os


def check_python_version():
    if sys.version_info < (3, 10):
        print(f"Error: Python 3.10+ required, got {sys.version}")
        sys.exit(1)
    print(f"Python version: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")


def install_dependencies():
    requirements = os.path.join(os.path.dirname(__file__), "requirements.txt")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", requirements])


def verify_install():
    try:
        import paddleocr
        import pdfplumber
        import docx
        print("All dependencies verified OK")
    except ImportError as e:
        print(f"Import error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    check_python_version()
    install_dependencies()
    verify_install()
    print("\nInstallation complete! Run: python parse.py --help")
