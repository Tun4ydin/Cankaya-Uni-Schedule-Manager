import React, { useState, useEffect } from 'react';
import { useSchedule } from '../context/ScheduleContext';
import { api } from '../services/api';
import { 
  X, 
  GraduationCap, 
  CheckCircle2, 
  Clock, 
  Plus, 
  Check, 
  BookOpen,
  Award
} from 'lucide-react';

export const CurriculumModal = () => {
  const { modalState, closeModal, profile, basket, addCourseToBasket } = useSchedule();
  const [progress, setProgress] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (modalState.type !== 'curriculum') return;
    setIsLoading(true);
    api.getCurriculumProgress(profile.primary_dept)
      .then(setProgress)
      .catch(console.error)
      .finally(() => setIsLoading(false));
  }, [modalState.type, profile.primary_dept]);

  if (modalState.type !== 'curriculum') return null;

  const compulsoryPct = progress && progress.compulsory_total > 0
    ? Math.round((progress.compulsory_passed / progress.compulsory_total) * 100)
    : 0;

  return (
    <div className="fixed inset-0 z-50 bg-slate-900/50 backdrop-blur-xs flex items-center justify-center p-4">
      <div className="bg-white dark:bg-darkbg-surface rounded-2xl border border-slate-200 dark:border-darkbg-border max-w-2xl w-full max-h-[90vh] flex flex-col shadow-2xl overflow-hidden animate-fadeIn">
        
        {/* Header */}
        <div className="p-4 border-b border-slate-200 dark:border-darkbg-border flex items-center justify-between bg-slate-50/60 dark:bg-darkbg-card/60">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-amber-400/20 dark:bg-amber-400/15 flex items-center justify-center text-amber-800 dark:text-amber-400">
              <GraduationCap className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-sm font-bold text-slate-900 dark:text-white">
                Müfredat Tamamlama Durumu
              </h2>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                {progress?.program_name || profile.primary_dept}
              </p>
            </div>
          </div>

          <button
            onClick={closeModal}
            className="p-1.5 rounded-lg text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-darkbg-border"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="flex-1 overflow-y-auto p-5 space-y-5">
          {isLoading ? (
            <div className="flex flex-col items-center justify-center h-48 text-slate-400 gap-2">
              <div className="w-6 h-6 border-2 border-cankaya-navy dark:border-cankaya-gold border-t-transparent rounded-full animate-spin" />
              <span className="text-xs">Müfredat yükleniyor...</span>
            </div>
          ) : progress ? (
            <>
              {/* Overall Compulsory Progress Bar */}
              <div className="p-4 rounded-xl bg-slate-50 dark:bg-darkbg-card border border-slate-200 dark:border-darkbg-border space-y-2">
                <div className="flex items-center justify-between text-xs">
                  <span className="font-bold text-slate-700 dark:text-slate-200 flex items-center gap-1.5">
                    <BookOpen className="w-4 h-4 text-amber-600 dark:text-amber-400" />
                    <span>Zorunlu Dersler İlerlemesi</span>
                  </span>
                  <span className="font-extrabold text-amber-700 dark:text-amber-400">
                    {progress.compulsory_passed} / {progress.compulsory_total} Ders (%{compulsoryPct})
                  </span>
                </div>

                <div className="w-full h-3 rounded-full bg-slate-200 dark:bg-slate-700 overflow-hidden">
                  <div 
                    className="h-full rounded-full bg-gradient-to-r from-amber-400 to-amber-500 dark:from-amber-400 dark:to-yellow-300 transition-all duration-500"
                    style={{ width: `${compulsoryPct}%` }}
                  />
                </div>
              </div>

              {/* Electives Grid */}
              <div className="grid grid-cols-2 gap-3">
                <div className="p-3.5 rounded-xl bg-slate-50 dark:bg-darkbg-card border border-slate-200 dark:border-darkbg-border text-center space-y-1">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
                    Teknik Seçmeli
                  </span>
                  <p className="text-lg font-extrabold text-emerald-600 dark:text-emerald-400">
                    {progress.tech_slots_passed} / {progress.tech_slots_total}
                  </p>
                  <p className="text-[11px] text-slate-500 dark:text-slate-400">
                    Kalan: {progress.tech_slots_remaining} Slot
                  </p>
                </div>

                <div className="p-3.5 rounded-xl bg-slate-50 dark:bg-darkbg-card border border-slate-200 dark:border-darkbg-border text-center space-y-1">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
                    Sosyal / Serbest Seçmeli
                  </span>
                  <p className="text-lg font-extrabold text-blue-600 dark:text-blue-400">
                    {progress.social_slots_passed} / {progress.social_slots_total}
                  </p>
                  <p className="text-[11px] text-slate-500 dark:text-slate-400">
                    Kalan: {progress.social_slots_remaining} Slot
                  </p>
                </div>
              </div>

              {/* Remaining Compulsory Courses List */}
              <div className="space-y-2">
                <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700 dark:text-slate-300 flex items-center justify-between">
                  <span>Alınması Gereken Zorunlu Dersler ({progress.compulsory_remaining_count})</span>
                </h3>

                <div className="divide-y divide-slate-100 dark:divide-darkbg-border border border-slate-200 dark:border-darkbg-border rounded-xl overflow-hidden max-h-60 overflow-y-auto">
                  {progress.compulsory_remaining.map((c) => {
                    const code = c.code || c.norm_code;
                    const isSelected = !!basket[code];

                    return (
                      <div 
                        key={code}
                        className="p-2.5 bg-white dark:bg-darkbg-card flex items-center justify-between gap-2 text-xs hover:bg-slate-50 dark:hover:bg-darkbg-surface transition-colors"
                      >
                        <div>
                          <span className="font-bold text-slate-900 dark:text-white">
                            {code}
                          </span>
                          <span className="text-slate-500 dark:text-slate-400 text-[11px] ml-2 truncate">
                            {c.name || ''}
                          </span>
                        </div>

                        <button
                          onClick={() => {
                            if (!isSelected) {
                              addCourseToBasket({ code, name: c.name || code, credit: 3, ects: 5 });
                            }
                          }}
                          disabled={isSelected}
                          className={`px-2 py-1 rounded-md text-[11px] font-bold flex items-center gap-1 transition-all ${
                            isSelected
                              ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950/60 dark:text-emerald-300'
                              : 'bg-amber-400 hover:bg-amber-500 text-slate-950 dark:bg-amber-400 dark:hover:bg-amber-300 dark:text-slate-950 shadow-xs'
                          }`}
                        >
                          {isSelected ? (
                            <>
                              <Check className="w-3 h-3" />
                              <span>Sepette</span>
                            </>
                          ) : (
                            <>
                              <Plus className="w-3 h-3" />
                              <span>Sepete Ekle</span>
                            </>
                          )}
                        </button>
                      </div>
                    );
                  })}
                </div>
              </div>

            </>
          ) : null}
        </div>

      </div>
    </div>
  );
};
