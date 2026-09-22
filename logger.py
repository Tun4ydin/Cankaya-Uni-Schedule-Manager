import sys
import logging
import traceback
from datetime import datetime

class TerminalFormatter(logging.Formatter):
    """Custom formatter with timestamps and clean terminal styling."""
    
    COLORS = {
        logging.DEBUG: "\033[90m",      # Gray
        logging.INFO: "\033[94m",       # Bright Blue
        logging.WARNING: "\033[93m",    # Bright Yellow
        logging.ERROR: "\033[91m",      # Bright Red
        logging.CRITICAL: "\033[95m",   # Bright Magenta
    }
    RESET = "\033[0m"
    BOLD = "\033[1m"

    def format(self, record):
        timestamp = datetime.now().strftime("%H:%M:%S")
        color = self.COLORS.get(record.levelno, "")
        levelname = record.levelname
        
        tag = getattr(record, "tag", None)
        if tag:
            tag_str = f"[{tag}] "
        else:
            tag_str = ""

        # Format message
        msg = record.getMessage()
        formatted = f"{self.BOLD}[{timestamp}]{self.RESET} {color}[{levelname}]{self.RESET} {tag_str}{msg}"

        if record.exc_info:
            formatted += "\n" + "".join(traceback.format_exception(*record.exc_info))

        return formatted

# Initialize logger
logger = logging.getLogger("CankayaScheduler")
logger.setLevel(logging.DEBUG)

if not logger.handlers:
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(TerminalFormatter())
    logger.addHandler(console_handler)

class AppLog:
    @staticmethod
    def info(msg, tag=None):
        extra = {"tag": tag} if tag else {}
        logger.info(msg, extra=extra)

    @staticmethod
    def warning(msg, tag=None):
        extra = {"tag": tag} if tag else {}
        logger.warning(msg, extra=extra)

    @staticmethod
    def error(msg, tag=None, exc_info=False):
        extra = {"tag": tag} if tag else {}
        logger.error(msg, extra=extra, exc_info=exc_info)

    @staticmethod
    def debug(msg, tag=None):
        extra = {"tag": tag} if tag else {}
        logger.debug(msg, extra=extra)

    @staticmethod
    def basket(msg):
        AppLog.info(msg, tag="SEPET")

    @staticmethod
    def schedule(msg):
        AppLog.info(msg, tag="PROGRAM")

    @staticmethod
    def block(msg):
        AppLog.info(msg, tag="ETKİNLİK")

    @staticmethod
    def data(msg):
        AppLog.info(msg, tag="VERİ")

def setup_exception_hook():
    """Catches all unhandled exceptions and prints full formatted tracebacks to terminal."""
    def custom_excepthook(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        
        tb_lines = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        logger.error(f"Yakalanmamış Hata (Unhandled Exception):\n{tb_lines}", extra={"tag": "KRİTİK HATA"})

    sys.excepthook = custom_excepthook
