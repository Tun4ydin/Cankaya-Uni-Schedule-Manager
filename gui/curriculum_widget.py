from gui.qt_compat import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QComboBox,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QLineEdit,
    QGroupBox,
    QFrame,
    Qt,
    ITEM_ENABLED,
    USER_ROLE,
)


class CurriculumWidget(QWidget):
    """
    Öğrencinin bölüm müfredatını görüntülemesini ve
    dersler arasında manuel bağlayıcılık tanımlamasını sağlar.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.manager = None
        self.current_curriculum = None
        self.current_course = None

        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(10)

        # =====================================================
        # BAŞLIK
        # =====================================================

        title = QLabel("📚 Müfredat ve Ders Bağlayıcılıkları")
        title.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                padding: 5px;
            }
        """)

        main_layout.addWidget(title)

        description = QLabel(
            "Bölümünüzün resmi müfredatını görüntüleyin ve "
            "dersler arasındaki bağlayıcılıkları manuel olarak tanımlayın."
        )

        description.setWordWrap(True)
        main_layout.addWidget(description)

        # =====================================================
        # BÖLÜM SEÇİMİ
        # =====================================================

        department_layout = QHBoxLayout()

        department_label = QLabel("Bölüm:")
        self.department_combo = QComboBox()

        department_layout.addWidget(department_label)
        department_layout.addWidget(self.department_combo, 1)

        self.load_button = QPushButton("🔄 Müfredatı Getir")
        self.load_button.clicked.connect(self.load_curriculum)

        department_layout.addWidget(self.load_button)

        main_layout.addLayout(department_layout)

        # =====================================================
        # DERS ARAMA
        # =====================================================

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(
            "Ders kodu veya ders adı ara..."
        )

        self.search_input.textChanged.connect(
            self.filter_courses
        )

        main_layout.addWidget(self.search_input)

        # =====================================================
        # ANA İÇERİK
        # =====================================================

        content_layout = QHBoxLayout()

        # -----------------------------------------------------
        # SOL: DERSLER
        # -----------------------------------------------------

        courses_box = QGroupBox("Müfredattaki Dersler")
        courses_layout = QVBoxLayout(courses_box)

        self.course_list = QListWidget()
        self.course_list.currentItemChanged.connect(
            self.course_selected
        )

        courses_layout.addWidget(self.course_list)

        content_layout.addWidget(courses_box, 1)

        # -----------------------------------------------------
        # SAĞ: BAĞLAYICILIK
        # -----------------------------------------------------

        prerequisite_box = QGroupBox(
            "Ders Bağlayıcılıkları"
        )

        prerequisite_layout = QVBoxLayout(
            prerequisite_box
        )

        self.selected_course_label = QLabel(
            "Bir ders seçin."
        )

        self.selected_course_label.setWordWrap(True)

        prerequisite_layout.addWidget(
            self.selected_course_label
        )

        self.prerequisite_list = QListWidget()

        prerequisite_layout.addWidget(
            self.prerequisite_list
        )

        # -----------------------------------------------------
        # BAĞLAYICILIK EKLE
        # -----------------------------------------------------

        add_layout = QHBoxLayout()

        self.prerequisite_combo = QComboBox()

        self.add_button = QPushButton(
            "➕ Bağlayıcılık Ekle"
        )

        self.add_button.clicked.connect(
            self.add_prerequisite
        )

        add_layout.addWidget(
            self.prerequisite_combo,
            1
        )

        add_layout.addWidget(
            self.add_button
        )

        prerequisite_layout.addLayout(
            add_layout
        )

        # -----------------------------------------------------
        # BAĞLAYICILIK SİL
        # -----------------------------------------------------

        self.remove_button = QPushButton(
            "🗑 Seçili Bağlayıcılığı Kaldır"
        )

        self.remove_button.clicked.connect(
            self.remove_prerequisite
        )

        prerequisite_layout.addWidget(
            self.remove_button
        )

        content_layout.addWidget(
            prerequisite_box,
            1
        )

        main_layout.addLayout(
            content_layout,
            1
        )

        # =====================================================
        # BİLGİ
        # =====================================================

        info = QLabel(
            "💡 Örneğin CENG114 dersini CENG218 için "
            "bağlayıcı olarak tanımlayabilirsiniz. "
            "Tanımladığınız kurallar bilgisayarınızda saklanır."
        )

        info.setWordWrap(True)

        main_layout.addWidget(info)

        self.set_buttons_enabled(False)

    # =========================================================
    # MANAGER
    # =========================================================

    def set_manager(self, manager):
        """
        Curriculum manager'ı dışarıdan bağlar.
        """

        self.manager = manager

        self.populate_departments()

    # =========================================================
    # DEPARTMENTS
    # =========================================================

    def populate_departments(self):

        if not self.manager:
            return

        self.department_combo.clear()

        departments = self.manager.get_departments()

        for code, config in departments.items():

            text = f"{code} - {config['name']}"

            self.department_combo.addItem(
                text,
                code
            )

    # =========================================================
    # CURRICULUM
    # =========================================================

    def load_curriculum(self):

        if not self.manager:
            QMessageBox.warning(
                self,
                "Hata",
                "Curriculum Manager bağlanmamış."
            )
            return

        department_code = (
            self.department_combo.currentData()
        )

        if not department_code:
            return

        self.load_button.setEnabled(False)
        self.load_button.setText(
            "⏳ Yükleniyor..."
        )

        try:

            self.current_curriculum = (
                self.manager.fetch_curriculum(
                    department_code,
                    use_cache=False
                )
            )

            self.populate_courses()

            self.set_buttons_enabled(True)

        except Exception as exc:

            QMessageBox.critical(
                self,
                "Müfredat Yüklenemedi",
                f"Müfredat alınırken hata oluştu:\n\n{exc}"
            )

        finally:

            self.load_button.setEnabled(True)
            self.load_button.setText(
                "🔄 Müfredatı Getir"
            )

    # =========================================================
    # COURSE LIST
    # =========================================================

    def populate_courses(self):

        self.course_list.clear()

        if not self.current_curriculum:
            return

        for course in self.current_curriculum.courses:

            semester_text = ""

            if course.semester:
                semester_text = (
                    f" | {course.semester}. dönem"
                )

            text = (
                f"{course.code} - "
                f"{course.name}"
                f"{semester_text}"
            )

            item = QListWidgetItem(text)

            item.setData(
                USER_ROLE,
                course.code
            )

            self.course_list.addItem(item)

        self.update_prerequisite_course_list()

    # =========================================================
    # SEARCH
    # =========================================================

    def filter_courses(self, text):

        text = text.lower().strip()

        for index in range(
            self.course_list.count()
        ):

            item = self.course_list.item(index)

            visible = (
                not text
                or text in item.text().lower()
            )

            item.setHidden(not visible)

    # =========================================================
    # COURSE SELECTED
    # =========================================================

    def course_selected(
        self,
        current,
        previous=None
    ):

        if current is None:
            self.current_course = None

            self.selected_course_label.setText(
                "Bir ders seçin."
            )

            self.prerequisite_list.clear()

            return

        course_code = current.data(
            USER_ROLE
        )

        if not course_code:
            return

        self.current_course = (
            self.current_curriculum.get_course(
                course_code
            )
        )

        if not self.current_course:
            return

        self.selected_course_label.setText(
            f"🔗 {self.current_course.code} - "
            f"{self.current_course.name}\n\n"
            f"Bu ders için alınması gereken "
            f"bağlayıcı dersleri seçin."
        )

        self.refresh_prerequisites()

    # =========================================================
    # PREREQUISITES
    # =========================================================

    def refresh_prerequisites(self):

        self.prerequisite_list.clear()

        if not self.current_course:
            return

        prerequisites = (
            self.current_course.get_all_prerequisites()
        )

        for code in prerequisites:

            item = QListWidgetItem(code)

            self.prerequisite_list.addItem(
                item
            )

    def update_prerequisite_course_list(self):

        self.prerequisite_combo.clear()

        if not self.current_curriculum:
            return

        for course in self.current_curriculum.courses:

            self.prerequisite_combo.addItem(
                f"{course.code} - {course.name}",
                course.code
            )

    # =========================================================
    # ADD
    # =========================================================

    def add_prerequisite(self):

        if not self.current_course:
            QMessageBox.warning(
                self,
                "Ders Seçilmedi",
                "Önce bağlayıcılık eklemek istediğiniz "
                "dersi seçin."
            )
            return

        prerequisite = (
            self.prerequisite_combo.currentData()
        )

        if not prerequisite:
            return

        course_code = self.current_course.code

        if prerequisite == course_code:

            QMessageBox.warning(
                self,
                "Geçersiz Bağlayıcılık",
                "Bir ders kendisinin ön koşulu olamaz."
            )

            return

        existing = (
            self.current_course.get_all_prerequisites()
        )

        if prerequisite in existing:

            QMessageBox.information(
                self,
                "Zaten Ekli",
                f"{prerequisite} zaten bu ders için "
                f"bağlayıcı olarak tanımlı."
            )

            return

        self.manager.add_manual_prerequisite(
            course_code,
            prerequisite
        )

        self.current_course.manual_prerequisites = (
            self.manager.manual_rules.get_prerequisites(
                course_code
            )
        )

        self.refresh_prerequisites()

    # =========================================================
    # REMOVE
    # =========================================================

    def remove_prerequisite(self):

        if not self.current_course:
            return

        item = (
            self.prerequisite_list.currentItem()
        )

        if not item:
            QMessageBox.warning(
                self,
                "Seçim Yok",
                "Kaldırmak istediğiniz bağlayıcılığı seçin."
            )

            return

        prerequisite = item.text()

        # Otomatik gelen ön koşul mu?
        if prerequisite in (
            self.current_course.prerequisites
        ):

            QMessageBox.information(
                self,
                "Otomatik Ön Koşul",
                "Bu ön koşul üniversitenin resmi "
                "müfredatından geliyor ve buradan silinemez."
            )

            return

        self.manager.remove_manual_prerequisite(
            self.current_course.code,
            prerequisite
        )

        self.current_course.manual_prerequisites = (
            self.manager.manual_rules.get_prerequisites(
                self.current_course.code
            )
        )

        self.refresh_prerequisites()

    # =========================================================
    # BUTTONS
    # =========================================================

    def set_buttons_enabled(self, enabled):

        self.add_button.setEnabled(enabled)
        self.remove_button.setEnabled(enabled)
