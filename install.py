import logging
import subprocess
import sys
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def check_python_version() -> None:
    if sys.version_info < (3, 10):
        logger.error(f"Python 3.10+ required, got {sys.version}")
        sys.exit(1)
    logger.info(f"Python version: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")


def install_dependencies() -> None:
    requirements = Path(__file__).parent / "requirements.txt"
    if not requirements.exists():
        logger.error(f"requirements.txt not found at {requirements}")
        sys.exit(1)
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", str(requirements)])


def verify_install() -> None:
    try:
        import paddleocr
        import pdfplumber
        import docx
        import tqdm
        logger.info("All dependencies verified OK")
    except ImportError as e:
        logger.error(f"Import error: {e}")
        sys.exit(1)


def main() -> None:
    check_python_version()
    install_dependencies()
    verify_install()
    logger.info("Installation complete! Run: python parse.py --help")


if __name__ == "__main__":
    main()
