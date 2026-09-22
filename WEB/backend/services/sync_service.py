import threading
import time
import sys
from typing import Optional, List
from config import ROOT_DIR
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from curriculum_fetcher import CurriculumFetcher
from scraper import CankayaScraper
from prerequisite_manager import PrerequisiteManager
from services.data_service import data_service

class SyncService:
    def __init__(self):
        self._lock = threading.Lock()
        self._is_running = False
        self._is_cancelled = False
        self._progress = 0
        self._stage = ""
        self._message = "Hazır"
        self._error = None
        self._course_count = 0
        self._dept_count = 0
        self._thread: Optional[threading.Thread] = None

    def get_status(self):
        with self._lock:
            return {
                "running": self._is_running,
                "progress": self._progress,
                "stage": self._stage,
                "message": self._message,
                "error": self._error,
                "course_count": self._course_count,
                "dept_count": self._dept_count
            }

    def cancel(self):
        with self._lock:
            if self._is_running:
                self._is_cancelled = True
                self._message = "İptal ediliyor..."
                return {"status": "cancelling"}
            return {"status": "not_running"}

    def start_sync(self, sync_courses: bool = True, sync_curricula: bool = True, dept_list: Optional[List[str]] = None):
        with self._lock:
            if self._is_running:
                return {"status": "already_running", "message": "Zaten bir veri çekme işlemi devam ediyor."}

            self._is_running = True
            self._is_cancelled = False
            self._progress = 0
            self._stage = "Başlatılıyor"
            self._message = "Veri çekme işlemi başlatılıyor..."
            self._error = None

            self._thread = threading.Thread(
                target=self._run_sync,
                args=(sync_courses, sync_curricula, dept_list),
                daemon=True
            )
            self._thread.start()
            return {"status": "started", "message": "Veri çekme işlemi arka planda başlatıldı."}

    def _run_sync(self, sync_courses: bool, sync_curricula: bool, dept_list: Optional[List[str]]):
        def cancel_check():
            with self._lock:
                return self._is_cancelled

        try:
            # Stage 1: Bilgi Paketi Curricula & Prerequisites
            if sync_curricula:
                with self._lock:
                    self._stage = "Müfredat & Ön Koşullar"
                    self._progress = 5
                    self._message = "Bilgi Paketi müfredat ve seçmeli havuzları güncelleniyor..."

                curr_fetcher = CurriculumFetcher()

                def curr_callback(cur, total, msg):
                    pct = int(5 + (cur / max(1, total)) * (40 if sync_courses else 90))
                    with self._lock:
                        self._progress = pct
                        self._message = msg

                c_ok, c_depts, c_details = curr_fetcher.fetch_all_curricula(
                    progress_callback=curr_callback,
                    dept_list=dept_list,
                    cancel_check=cancel_check
                )

                if cancel_check():
                    with self._lock:
                        self._is_running = False
                        self._message = "İşlem iptal edildi."
                    return

                if c_ok:
                    data_service.dm.reload_official_curricula()
                    PrerequisiteManager.reload_official_prerequisites()

            # Stage 2: Cankaya Scraper (Offered courses & schedules)
            if sync_courses:
                with self._lock:
                    self._stage = "Açılan Dersler"
                    self._progress = 50 if sync_curricula else 5
                    self._message = "cankaya.edu.tr üzerinden açılan dersler çekiliyor..."

                scraper = CankayaScraper()

                def scrape_callback(cur, total, msg):
                    base_pct = 50 if sync_curricula else 5
                    scale = 45 if sync_curricula else 90
                    pct = int(base_pct + (cur / max(1, total)) * scale)
                    with self._lock:
                        self._progress = pct
                        self._message = msg

                raw_entries = scraper.fetch_all_schedules(
                    progress_callback=scrape_callback,
                    dept_list=dept_list,
                    cancel_check=cancel_check
                )

                if cancel_check():
                    with self._lock:
                        self._is_running = False
                        self._message = "İşlem iptal edildi."
                    return

                if not raw_entries:
                    with self._lock:
                        self._is_running = False
                        self._error = "Açılan dersler sayfasından veri alınamadı."
                        self._message = "Açılan dersler sayfasından veri alınamadı."
                    return

                with self._lock:
                    self._progress = 98
                    self._message = "Veriler işleniyor ve önbelleğe kaydediliyor..."

                data_service.dm.process_raw_entries(raw_entries)
                data_service.dm.load_from_cache()

            with self._lock:
                self._progress = 100
                self._stage = "Tamamlandı"
                self._course_count = len(data_service.dm.courses)
                self._dept_count = len(data_service.dm.departments)
                self._message = f"Başarıyla tamamlandı! {self._course_count} ders ve {self._dept_count} bölüm güncellendi."
                self._is_running = False

        except Exception as e:
            with self._lock:
                self._is_running = False
                self._error = str(e)
                self._message = f"Hata oluştu: {e}"

sync_service = SyncService()
