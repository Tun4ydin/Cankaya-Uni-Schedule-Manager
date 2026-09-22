import React, { useState, useEffect, useRef } from 'react';
import { useSchedule } from '../context/ScheduleContext';
import { api } from '../services/api';
import { 
  X, 
  RefreshCw, 
  CloudDownload, 
  CheckCircle2, 
  AlertCircle, 
  StopCircle, 
  Layers, 
  BookOpen, 
  CalendarCheck
} from 'lucide-react';

export const SyncModal = () => {
  const { modalState, closeModal, departments, refreshProfile } = useSchedule();

  const [syncCourses, setSyncCourses] = useState(true);
  const [syncCurricula, setSyncCurricula] = useState(true);
  const [selectedDept, setSelectedDept] = useState('ALL');

  const [status, setStatus] = useState({
    running: false,
    progress: 0,
    stage: '',
    message: 'Hazır',
    error: null,
    course_count: 0,
    dept_count: 0
  });

  const pollIntervalRef = useRef(null);

  const isModalOpen = modalState.type === 'sync';

  // Check initial status on open
  useEffect(() => {
    if (!isModalOpen) return;

    api.getSyncStatus().then(setStatus).catch(console.error);

    return () => {
      if (pollIntervalRef.current) {
        clearInterval(pollIntervalRef.current);
      }
    };
  }, [isModalOpen]);

  // Polling when running
  useEffect(() => {
    if (status.running) {
      if (!pollIntervalRef.current) {
        pollIntervalRef.current = setInterval(async () => {
          try {
            const currentStatus = await api.getSyncStatus();
            setStatus(currentStatus);
            if (!currentStatus.running) {
              clearInterval(pollIntervalRef.current);
              pollIntervalRef.current = null;
              refreshProfile();
            }
          } catch (err) {
            console.error(err);
          }
        }, 800);
      }
    } else {
      if (pollIntervalRef.current) {
        clearInterval(pollIntervalRef.current);
        pollIntervalRef.current = null;
      }
    }
  }, [status.running, refreshProfile]);

  if (!isModalOpen) return null;

  const handleStartSync = async () => {
    try {
      const deptList = selectedDept === 'ALL' ? null : [selectedDept];
      await api.startSync({
        syncCourses,
        syncCurricula,
        deptList
      });
      const initial = await api.getSyncStatus();
      setStatus(initial);
    } catch (err) {
      console.error(err);
      setStatus(prev => ({ ...prev, error: 'İşlem başlatılamadı.' }));
    }
  };

  const handleCancelSync = async () => {
    try {
      await api.cancelSync();
      const current = await api.getSyncStatus();
      setStatus(current);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-slate-900/50 backdrop-blur-xs flex items-center justify-center p-4">
      <div className="bg-white dark:bg-darkbg-surface rounded-2xl border border-slate-200 dark:border-darkbg-border max-w-lg w-full shadow-2xl overflow-hidden animate-fadeIn">
        
        {/* Header */}
        <div className="p-4 border-b border-slate-200 dark:border-darkbg-border flex items-center justify-between bg-slate-50/60 dark:bg-darkbg-card/60">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-amber-400/20 dark:bg-amber-400/15 flex items-center justify-center text-amber-800 dark:text-amber-400">
              <CloudDownload className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-sm font-bold text-slate-900 dark:text-white">
                Çankaya Verilerini Çek & Güncelle
              </h2>
              <p className="text-[11px] text-slate-500 dark:text-slate-400">
                Açılan dersleri ve resmi müfredatları okul sitelerinden çeker
              </p>
            </div>
          </div>

          <button
            onClick={closeModal}
            disabled={status.running}
            className="p-1.5 rounded-lg text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-darkbg-border disabled:opacity-40"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Content */}
        <div className="p-5 space-y-4">
          
          {/* Options (Disabled when running) */}
          {!status.running && (
            <div className="space-y-3">
              <div className="space-y-2">
                <label className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400 block">
                  Çekilecek Veri Türleri
                </label>

                {/* Option 1: Offered courses */}
                <label className="flex items-start gap-3 p-3 rounded-xl border border-slate-200 dark:border-darkbg-border bg-slate-50/50 dark:bg-darkbg-card/40 cursor-pointer hover:bg-slate-50 dark:hover:bg-darkbg-card transition-colors">
                  <input
                    type="checkbox"
                    checked={syncCourses}
                    onChange={(e) => setSyncCourses(e.target.checked)}
                    className="mt-0.5 w-4 h-4 rounded text-amber-500 focus:ring-amber-400 dark:focus:ring-amber-400 cursor-pointer"
                  />
                  <div className="text-xs">
                    <p className="font-bold text-slate-800 dark:text-slate-200 flex items-center gap-1.5">
                      <CalendarCheck className="w-3.5 h-3.5 text-amber-600 dark:text-amber-400" />
                      <span>Açılan Dersler, Şubeler & Derslikler</span>
                    </p>
                    <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-0.5">
                      Öğrenci işleri haftalık program sayfasından (cankaya.edu.tr/ogrenci_isleri) tüm şube saatlerini ve derslikleri çeker.
                    </p>
                  </div>
                </label>

                {/* Option 2: Curricula */}
                <label className="flex items-start gap-3 p-3 rounded-xl border border-slate-200 dark:border-darkbg-border bg-slate-50/50 dark:bg-darkbg-card/40 cursor-pointer hover:bg-slate-50 dark:hover:bg-darkbg-card transition-colors">
                  <input
                    type="checkbox"
                    checked={syncCurricula}
                    onChange={(e) => setSyncCurricula(e.target.checked)}
                    className="mt-0.5 w-4 h-4 rounded text-amber-500 focus:ring-amber-400 dark:focus:ring-amber-400 cursor-pointer"
                  />
                  <div className="text-xs">
                    <p className="font-bold text-slate-800 dark:text-slate-200 flex items-center gap-1.5">
                      <BookOpen className="w-3.5 h-3.5 text-amber-600 dark:text-amber-400" />
                      <span>Bölüm Müfredatları</span>
                    </p>
                    <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-0.5">
                      Bölüm web sitelerinden zorunlu ve seçmeli ders listelerini çeker.
                    </p>
                  </div>
                </label>
              </div>

              {/* Department Scope */}
              <div>
                <label className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400 mb-1 block">
                  Kapsam
                </label>
                <select
                  value={selectedDept}
                  onChange={(e) => setSelectedDept(e.target.value)}
                  className="w-full text-xs py-2 px-2.5 rounded-lg bg-slate-50 dark:bg-darkbg-card border border-slate-200 dark:border-darkbg-border text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-1 focus:ring-cankaya-navy dark:focus:ring-cankaya-gold cursor-pointer"
                >
                  <option value="ALL">Tüm Üniversite (Tüm Bölümler)</option>
                  {departments.map(d => (
                    <option key={d.code} value={d.code}>
                      Yalnızca {d.code} - {d.name.split('(')[0]}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          )}

          {/* Progress / Status Display */}
          {(status.running || status.progress > 0) && (
            <div className="p-4 rounded-xl bg-slate-50 dark:bg-darkbg-card border border-slate-200 dark:border-darkbg-border space-y-3">
              
              <div className="flex items-center justify-between text-xs">
                <span className="font-bold text-slate-700 dark:text-slate-200 flex items-center gap-2">
                  {status.running ? (
                    <RefreshCw className="w-4 h-4 text-amber-600 dark:text-amber-400 animate-spin" />
                  ) : status.error ? (
                    <AlertCircle className="w-4 h-4 text-red-500" />
                  ) : (
                    <CheckCircle2 className="w-4 h-4 text-emerald-500" />
                  )}
                  <span>{status.stage || 'Durum'}</span>
                </span>
                <span className="font-extrabold text-amber-700 dark:text-amber-400">
                  %{status.progress}
                </span>
              </div>

              {/* Progress Bar */}
              <div className="w-full h-2.5 rounded-full bg-slate-200 dark:bg-slate-700 overflow-hidden">
                <div 
                  className={`h-full rounded-full transition-all duration-300 ${
                    status.error 
                      ? 'bg-red-500' 
                      : status.progress === 100 
                        ? 'bg-emerald-500' 
                        : 'bg-gradient-to-r from-amber-400 to-amber-500 dark:from-amber-400 dark:to-yellow-300'
                  }`}
                  style={{ width: `${status.progress}%` }}
                />
              </div>

              <p className="text-[11px] text-slate-600 dark:text-slate-300 font-mono truncate">
                {status.message}
              </p>

            </div>
          )}

          {/* Action Buttons */}
          <div className="pt-2 border-t border-slate-200 dark:border-darkbg-border flex items-center justify-between gap-2">
            {status.running ? (
              <button
                type="button"
                onClick={handleCancelSync}
                className="w-full py-2.5 px-4 rounded-xl text-xs font-bold text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-950/40 hover:bg-red-100 dark:hover:bg-red-900/60 border border-red-200 dark:border-red-800 transition-all flex items-center justify-center gap-1.5"
              >
                <StopCircle className="w-4 h-4" />
                <span>İptal Et</span>
              </button>
            ) : (
              <>
                <button
                  type="button"
                  onClick={closeModal}
                  className="px-4 py-2 rounded-xl text-xs font-medium text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-darkbg-card transition-colors"
                >
                  Kapat
                </button>

                <button
                  type="button"
                  disabled={!syncCourses && !syncCurricula}
                  onClick={handleStartSync}
                  className="px-5 py-2.5 rounded-xl text-xs font-extrabold text-slate-950 bg-amber-400 hover:bg-amber-500 dark:bg-amber-400 dark:hover:bg-amber-300 dark:text-slate-950 hover:opacity-95 transition-all shadow-md shadow-amber-400/25 dark:shadow-glow-yellow flex items-center gap-1.5 disabled:opacity-50"
                >
                  <CloudDownload className="w-4 h-4" />
                  <span>Çekmeye Başla</span>
                </button>
              </>
            )}
          </div>

        </div>

      </div>
    </div>
  );
};
