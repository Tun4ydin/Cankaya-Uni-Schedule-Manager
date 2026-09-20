import json

from gui.qt_compat import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QPushButton,
    QDialog,
    QLabel,
    QSplitter,
    QMessageBox,
    QProgressDialog,
    QFileDialog,
    QFrame,
    Qt,
    QThread,
    pyqtSignal,
    HORIZONTAL,
    WINDOW_MODAL,
    QApplication,
)

from data_manager import DataManager
from scheduler_engine import SchedulerEngine
from scraper import CankayaScraper

from gui.styles import StyleManager
from gui.timetable_widget import TimetableWidget
from gui.course_search_panel import CourseSearchPanel
from gui.combination_bar import CombinationBar
from gui.curriculum_widget import CurriculumWidget
from cankaya_curriculum_manager import CankayaCurriculumManager



# ============================================================
# SCRAPER THREAD
# ============================================================

class ScraperThread(QThread):
    progress_signal = pyqtSignal(int, int, str)
    finished_signal = pyqtSignal(bool, int, int, str)

    def __init__(self, data_manager, dept_list=None):
        super().__init__()

        self.data_manager = data_manager
        self.dept_list = dept_list
        self._is_cancelled = False

    def cancel(self):
        self._is_cancelled = True

    def run(self):
        scraper = CankayaScraper()

        def callback(current, total, message):
            self.progress_signal.emit(
                current,
                total,
                message
            )

        def cancel_check():
            return self._is_cancelled

        try:
            raw_entries = scraper.fetch_all_schedules(
                progress_callback=callback,
                dept_list=self.dept_list,
                cancel_check=cancel_check,
            )

            if self._is_cancelled:
                self.finished_signal.emit(
                    False,
                    0,
                    0,
                    "İşlem kullanıcı tarafından iptal edildi."
                )
                return

            if not raw_entries:
                self.finished_signal.emit(
                    False,
                    0,
                    0,
                    "Web sitesinden herhangi bir ders verisi alınamadı."
                )
                return

            self.progress_signal.emit(
                100,
                100,
                "Veriler işleniyor ve diske kaydediliyor..."
            )

            self.data_manager.process_raw_entries(
                raw_entries
            )

            course_count = len(
                self.data_manager.courses
            )

            department_count = len(
                self.data_manager.departments
            )

            self.finished_signal.emit(
                True,
                course_count,
                department_count,
                "Başarılı"
            )

        except Exception as exc:
            self.finished_signal.emit(
                False,
                0,
                0,
                str(exc)
            )


