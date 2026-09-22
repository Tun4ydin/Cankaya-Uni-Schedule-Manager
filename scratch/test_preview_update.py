import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from gui.qt_compat import QApplication
from gui.main_window import MainWindow

app = QApplication.instance() or QApplication(sys.argv)
window = MainWindow()
window.show()

search_panel = window.search_panel

# 1. User searches and adds CENG329
search_panel.txt_search.setText("CENG329")
search_panel.on_search_changed()
search_panel.list_results.setCurrentRow(0)
print("Adding CENG329 to basket...")
search_panel.btn_add.click()

print("Basket courses:", list(search_panel.basket_courses.keys()))
print("Timetable sections count:", len(window.timetable_widget.last_sections_list))
print("Combinations count:", len(window.current_combinations))
print("Status label:", window.combination_bar.lbl_status.text())
print("Credit label:", window.combination_bar.lbl_credit_summary.text())

# 2. User adds CENG383
search_panel.txt_search.setText("CENG383")
search_panel.on_search_changed()
search_panel.list_results.setCurrentRow(0)
print("\nAdding CENG383 to basket...")
search_panel.btn_add.click()

print("Basket courses:", list(search_panel.basket_courses.keys()))
print("Timetable sections count:", len(window.timetable_widget.last_sections_list))
print("Combinations count:", len(window.current_combinations))
print("Status label:", window.combination_bar.lbl_status.text())
print("Credit label:", window.combination_bar.lbl_credit_summary.text())

window.close()
