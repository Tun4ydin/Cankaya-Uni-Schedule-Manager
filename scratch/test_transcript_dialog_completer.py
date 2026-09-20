import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from data_manager import DataManager
from gui.transcript_dialog import TranscriptDialog
from gui.qt_compat import QApplication

def main():
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)

    dm = DataManager()
    # Add dummy course to test
    dm.courses["CENG111"] = type("Course", (), {"code": "CENG111", "name": "Introduction to Programming"})()
    dm.courses["MATH157"] = type("Course", (), {"code": "MATH157", "name": "Calculus I"})()

    dialog = TranscriptDialog(dm)
    print("TranscriptDialog initialized successfully.")

    # Test completer exists
    completer = dialog.txt_manual_code.completer()
    assert completer is not None, "QCompleter should be attached to txt_manual_code"
    model = completer.model()
    print(f"Completer model row count: {model.rowCount()}")
    assert model.rowCount() > 0, "Completer should contain courses"

    # Test adding course via code + name string
    dialog.txt_manual_code.setText("CENG111 - Introduction to Programming")
    dialog.add_manual_course()
    assert "CENG111" in dialog.detected_data["passed_courses"], "CENG111 should be added"
    print("Test 1: Adding course with completer format PASSED.")

    # Test adding course via lowercase raw code with space
    dialog.txt_manual_code.setText("math 157")
    dialog.add_manual_course()
    assert "MATH157" in dialog.detected_data["passed_courses"], "MATH157 should be added"
    print("Test 2: Adding course with raw string PASSED.")

    # Test table rows
    assert dialog.table_courses.rowCount() == 2, f"Table should have 2 rows, got {dialog.table_courses.rowCount()}"
    assert dialog.table_courses.columnCount() == 4, f"Table should have 4 columns, got {dialog.table_courses.columnCount()}"
    print("Test 3: Table rows and columns PASSED.")

    # Verify PDF tab is gone
    assert not hasattr(dialog, "btn_tab_file"), "btn_tab_file should not exist"
    assert not hasattr(dialog, "container_file"), "container_file should not exist"
    print("Test 4: PDF tab removal verified.")

    print("\nALL TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    main()
