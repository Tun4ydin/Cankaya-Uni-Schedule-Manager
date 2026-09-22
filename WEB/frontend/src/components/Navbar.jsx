import React from 'react';
import { useSchedule } from '../context/ScheduleContext';
import {
  GraduationCap,
  FileText,
  Sun,
  Moon,
  BookOpen,
  Layers,
  CloudDownload
} from 'lucide-react';

export const Navbar = () => {
  const {
    theme,
    toggleTheme,
    profile,
    departments,
    updateDepartments,
    openModal
  } = useSchedule();

  const handlePrimaryChange = (e) => {
    updateDepartments(e.target.value, profile.secondary_dept, profile.secondary_type);
  };

  const handleSecondaryTypeChange = (e) => {
    const secType = e.target.value;
    const secDept = secType === 'YOK' ? 'YOK' : profile.secondary_dept === 'YOK' ? 'SENG' : profile.secondary_dept;
    updateDepartments(profile.primary_dept, secDept, secType);
  };

  const handleSecondaryDeptChange = (e) => {
    updateDepartments(profile.primary_dept, e.target.value, profile.secondary_type);
  };

  return (
    <header className="sticky top-0 z-30 border-b border-slate-200/80 dark:border-darkbg-border bg-white/95 dark:bg-darkbg-surface/95 backdrop-blur-md transition-colors">
      <div className="max-w-[1700px] mx-auto px-4 sm:px-6 py-2.5">
        <div className="flex flex-wrap items-center justify-between gap-4">

          {/* Brand Logo & Title */}
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-amber-400 to-amber-500 dark:from-amber-400 dark:to-yellow-500 flex items-center justify-center text-slate-950 shadow-md shadow-amber-400/20 border border-amber-300/40 dark:border-amber-400/30">
              <GraduationCap className="w-6 h-6 text-slate-950" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-extrabold text-lg tracking-tight text-slate-900 dark:text-white">
                  ÇANKAYA
                </span>
                <span className="text-xs font-bold px-2 py-0.5 rounded-full bg-amber-400/20 text-amber-800 dark:text-amber-300 border border-amber-400/40">
                  SCHEDULE
                </span>
              </div>
              <p className="text-xs text-slate-500 dark:text-slate-400 font-medium">
                Ders Programı & Müfredat Yöneticisi
              </p>
            </div>
          </div>

          {/* Department Selectors (Major + Minor/Double Major) */}
          <div className="flex flex-wrap items-center gap-3">
            {/* Primary Major */}
            <div className="flex items-center gap-2 bg-slate-50 dark:bg-darkbg-card px-3 py-1.5 rounded-lg border border-slate-200 dark:border-darkbg-border">
              <BookOpen className="w-4 h-4 text-amber-500 dark:text-amber-400 shrink-0" />
              <div className="flex flex-col">
                <label className="text-[10px] font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">
                  Ana Bölüm
                </label>
                <select
                  value={profile.primary_dept || 'CENG'}
                  onChange={handlePrimaryChange}
                  className="bg-transparent text-xs font-semibold text-slate-800 dark:text-slate-200 focus:outline-none cursor-pointer pr-2"
                >
                  {departments.map(d => (
                    <option key={d.code} value={d.code} className="dark:bg-darkbg-surface dark:text-white">
                      {d.code} - {d.name.split('(')[0]}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            {/* Secondary Program Type */}
            <div className="flex items-center gap-2 bg-slate-50 dark:bg-darkbg-card px-3 py-1.5 rounded-lg border border-slate-200 dark:border-darkbg-border">
              <Layers className="w-4 h-4 text-purple-600 dark:text-purple-400 shrink-0" />
              <div className="flex flex-col">
                <label className="text-[10px] font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">
                  İkinci Program
                </label>
                <select
                  value={profile.secondary_type || 'YOK'}
                  onChange={handleSecondaryTypeChange}
                  className="bg-transparent text-xs font-semibold text-slate-800 dark:text-slate-200 focus:outline-none cursor-pointer pr-2"
                >
                  <option value="YOK" className="dark:bg-darkbg-surface dark:text-white">Yok</option>
                  <option value="CAP" className="dark:bg-darkbg-surface dark:text-white">Çift Anadal (ÇAP)</option>
                  <option value="YANDAL" className="dark:bg-darkbg-surface dark:text-white">Yandal</option>
                </select>
              </div>
            </div>

            {/* Secondary Department (if enabled) */}
            {profile.secondary_type && profile.secondary_type !== 'YOK' && (
              <div className="flex items-center gap-2 bg-purple-50 dark:bg-purple-950/40 px-3 py-1.5 rounded-lg border border-purple-200 dark:border-purple-800/60 animate-fadeIn">
                <div className="flex flex-col">
                  <label className="text-[10px] font-bold uppercase tracking-wider text-purple-700 dark:text-purple-300">
                    {profile.secondary_type === 'CAP' ? 'ÇAP Bölümü' : 'Yandal Bölümü'}
                  </label>
                  <select
                    value={profile.secondary_dept || ''}
                    onChange={handleSecondaryDeptChange}
                    className="bg-transparent text-xs font-semibold text-purple-900 dark:text-purple-200 focus:outline-none cursor-pointer pr-2"
                  >
                    {departments.filter(d => d.code !== profile.primary_dept).map(d => (
                      <option key={d.code} value={d.code} className="dark:bg-darkbg-surface dark:text-white">
                        {d.code} - {d.name.split('(')[0]}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
            )}
          </div>

          {/* Action Buttons: Transcript, Curriculum, Theme */}
          <div className="flex items-center gap-2">
            <button
              onClick={() => openModal('sync')}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-lg bg-amber-400/15 text-amber-800 dark:text-amber-400 border border-amber-400/40 hover:bg-amber-400/25 transition-all shadow-xs active:scale-95"
              title="Açılan Dersleri ve Müfredatları Çankaya Sitelerinden Çek"
            >
              <CloudDownload className="w-4 h-4 text-amber-600 dark:text-amber-400" />
              <span>Verileri Çek</span>
            </button>

            <button
              onClick={() => openModal('transcript')}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg bg-white dark:bg-darkbg-card text-slate-700 dark:text-slate-200 border border-slate-200 dark:border-darkbg-border hover:border-amber-400/60 dark:hover:border-amber-400/50 hover:text-amber-700 dark:hover:text-amber-400 transition-all shadow-xs active:scale-95"
              title="Transkript Yükle ve Notları İşle"
            >
              <FileText className="w-4 h-4 text-amber-600 dark:text-amber-400" />
              <span>Transkript</span>
            </button>

            <button
              onClick={() => openModal('curriculum')}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg bg-white dark:bg-darkbg-card text-slate-700 dark:text-slate-200 border border-slate-200 dark:border-darkbg-border hover:border-amber-400/60 dark:hover:border-amber-400/50 hover:text-amber-700 dark:hover:text-amber-400 transition-all shadow-xs active:scale-95"
              title="Müfredat Tamamlama Durumu"
            >
              <GraduationCap className="w-4 h-4 text-amber-600 dark:text-amber-400" />
              <span>Müfredat</span>
            </button>

            <button
              onClick={toggleTheme}
              className="p-2 rounded-lg text-slate-600 dark:text-slate-300 hover:bg-amber-50 dark:hover:bg-darkbg-card border border-transparent hover:border-amber-200 dark:hover:border-darkbg-border transition-all active:scale-95"
              title={theme === 'light' ? 'Karanlık Temaya Geç' : 'Aydınlık Temaya Geç'}
            >
              {theme === 'light' ? (
                <Moon className="w-4 h-4 text-amber-600" />
              ) : (
                <Sun className="w-4 h-4 text-amber-400" />
              )}
            </button>
          </div>

        </div>
      </div>
    </header>
  );
};
