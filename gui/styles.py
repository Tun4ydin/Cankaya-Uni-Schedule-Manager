class ModernStyle:
    # Color palette constants
    BG_DARK = "#181825"
    SURFACE_DARK = "#1e1e2e"
    CARD_BG = "#2b2b3d"
    TEXT_MAIN = "#cdd6f4"
    TEXT_MUTED = "#a6adc8"
    ACCENT_CYAN = "#89b4fa"
    ACCENT_HOVER = "#74c7ec"
    ACCENT_PURPLE = "#cba6f7"
    BORDER_COLOR = "#45475a"
    CONFLICT_BG = "#451a24"
    CONFLICT_BORDER = "#f38ba8"
    CONFLICT_TEXT = "#f38ba8"
    SUCCESS_BG = "#1e3a29"
    SUCCESS_BORDER = "#a6e3a1"

    # Rich, fully opaque color palette for courses in schedule (Dark Theme)
    COURSE_COLORS = [
        ("#1e3a8a", "#60a5fa", "#ffffff"), # Opaque Deep Blue
        ("#064e3b", "#34d399", "#ffffff"), # Opaque Deep Emerald
        ("#4c1d95", "#c084fc", "#ffffff"), # Opaque Deep Purple
        ("#7c2d12", "#fb923c", "#ffffff"), # Opaque Deep Orange
        ("#134e4a", "#2dd4bf", "#ffffff"), # Opaque Deep Teal
        ("#831843", "#f472b6", "#ffffff"), # Opaque Deep Pink
        ("#312e81", "#818cf8", "#ffffff"), # Opaque Deep Indigo
        ("#713f12", "#fde047", "#ffffff"), # Opaque Deep Amber
    ]

    @classmethod
    def get_stylesheet(cls):
        return f"""
        QMainWindow, QDialog {{
            background-color: {cls.BG_DARK};
            color: {cls.TEXT_MAIN};
            font-family: 'Helvetica Neue', Arial, sans-serif;
            font-size: 13px;
        }}

        QWidget {{
            color: {cls.TEXT_MAIN};
            font-family: 'Helvetica Neue', Arial, sans-serif;
        }}

        /* Header & Labels */
        QLabel {{
            color: {cls.TEXT_MAIN};
        }}

        QLabel#titleLabel {{
            font-size: 18px;
            font-weight: bold;
            color: {cls.ACCENT_CYAN};
        }}

        QLabel#sectionHeader {{
            font-size: 14px;
            font-weight: bold;
            color: {cls.ACCENT_PURPLE};
            padding-bottom: 4px;
        }}

        /* Group Box & Frames */
        QFrame#panelFrame {{
            background-color: {cls.SURFACE_DARK};
            border: 1px solid {cls.BORDER_COLOR};
            border-radius: 8px;
            padding: 8px;
        }}

        QGroupBox {{
            background-color: {cls.SURFACE_DARK};
            border: 1px solid {cls.BORDER_COLOR};
            border-radius: 8px;
            margin-top: 12px;
            font-weight: bold;
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top left;
            left: 10px;
            padding: 0 5px;
            color: {cls.ACCENT_CYAN};
        }}

        /* Line Edits & Combo Boxes */
        QLineEdit, QComboBox {{
            background-color: {cls.CARD_BG};
            border: 1px solid {cls.BORDER_COLOR};
            border-radius: 6px;
            padding: 6px 10px;
            color: {cls.TEXT_MAIN};
            font-size: 13px;
        }}
        QLineEdit:focus, QComboBox:focus {{
            border: 1px solid {cls.ACCENT_CYAN};
        }}
        QComboBox::drop-down {{
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 20px;
            border-left: none;
        }}
        QComboBox QAbstractItemView {{
            background-color: {cls.CARD_BG};
            color: {cls.TEXT_MAIN};
            selection-background-color: {cls.ACCENT_CYAN};
            selection-color: #11111b;
            border: 1px solid {cls.BORDER_COLOR};
        }}

        /* Buttons */
        QPushButton {{
            background-color: {cls.CARD_BG};
            border: 1px solid {cls.BORDER_COLOR};
            border-radius: 6px;
            padding: 7px 14px;
            color: {cls.TEXT_MAIN};
            font-weight: 600;
        }}
        QPushButton:hover {{
            background-color: {cls.BORDER_COLOR};
            border-color: {cls.ACCENT_CYAN};
        }}
        QPushButton:pressed {{
            background-color: {cls.ACCENT_CYAN};
            color: #11111b;
        }}

        QPushButton#primaryButton {{
            background-color: {cls.ACCENT_CYAN};
            color: #11111b;
            border: none;
            font-weight: bold;
        }}
        QPushButton#primaryButton:hover {{
            background-color: {cls.ACCENT_HOVER};
        }}

        QPushButton#dangerButton {{
            background-color: #f38ba8;
            color: #11111b;
            border: none;
            font-weight: bold;
        }}
        QPushButton#dangerButton:hover {{
            background-color: #e57493;
        }}

        /* List Widgets & Tree Widgets */
        QListWidget, QTreeWidget {{
            background-color: {cls.CARD_BG};
            border: 1px solid {cls.BORDER_COLOR};
            border-radius: 6px;
            padding: 4px;
            color: {cls.TEXT_MAIN};
        }}
        QListWidget::item, QTreeWidget::item {{
            padding: 6px;
            border-radius: 4px;
        }}
        QListWidget::item:hover, QTreeWidget::item:hover {{
            background-color: {cls.BORDER_COLOR};
        }}
        QListWidget::item:selected, QTreeWidget::item:selected {{
            background-color: {cls.ACCENT_CYAN};
            color: #11111b;
        }}

        /* Table Widget */
        QTableWidget {{
            background-color: {cls.SURFACE_DARK};
            border: 1px solid {cls.BORDER_COLOR};
            gridline-color: {cls.BORDER_COLOR};
            border-radius: 8px;
        }}
        QHeaderView::section {{
            background-color: {cls.CARD_BG};
            color: {cls.ACCENT_CYAN};
            font-weight: bold;
            padding: 8px;
            border: 1px solid {cls.BORDER_COLOR};
        }}
        QTableCornerButton::section {{
            background-color: {cls.CARD_BG};
            border: 1px solid {cls.BORDER_COLOR};
        }}

        /* Checkboxes & Radio Buttons */
        QCheckBox {{
            spacing: 6px;
            color: {cls.TEXT_MAIN};
        }}
        QCheckBox::indicator {{
            width: 16px;
            height: 16px;
            border: 1px solid {cls.BORDER_COLOR};
            border-radius: 4px;
            background-color: {cls.CARD_BG};
        }}
        QCheckBox::indicator:checked {{
            background-color: {cls.ACCENT_CYAN};
            border-color: {cls.ACCENT_CYAN};
        }}

        /* Scrollbars */
        QScrollBar:vertical {{
            border: none;
            background: {cls.SURFACE_DARK};
            width: 8px;
            border-radius: 4px;
        }}
        QScrollBar::handle:vertical {{
            background: {cls.BORDER_COLOR};
            border-radius: 4px;
            min-height: 20px;
        }}
        QScrollBar::handle:vertical:hover {{
            background: {cls.ACCENT_CYAN};
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}

        QScrollBar:horizontal {{
            border: none;
            background: {cls.SURFACE_DARK};
            height: 8px;
            border-radius: 4px;
        }}
        QScrollBar::handle:horizontal {{
            background: {cls.BORDER_COLOR};
            border-radius: 4px;
            min-width: 20px;
        }}
        QScrollBar::handle:horizontal:hover {{
            background: {cls.ACCENT_CYAN};
        }}
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
            width: 0px;
        }}

        /* Progress Bar */
        QProgressBar {{
            border: 1px solid {cls.BORDER_COLOR};
            border-radius: 6px;
            text-align: center;
            background-color: {cls.CARD_BG};
            color: {cls.TEXT_MAIN};
            font-weight: bold;
        }}
        QProgressBar::chunk {{
            background-color: {cls.ACCENT_CYAN};
            border-radius: 5px;
        }}

        /* Summary Card */
        QFrame#summaryCard {{
            background-color: #181825;
            border: 1px solid #313244;
            border-radius: 8px;
            padding: 6px 10px;
        }}
        QLabel#summaryTitle {{
            font-weight: bold;
            color: #89dceb;
            font-size: 11px;
        }}
        QLabel#summaryStats {{
            font-weight: bold;
            color: #cdd6f4;
            font-size: 13px;
        }}
        QLabel#summaryHours {{
            color: #a6adc8;
            font-size: 11px;
        }}
        """