# ============================================================
# MAIN WINDOW
# ============================================================

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle(
            "Çankaya Üniversitesi - Haftalık Ders Programı Oluşturucu"
        )

        # ----------------------------------------------------
        # WINDOW SIZE
        # ----------------------------------------------------

        screen = QApplication.primaryScreen()

        if screen:
            available = screen.availableGeometry()

            self.target_w = min(
                1260,
                available.width() - 40
            )

            self.target_h = min(
                820,
                available.height() - 40
            )

            self.resize(
                self.target_w,
                self.target_h
            )

            pos_x = (
                available.x()
                + (
                    available.width()
                    - self.target_w
                ) // 2
            )

            pos_y = (
                available.y()
                + (
                    available.height()
                    - self.target_h
                ) // 2
            )

            self.move(
                pos_x,
                pos_y
            )

        else:
            self.target_w = 1240
            self.target_h = 800

            self.resize(
                self.target_w,
                self.target_h
            )

        # ----------------------------------------------------
        # CORE OBJECTS
        # ----------------------------------------------------

        self.data_manager = DataManager()

        self.scheduler_engine = SchedulerEngine()

        self.curriculum_manager = CankayaCurriculumManager()

        self.current_combinations = []

        self.scraper_thread = None


        # Curriculum dialog
        self.curriculum_window = None
        self.curriculum_widget = None

        # ----------------------------------------------------
        # THEME
        # ----------------------------------------------------

        saved_theme = (
            self.data_manager.student_profile.get(
                "theme",
                "cankaya"
            )
        )

        StyleManager.set_active_theme(
            saved_theme
        )

        # ----------------------------------------------------
        # UI
        # ----------------------------------------------------

        self.init_ui()

        self.setStyleSheet(
            StyleManager.get_stylesheet()
        )

    # ========================================================
    # UI
    # ========================================================

    def init_ui(self):

        central_widget = QWidget()

        self.setCentralWidget(
            central_widget
        )

        main_layout = QVBoxLayout(
            central_widget
        )

        main_layout.setContentsMargins(
            10,
            10,
            10,
            10
        )

        main_layout.setSpacing(8)

        # ====================================================
        # HEADER
        # ====================================================

        header_frame = QFrame()

        header_frame.setObjectName(
            "panelFrame"
        )

        header_layout = QHBoxLayout(
            header_frame
        )

        header_layout.setContentsMargins(
            10,
            6,
            10,
            6
        )

        header_layout.setSpacing(8)

        # Title
        title_label = QLabel(
            "🎓 Çankaya Üniversitesi Ders Programı Oluşturucu"
        )

        title_label.setObjectName(
            "titleLabel"
        )

        header_layout.addWidget(
            title_label
        )

        header_layout.addStretch()

        # ====================================================
        # THEME BUTTON
        # ====================================================

        active_theme = (
            StyleManager.get_active_theme()
        )

        if active_theme == "cankaya":
            theme_text = "🎨 ☀️ Açık Tema"
        else:
            theme_text = "🎨 🌙 Karanlık Tema"

        self.btn_theme = QPushButton(
            theme_text
        )

        self.btn_theme.setToolTip(
            "Açık ve karanlık tema arasında geçiş yap"
        )

        self.btn_theme.clicked.connect(
            self.toggle_theme
        )

        header_layout.addWidget(
            self.btn_theme
        )

        # ====================================================
        # REFRESH BUTTON
        # ====================================================

        self.btn_refresh = QPushButton(
            "🔄 Verileri Çek"
        )

        self.btn_refresh.setToolTip(
            "Çankaya Üniversitesi web sitesinden "
            "güncel ders programlarını çeker"
        )

        self.btn_refresh.clicked.connect(
            self.start_web_scraping
        )

        header_layout.addWidget(
            self.btn_refresh
        )

        # ====================================================
        # SCHEDULE GENERATE
        # ====================================================

        self.btn_generate = QPushButton(
            "⚡ Program Oluştur"
        )

        self.btn_generate.setObjectName(
            "primaryButton"
        )

        self.btn_generate.clicked.connect(
            self.generate_schedule_combinations
        )

        header_layout.addWidget(
            self.btn_generate
        )

        # ====================================================
        # EXPORT
        # ====================================================

        self.btn_export = QPushButton(
            "💾 Dışa Aktar"
        )

        self.btn_export.setToolTip(
            "Haftalık programı PNG veya JSON olarak kaydet"
        )

        self.btn_export.clicked.connect(
            self.export_schedule
        )

        header_layout.addWidget(
            self.btn_export
        )

        # ====================================================
        # CURRICULUM
        # ====================================================

        self.btn_curriculum = QPushButton(
            "📚 Müfredat"
        )

        self.btn_curriculum.setToolTip(
            "Bölümlerin resmi müfredatlarını görüntüle "
            "ve ders bağlayıcılıklarını düzenle"
        )

        self.btn_curriculum.clicked.connect(
            self.open_curriculum
        )

        header_layout.addWidget(
            self.btn_curriculum
        )

        main_layout.addWidget(
            header_frame
        )

        # ====================================================
        # MAIN SPLITTER
        # ====================================================

        splitter = QSplitter(
            HORIZONTAL
        )

        # ----------------------------------------------------
        # LEFT PANEL
        # ----------------------------------------------------

        self.search_panel = CourseSearchPanel(
            self.data_manager
        )

        self.search_panel.courses_changed.connect(
            self.on_basket_courses_changed
        )

        splitter.addWidget(
            self.search_panel
        )

        # ----------------------------------------------------
        # RIGHT PANEL
        # ----------------------------------------------------

        right_container = QWidget()

        right_layout = QVBoxLayout(
            right_container
        )

        right_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        right_layout.setSpacing(6)

        # Combination bar
        self.combination_bar = CombinationBar()

        self.combination_bar.index_changed.connect(
            self.display_combination_by_index
        )

        self.combination_bar.preferences_changed.connect(
            self.on_preferences_changed
        )

        right_layout.addWidget(
            self.combination_bar
        )

        # Timetable
        self.timetable_widget = TimetableWidget(
            data_manager=self.data_manager
        )

        right_layout.addWidget(
            self.timetable_widget
        )

        splitter.addWidget(
            right_container
        )

        # ----------------------------------------------------
        # SPLITTER SIZE
        # ----------------------------------------------------

        left_width = min(
            320,
            int(self.target_w * 0.26)
        )

        splitter.setSizes([
            left_width,
            self.target_w - left_width
        ])

        splitter.setCollapsible(
            0,
            False
        )

        splitter.setCollapsible(
            1,
            False
        )

        main_layout.addWidget(
            splitter
        )

        # ----------------------------------------------------
        # FIRST START MESSAGE
        # ----------------------------------------------------

        if not self.data_manager.courses:

            QMessageBox.information(
                self,
                "Hoş Geldiniz",
                "Henüz kaydedilmiş ders verisi bulunamadı.\n\n"
                "Lütfen 'Webden Verileri Çek' butonuna "
                "basarak ders bilgilerini indirin."
            )

    # ========================================================
    # CURRICULUM
    # ========================================================

    def open_curriculum(self):

        # Zaten açık olan müfredat penceresi varsa
        # yeni pencere açma.
        if (
            self.curriculum_window is not None
            and self.curriculum_window.isVisible()
        ):
            self.curriculum_window.raise_()
            self.curriculum_window.activateWindow()
            return

        self.curriculum_window = QDialog(self)

        self.curriculum_window.setWindowTitle(
            "📚 Çankaya Üniversitesi - Müfredat Yönetimi"
        )

        self.curriculum_window.resize(
            1150,
            750
        )

        self.curriculum_window.setModal(False)

        layout = QVBoxLayout(
            self.curriculum_window
        )

        layout.setContentsMargins(
            10,
            10,
            10,
            10
        )

        # --------------------------------------------------------
        # CURRICULUM WIDGET
        # --------------------------------------------------------

        self.curriculum_widget = CurriculumWidget(
            self.curriculum_window
        )

        # --------------------------------------------------------
        # CURRICULUM MANAGER'I BAĞLA
        # --------------------------------------------------------

        self.curriculum_widget.set_manager(
            self.curriculum_manager
        )

        layout.addWidget(
            self.curriculum_widget
        )

        # --------------------------------------------------------
        # PENCERE KAPANINCA REFERANSLARI TEMİZLE
        # --------------------------------------------------------

        self.curriculum_window.finished.connect(
            self.on_curriculum_closed
        )

        self.curriculum_window.show()

    def on_curriculum_closed(self):

        self.curriculum_widget = None
        self.curriculum_window = None

    # ========================================================
    # WEB SCRAPING
    # ========================================================

    def start_web_scraping(self):

        msg_box = QMessageBox(
            self
        )

        msg_box.setWindowTitle(
            "Veri Çekme Modu"
        )

        msg_box.setText(
            "Nasıl bir güncelleme yapmak istersiniz?"
        )

        btn_quick = msg_box.addButton(
            "⚡ Hızlı Güncelleme (Ana Bölümler ~15 sn)",
            QMessageBox.ButtonRole.ActionRole
        )

        btn_full = msg_box.addButton(
            "🌐 Tüm Üniversite (100+ Bölüm ~1-2 dk)",
            QMessageBox.ButtonRole.ActionRole
        )

        btn_cancel = msg_box.addButton(
            "İptal",
            QMessageBox.ButtonRole.RejectRole
        )

        msg_box.exec()

        clicked = msg_box.clickedButton()

        if clicked == btn_cancel:
            return

        dept_list = None

        if clicked == btn_quick:

            dept_list = [
                "CENG",
                "SENG",
                "ECE",
                "IE",
                "ME",
                "MATH",
                "PHYS",
                "CHEM",
                "ENG",
                "TURK",
                "AİIT",
                "MAN",
                "LAW",
            ]

        self.progress_dialog = QProgressDialog(
            "Veriler indiriliyor...",
            "İptal",
            0,
            100,
            self
        )

        self.progress_dialog.setWindowModality(
            WINDOW_MODAL
        )

        self.progress_dialog.setAutoClose(
            False
        )

        self.progress_dialog.setAutoReset(
            False
        )

        self.progress_dialog.setValue(
            0
        )

        self.progress_dialog.show()

        self.scraper_thread = ScraperThread(
            self.data_manager,
            dept_list=dept_list
        )

        self.scraper_thread.progress_signal.connect(
            self.on_scraping_progress
        )

        self.scraper_thread.finished_signal.connect(
            self.on_scraping_finished
        )

        self.progress_dialog.canceled.connect(
            self.scraper_thread.cancel
        )

        self.scraper_thread.start()

    def on_scraping_progress(
        self,
        current,
        total,
        message
    ):

        percent = int(
            (current / max(1, total))
            * 100
        )

        self.progress_dialog.setValue(
            percent
        )

        self.progress_dialog.setLabelText(
            message
        )

    def on_scraping_finished(
        self,
        success,
        course_count,
        department_count,
        message
    ):

        self.progress_dialog.close()

        if success:

            self.search_panel.populate_departments()

            self.search_panel.on_search_changed()

            QMessageBox.information(
                self,
                "Başarılı",
                f"Toplam {course_count} ders ve "
                f"{department_count} bölüm bilgisi "
                f"başarıyla güncellendi!"
            )

        else:

            if (
                not self.scraper_thread
                or not self.scraper_thread._is_cancelled
            ):

                QMessageBox.warning(
                    self,
                    "Hata",
                    "Veriler güncellenirken sorun oluştu:\n"
                    f"{message}"
                )

    # ========================================================
    # BASKET
    # ========================================================

    def on_basket_courses_changed(self):

        target_dict = (
            self.search_panel
            .get_selected_target_dict()
        )

        if not target_dict:

            self.timetable_widget.clear_schedule()

            self.combination_bar.set_combinations_count(
                0
            )

            return

        all_manual_sections = []

        for course_code, sections in target_dict.items():

            all_manual_sections.extend(
                sections
            )

        self.timetable_widget.display_schedule(
            all_manual_sections
        )

    # ========================================================
    # SCHEDULE GENERATION
    # ========================================================

    def generate_schedule_combinations(self):

        target_dict = (
            self.search_panel
            .get_selected_target_dict()
        )

        if not target_dict:

            QMessageBox.warning(
                self,
                "Ders Seçilmedi",
                "Lütfen önce sol panelden "
                "alınmak istenen dersleri "
                "sepete ekleyin."
            )

            return

        preferences = {
            "no_morning": (
                self.combination_bar
                .chk_no_morning
                .isChecked()
            ),

            "free_friday": (
                self.combination_bar
                .chk_free_friday
                .isChecked()
            ),

            "free_monday": (
                self.combination_bar
                .chk_free_monday
                .isChecked()
            ),
        }

        self.current_combinations = (
            self.scheduler_engine
            .generate_combinations(
                target_dict,
                preferences=preferences
            )
        )

        count = len(
            self.current_combinations
        )

        self.combination_bar.set_combinations_count(
            count
        )

        if count > 0:

            self.display_combination_by_index(
                0
            )

            QMessageBox.information(
                self,
                "Kombinasyon Üretildi",
                f"Çakışma oluşturmayan toplam "
                f"{count} adet ders programı "
                f"kombinasyonu bulundu!"
            )

        else:

            self.timetable_widget.clear_schedule()

            QMessageBox.warning(
                self,
                "Çakışmasız Program Bulunamadı",
                "Seçtiğiniz dersler/section'lar "
                "arasında çakışma oluşturmayan "
                "bir kombinasyon bulunamadı.\n\n"
                "Lütfen farklı section'lar seçmeyi "
                "veya filtreleri esnetmeyi deneyin."
            )

    def on_preferences_changed(
        self,
        preferences
    ):

        target_dict = (
            self.search_panel
            .get_selected_target_dict()
        )

        if target_dict:
            self.generate_schedule_combinations()

    # ========================================================
    # DISPLAY COMBINATION
    # ========================================================

    def display_combination_by_index(
        self,
        index
    ):

        if (
            0 <= index
            < len(self.current_combinations)
        ):

            combo_sections = (
                self.current_combinations[index]
            )

            self.timetable_widget.display_schedule(
                combo_sections
            )

            total_credit = 0
            total_ects = 0

            distinct_courses = set()

            for section in combo_sections:

                if (
                    section.course_code
                    not in distinct_courses
                ):

                    distinct_courses.add(
                        section.course_code
                    )

                    credits, ects = (
                        self.data_manager
                        .get_course_credits(
                            section.course_code
                        )
                    )

                    total_credit += credits
                    total_ects += ects

            self.combination_bar.set_combination_credits(
                len(distinct_courses),
                total_credit,
                total_ects
            )

        else:

            self.combination_bar.set_combination_credits(
                0,
                0,
                0
            )

    # ========================================================
    # EXPORT
    # ========================================================

    def export_schedule(self):

        if (
            self.timetable_widget
            .findChildren(QWidget)
            == 0
        ):

            QMessageBox.warning(
                self,
                "Program Boş",
                "Dışa aktarmak için önce "
                "bir ders programı oluşturun."
            )

            return

        filepath, selected_filter = (
            QFileDialog.getSaveFileName(
                self,
                "Ders Programını Kaydet",
                "haftalik_program.png",
                "PNG Görsel (*.png);;"
                "JSON Dosyası (*.json)"
            )
        )

        if not filepath:
            return

        try:

            if filepath.lower().endswith(
                ".json"
            ):

                current_index = (
                    self.combination_bar
                    .current_index
                )

                if (
                    0 <= current_index
                    < len(self.current_combinations)
                ):

                    sections = (
                        self.current_combinations[
                            current_index
                        ]
                    )

                else:
                    sections = []

                data = [
                    section.to_dict()
                    for section in sections
                ]

                with open(
                    filepath,
                    "w",
                    encoding="utf-8"
                ) as file:

                    json.dump(
                        data,
                        file,
                        ensure_ascii=False,
                        indent=2
                    )

                QMessageBox.information(
                    self,
                    "Kaydedildi",
                    "Program JSON olarak kaydedildi:\n"
                    f"{filepath}"
                )

            else:

                pixmap = (
                    self.timetable_widget.grab()
                )

                pixmap.save(
                    filepath,
                    "PNG"
                )

                QMessageBox.information(
                    self,
                    "Kaydedildi",
                    "Program görsel olarak kaydedildi:\n"
                    f"{filepath}"
                )

        except Exception as exc:

            QMessageBox.critical(
                self,
                "Hata",
                "Dosya kaydedilirken hata oluştu:\n"
                f"{exc}"
            )

    # ========================================================
    # THEME
    # ========================================================

    def toggle_theme(self):

        new_theme = (
            StyleManager.toggle_theme()
        )

        self.setStyleSheet(
            StyleManager.get_stylesheet()
        )

        self.data_manager.student_profile[
            "theme"
        ] = new_theme

        self.data_manager.save_student_profile(
            self.data_manager.student_profile.get(
                "primary_dept",
                "CENG"
            ),
            self.data_manager.student_profile.get(
                "secondary_dept",
                "YOK"
            ),
            self.data_manager.student_profile.get(
                "secondary_type",
                "YOK"
            )
        )

        if new_theme == "cankaya":

            self.btn_theme.setText(
                "🎨 Tema: ☀️ Açık (Çankaya)"
            )

        else:

            self.btn_theme.setText(
                "🎨 Tema: 🌙 Karanlık"
            )

        self.timetable_widget.refresh_theme()

        if hasattr(
            self.search_panel,
            "refresh_theme"
        ):

            self.search_panel.refresh_theme()

        # Müfredat penceresi açıksa temasını yenile
        if (
            self.curriculum_widget is not None
            and hasattr(
                self.curriculum_widget,
                "refresh_theme"
            )
        ):

            self.curriculum_widget.refresh_theme()
