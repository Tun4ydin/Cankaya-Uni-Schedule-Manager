import sys
import os

from logger import AppLog, setup_exception_hook
from gui.qt_compat import QApplication, Qt
from gui.main_window import MainWindow

def main():
    setup_exception_hook()
    AppLog.info("Çankaya Üniversitesi Ders Programı Yöneticisi başlatılıyor...", tag="SİSTEM")

    if hasattr(Qt, "HighDpiScaleFactorRoundingPolicy"):
        QApplication.setHighDpiScaleFactorRoundingPolicy(
            Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
        )
    
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    window = MainWindow()
    window.show()
    AppLog.info("Arayüz başarıyla yüklendi ve gösterildi.", tag="SİSTEM")
    
    exit_code = app.exec()
    AppLog.info(f"Uygulama sonlandı (kod: {exit_code}).", tag="SİSTEM")
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