class CankayaStyle:
    THEME_NAME = "cankaya"

    # Çankaya University Official Brand Palette
    BG_LIGHT = "#f1f5f9"
    SURFACE_LIGHT = "#ffffff"
    CARD_BG = "#ffffff"
    NAVY_PRIMARY = "#002855"
    NAVY_LIGHT = "#003b7a"
    NAVY_DARK = "#001b3a"
    GOLD_ACCENT = "#d49a17"
    GOLD_HOVER = "#e5a823"
    TEXT_MAIN = "#0f172a"
    TEXT_MUTED = "#475569"
    BORDER_COLOR = "#cbd5e1"
    CONFLICT_BG = "#fee2e2"
    CONFLICT_BORDER = "#ef4444"
    CONFLICT_TEXT = "#991b1b"
    SUCCESS_BG = "#dcfce7"
    SUCCESS_BORDER = "#22c55e"

    # Saturated, fully opaque pastel color palette for courses in schedule (Light Theme)
    COURSE_COLORS = [
        ("#bfdbfe", "#1d4ed8", "#1e3a8a"), # Opaque Solid Blue
        ("#fde68a", "#b45309", "#78350f"), # Opaque Solid Amber
        ("#bbf7d0", "#15803d", "#14532d"), # Opaque Solid Emerald
        ("#ddd6fe", "#7c3aed", "#4c1d95"), # Opaque Solid Purple
        ("#fed7aa", "#c2410c", "#7c2d12"), # Opaque Solid Orange
        ("#99f6e4", "#0f766e", "#134e4a"), # Opaque Solid Teal
        ("#fbcfe8", "#be123c", "#831843"), # Opaque Solid Rose
        ("#c7d2fe", "#4338ca", "#312e81"), # Opaque Solid Indigo
    ]

    @classmethod
    def get_stylesheet(cls):
        return f"""
        QMainWindow, QDialog {{
            background-color: {cls.BG_LIGHT};
            color: {cls.TEXT_MAIN};
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            font-size: 13px;
        }}

        QWidget {{
            color: {cls.TEXT_MAIN};
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
        }}

        /* Header & Labels */
        QLabel {{
            color: {cls.TEXT_MAIN};
        }}

        QLabel#titleLabel {{
            font-size: 17px;
            font-weight: bold;
            color: {cls.NAVY_PRIMARY};
        }}

        QLabel#sectionHeader {{
            font-size: 14px;
            font-weight: bold;
            color: {cls.NAVY_PRIMARY};
            padding-bottom: 4px;
        }}

        /* Group Box & Frames */
        QFrame#panelFrame {{
            background-color: {cls.SURFACE_LIGHT};
            border: 1px solid {cls.BORDER_COLOR};
            border-top: 3px solid {cls.NAVY_PRIMARY};
            border-radius: 8px;
            padding: 8px;
        }}

        QGroupBox {{
            background-color: {cls.SURFACE_LIGHT};
            border: 1px solid {cls.BORDER_COLOR};
            border-top: 3px solid {cls.NAVY_PRIMARY};
            border-radius: 8px;
            margin-top: 14px;
            font-weight: bold;
            padding-top: 6px;
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top left;
            left: 10px;
            padding: 2px 8px;
            color: {cls.NAVY_PRIMARY};
            background-color: {cls.SURFACE_LIGHT};
            border-radius: 4px;
        }}

        /* Line Edits & Combo Boxes */
        QLineEdit, QComboBox {{
            background-color: #f8fafc;
            border: 1px solid {cls.BORDER_COLOR};
            border-radius: 6px;
            padding: 6px 10px;
            color: {cls.TEXT_MAIN};
            font-size: 13px;
        }}
        QLineEdit:focus, QComboBox:focus {{
            border: 2px solid {cls.NAVY_PRIMARY};
            background-color: #ffffff;
        }}
        QComboBox::drop-down {{
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 20px;
            border-left: none;
        }}
        QComboBox QAbstractItemView {{
            background-color: #ffffff;
            color: {cls.TEXT_MAIN};
            selection-background-color: {cls.NAVY_PRIMARY};
            selection-color: #ffffff;
            border: 1px solid {cls.BORDER_COLOR};
        }}

        /* Buttons */
        QPushButton {{
            background-color: #ffffff;
            border: 1px solid {cls.BORDER_COLOR};
            border-radius: 6px;
            padding: 7px 14px;
            color: {cls.NAVY_PRIMARY};
            font-weight: 600;
        }}
        QPushButton:hover {{
            background-color: #f1f5f9;
            border-color: {cls.NAVY_PRIMARY};
        }}
        QPushButton:pressed {{
            background-color: {cls.NAVY_PRIMARY};
            color: #ffffff;
        }}

        QPushButton#primaryButton {{
            background-color: {cls.NAVY_PRIMARY};
            color: #ffffff;
            border: none;
            font-weight: bold;
        }}
        QPushButton#primaryButton:hover {{
            background-color: {cls.NAVY_LIGHT};
        }}

        QPushButton#dangerButton {{
            background-color: #fee2e2;
            color: #991b1b;
            border: 1px solid #fca5a5;
            font-weight: bold;
        }}
        QPushButton#dangerButton:hover {{
            background-color: #fecaca;
            border-color: #f87171;
        }}

        /* List Widgets & Tree Widgets */
        QListWidget, QTreeWidget {{
            background-color: #ffffff;
            border: 1px solid {cls.BORDER_COLOR};
            border-radius: 6px;
            padding: 4px;
            color: {cls.TEXT_MAIN};
        }}
        QListWidget::item, QTreeWidget::item {{
            padding: 6px;
            border-radius: 4px;
            border-bottom: 1px solid #f1f5f9;
        }}
        QListWidget::item:hover, QTreeWidget::item:hover {{
            background-color: #f8fafc;
        }}
        QListWidget::item:selected, QTreeWidget::item:selected {{
            background-color: {cls.NAVY_PRIMARY};
            color: #ffffff;
        }}

        /* Table Widget */
        QTableWidget {{
            background-color: #ffffff;
            border: 1px solid {cls.BORDER_COLOR};
            gridline-color: #e2e8f0;
            border-radius: 8px;
        }}
        QHeaderView::section {{
            background-color: {cls.NAVY_PRIMARY};
            color: #ffffff;
            font-weight: bold;
            padding: 8px;
            border: 1px solid {cls.NAVY_LIGHT};
        }}
        QTableCornerButton::section {{
            background-color: {cls.NAVY_PRIMARY};
            border: 1px solid {cls.NAVY_LIGHT};
        }}

        /* Checkboxes & Radio Buttons */
        QCheckBox {{
            spacing: 6px;
            color: {cls.TEXT_MAIN};
        }}
        QCheckBox::indicator {{
            width: 16px;
            height: 16px;
            border: 1px solid {cls.BORDER_COLOR};
            border-radius: 4px;
            background-color: #ffffff;
        }}
        QCheckBox::indicator:checked {{
            background-color: {cls.NAVY_PRIMARY};
            border-color: {cls.NAVY_PRIMARY};
        }}

        /* Scrollbars */
        QScrollBar:vertical {{
            border: none;
            background: #f1f5f9;
            width: 8px;
            border-radius: 4px;
        }}
        QScrollBar::handle:vertical {{
            background: #cbd5e1;
            border-radius: 4px;
            min-height: 20px;
        }}
        QScrollBar::handle:vertical:hover {{
            background: {cls.NAVY_PRIMARY};
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}

        QScrollBar:horizontal {{
            border: none;
            background: #f1f5f9;
            height: 8px;
            border-radius: 4px;
        }}
        QScrollBar::handle:horizontal {{
            background: #cbd5e1;
            border-radius: 4px;
            min-width: 20px;
        }}
        QScrollBar::handle:horizontal:hover {{
            background: {cls.NAVY_PRIMARY};
        }}
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
            width: 0px;
        }}

        /* Progress Bar */
        QProgressBar {{
            border: 1px solid {cls.BORDER_COLOR};
            border-radius: 6px;
            text-align: center;
            background-color: #ffffff;
            color: {cls.TEXT_MAIN};
            font-weight: bold;
        }}
        QProgressBar::chunk {{
            background-color: {cls.NAVY_PRIMARY};
            border-radius: 5px;
        }}

        /* Summary Card */
        QFrame#summaryCard {{
            background-color: #e8f0fe;
            border: 1px solid #b9d5fc;
            border-left: 4px solid {cls.NAVY_PRIMARY};
            border-radius: 8px;
            padding: 6px 10px;
        }}
        QLabel#summaryTitle {{
            font-weight: bold;
            color: {cls.NAVY_PRIMARY};
            font-size: 11px;
        }}
        QLabel#summaryStats {{
            font-weight: bold;
            color: {cls.NAVY_PRIMARY};
            font-size: 13px;
        }}
        QLabel#summaryHours {{
            color: {cls.TEXT_MUTED};
            font-size: 11px;
        }}
        """


class StyleManager:
    _current_theme = "cankaya"  # "cankaya" (default) or "modern"

    @classmethod
    def get_active_theme(cls):
        return cls._current_theme

    @classmethod
    def set_active_theme(cls, theme_name):
        if theme_name in ("cankaya", "modern"):
            cls._current_theme = theme_name

    @classmethod
    def toggle_theme(cls):
        cls._current_theme = "modern" if cls._current_theme == "cankaya" else "cankaya"
        return cls._current_theme

    @classmethod
    def get_style_class(cls, theme_name=None):
        t = theme_name or cls._current_theme
        return CankayaStyle if t == "cankaya" else ModernStyle

    @classmethod
    def get_stylesheet(cls, theme_name=None):
        return cls.get_style_class(theme_name).get_stylesheet()

    @classmethod
    def get_course_colors(cls, theme_name=None):
        return cls.get_style_class(theme_name).COURSE_COLORS

    @classmethod
    def get_conflict_style(cls, theme_name=None):
        style = cls.get_style_class(theme_name)
        return style.CONFLICT_BG, style.CONFLICT_BORDER, style.CONFLICT_TEXT

    @classmethod
    def get_custom_block_style(cls, color_name="amber", theme_name=None):
        is_dark = (theme_name or cls._current_theme) == "modern"
        palettes = {
            "amber": (("#78350f", "#f59e0b", "#ffffff") if is_dark else ("#fef3c7", "#d97706", "#78350f")),
            "emerald": (("#064e3b", "#10b981", "#ffffff") if is_dark else ("#d1fae5", "#059669", "#064e3b")),
            "blue": (("#1e3a8a", "#3b82f6", "#ffffff") if is_dark else ("#dbeafe", "#2563eb", "#1e3a8a")),
            "purple": (("#581c87", "#a855f7", "#ffffff") if is_dark else ("#f3e8ff", "#9333ea", "#581c87")),
            "rose": (("#831843", "#f43f5e", "#ffffff") if is_dark else ("#ffe4e6", "#e11d48", "#881337")),
            "slate": (("#1e293b", "#64748b", "#ffffff") if is_dark else ("#f1f5f9", "#64748b", "#0f172a")),
        }
        return palettes.get(color_name.lower(), palettes["amber"])


