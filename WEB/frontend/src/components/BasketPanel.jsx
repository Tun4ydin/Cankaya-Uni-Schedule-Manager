import React, { useState, useMemo } from 'react';
import { useSchedule } from '../context/ScheduleContext';
import { 
  ShoppingBag, 
  Trash2, 
  Calendar, 
  Sparkles, 
  AlertCircle, 
  AlertTriangle, 
  Check, 
  X, 
  Users 
} from 'lucide-react';

export const BasketPanel = () => {
  const { 
    basket, 
    removeCourseFromBasket, 
    updateLockedSection, 
    updateAllowedInstructors,
    clearBasket, 
    generateSchedule, 
    isLoadingCombinations, 
    combinationError,
    openModal
  } = useSchedule();

  const [confirmRemoveAllInstructors, setConfirmRemoveAllInstructors] = useState(null);

  const selectedList = Object.values(basket);

  const totals = useMemo(() => {
    let credits = 0;
    let ects = 0;
    for (const c of selectedList) {
      credits += c.credit || 0;
      ects += c.ects || 0;
    }
    return { credits, ects };
  }, [selectedList]);

  const handleToggleInstructor = (courseCode, instructorName, currentAllowedList) => {
    const isCurrentlyAllowed = currentAllowedList.includes(instructorName);
    if (isCurrentlyAllowed) {
      if (currentAllowedList.length <= 1) {
        setConfirmRemoveAllInstructors({ courseCode, instructorName });
        return;
      }
      const next = currentAllowedList.filter(n => n !== instructorName);
      updateAllowedInstructors(courseCode, next);
    } else {
      const next = [...currentAllowedList, instructorName];
      updateAllowedInstructors(courseCode, next);
    }
  };

  return (
    <div className="flex flex-col h-full bg-white dark:bg-darkbg-surface border-r border-slate-200/80 dark:border-darkbg-border">
      
      {/* Header with Totals */}
      <div className="p-3.5 border-b border-slate-200/80 dark:border-darkbg-border bg-slate-50/70 dark:bg-darkbg-card/50">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <ShoppingBag className="w-4 h-4 text-amber-600 dark:text-amber-400" />
            <h2 className="text-xs font-bold uppercase tracking-wider text-slate-700 dark:text-slate-200">
              Seçilen Dersler
            </h2>
            <span className="text-[11px] font-extrabold px-2 py-0.5 rounded-full bg-amber-400 text-slate-950">
              {selectedList.length}
            </span>
          </div>

          {selectedList.length > 0 && (
            <button
              onClick={clearBasket}
              className="text-[11px] text-red-600 hover:text-red-700 dark:text-red-400 font-medium flex items-center gap-1 hover:underline"
            >
              <Trash2 className="w-3 h-3" />
              <span>Temizle</span>
            </button>
          )}
        </div>

        {/* Totals Banner */}
        <div className="grid grid-cols-2 gap-2 mt-3">
          <div className="bg-white dark:bg-darkbg-surface p-2 rounded-lg border border-slate-200 dark:border-darkbg-border text-center shadow-2xs">
            <span className="text-[10px] uppercase font-bold text-slate-400">Toplam Kredi</span>
            <p className="text-base font-extrabold text-amber-600 dark:text-amber-400">
              {totals.credits}
            </p>
          </div>
          <div className="bg-white dark:bg-darkbg-surface p-2 rounded-lg border border-slate-200 dark:border-darkbg-border text-center shadow-2xs">
            <span className="text-[10px] uppercase font-bold text-slate-400">Toplam AKTS</span>
            <p className="text-base font-extrabold text-slate-800 dark:text-slate-200">
              {totals.ects}
            </p>
          </div>
        </div>
      </div>

      {/* Selected Courses List */}
      <div className="flex-1 overflow-y-auto p-3 space-y-2.5">
        {selectedList.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-48 text-center p-4">
            <Calendar className="w-8 h-8 text-slate-300 dark:text-slate-600 mb-2" />
            <p className="text-xs font-semibold text-slate-600 dark:text-slate-300">Sepetiniz boş</p>
            <p className="text-[11px] text-slate-400 mt-1">
              Sol taraftaki arama panelinden dersleri sepetinize ekleyebilirsiniz.
            </p>
          </div>
        ) : (
          selectedList.map((item) => {
            // Compute unique instructors
            const instructorsMap = new Map();
            for (const sec of item.sections || []) {
              if (!sec.instructor) continue;
              if (!instructorsMap.has(sec.instructor)) {
                instructorsMap.set(sec.instructor, []);
              }
              instructorsMap.get(sec.instructor).push(sec.section_no);
            }
            const instructorsList = Array.from(instructorsMap.entries()).map(([name, sections]) => ({
              name,
              sections: sections.sort((a, b) => Number(a) - Number(b))
            }));

            const currentAllowed = item.allowedInstructors ?? instructorsList.map(i => i.name);
            const availableSections = (item.sections || []).filter(sec => currentAllowed.includes(sec.instructor));

            return (
              <div
                key={item.code}
                className="p-3 rounded-xl border border-slate-200 dark:border-darkbg-border bg-white dark:bg-darkbg-card shadow-2xs space-y-2.5"
              >
                <div className="flex items-start justify-between gap-2">
                  <div className="space-y-1">
                    <div className="flex items-center gap-1.5 flex-wrap">
                      <span className="font-bold text-sm text-cankaya-navy dark:text-slate-100">
                        {item.code}
                      </span>

                      {/* Passed Badge */}
                      {item.passed_info?.is_passed && (
                        <span className="text-[10px] font-bold px-1.5 py-0.5 rounded-md bg-emerald-100 text-emerald-800 dark:bg-emerald-950/70 dark:text-emerald-300 border border-emerald-300 dark:border-emerald-700 flex items-center gap-0.5">
                          <Check className="w-2.5 h-2.5" />
                          <span>Geçildi ({item.passed_info.grade})</span>
                        </span>
                      )}

                      {/* Missing Prereq Badge */}
                      {item.prerequisites && !item.prerequisites.can_take && (
                        <span 
                          title={`Eksik Ön Koşul: ${item.prerequisites.missing_prereqs?.join(', ')}`}
                          className="text-[10px] font-bold px-1.5 py-0.5 rounded-md bg-rose-100 text-rose-800 dark:bg-rose-950/70 dark:text-rose-300 border border-rose-300 dark:border-rose-700 flex items-center gap-0.5 cursor-help"
                        >
                          <AlertTriangle className="w-2.5 h-2.5 text-rose-600 dark:text-rose-400 shrink-0" />
                          <span>Ön Koşul Eksik</span>
                        </span>
                      )}
                    </div>

                    <div className="flex items-center gap-2 text-[11px] text-slate-500 dark:text-slate-400">
                      <span>{item.credit} Kredi</span>
                      <span>•</span>
                      <span>{item.ects} AKTS</span>
                      <span>•</span>
                      <span>{item.sections?.length || 0} Şube</span>
                    </div>
                  </div>

                  <button
                    onClick={() => removeCourseFromBasket(item.code)}
                    className="p-1 rounded-lg text-slate-400 hover:text-red-600 dark:hover:text-red-400 hover:bg-slate-100 dark:hover:bg-darkbg-surface transition-colors"
                    title="Sepetten Çıkar"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>

                {/* Instructor Selection Chips */}
                {instructorsList.length > 0 && (
                  <div className="pt-2 border-t border-slate-100 dark:border-darkbg-border/60 space-y-1.5">
                    <div className="flex items-center justify-between text-[11px]">
                      <span className="font-semibold text-slate-600 dark:text-slate-300 flex items-center gap-1">
                        <Users className="w-3 h-3 text-amber-600 dark:text-amber-400" />
                        <span>Öğretmen Tercihi:</span>
                      </span>
                      <span className="text-[10px] text-slate-400 font-medium">
                        {currentAllowed.length} / {instructorsList.length} Seçili
                      </span>
                    </div>

                    <div className="flex flex-wrap gap-1">
                      {instructorsList.map((inst) => {
                        const isAllowed = currentAllowed.includes(inst.name);
                        return (
                          <button
                            key={inst.name}
                            type="button"
                            onClick={() => handleToggleInstructor(item.code, inst.name, currentAllowed)}
                            className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-[10px] font-medium transition-all ${
                              isAllowed
                                ? 'bg-amber-400/20 text-amber-900 border border-amber-400/40 dark:bg-amber-400/15 dark:text-amber-300 dark:border-amber-400/40 shadow-2xs hover:opacity-80'
                                : 'bg-slate-100 text-slate-400 line-through border border-dashed border-slate-300 hover:bg-slate-200 dark:bg-darkbg-surface dark:text-slate-500 dark:border-darkbg-border dark:hover:bg-darkbg-card'
                            }`}
                            title={isAllowed ? 'Bu öğretmeni kaldırmak için tıklayın' : 'Bu öğretmeni tekrar seçmek için tıklayın'}
                          >
                            {isAllowed ? (
                              <Check className="w-2.5 h-2.5 text-emerald-600 dark:text-emerald-400 shrink-0" />
                            ) : (
                              <X className="w-2.5 h-2.5 text-slate-400 shrink-0" />
                            )}
                            <span className="truncate max-w-[130px]">{inst.name}</span>
                            <span className="opacity-70 text-[9px]">({inst.sections.map(s => `Şb.${s}`).join(',')})</span>
                          </button>
                        );
                      })}
                    </div>
                  </div>
                )}

                {/* Section Lock Selector */}
                <div className="flex items-center justify-between text-xs pt-2 border-t border-slate-100 dark:border-darkbg-border/60">
                  <span className="text-slate-500 dark:text-slate-400 text-[11px]">Şube Tercihi:</span>
                  <select
                    value={item.lockedSection || 'auto'}
                    onChange={(e) => updateLockedSection(item.code, e.target.value)}
                    className="text-xs font-semibold py-1 px-2 rounded-md bg-slate-50 dark:bg-darkbg-surface border border-slate-200 dark:border-darkbg-border text-slate-800 dark:text-slate-200 focus:outline-none focus:ring-1 focus:ring-amber-400 dark:focus:ring-amber-400 cursor-pointer max-w-[170px] truncate"
                  >
                    <option value="auto">Otomatik ({availableSections.length} Şube)</option>
                    {availableSections.map(sec => (
                      <option key={sec.section_no} value={sec.section_no}>
                        Şube {sec.section_no} ({sec.instructor.split(' ')[0]})
                      </option>
                    ))}
                  </select>
                </div>

              </div>
            );
          })
        )}
      </div>

      {/* Confirmation Modal when removing all instructors */}
      {confirmRemoveAllInstructors && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white dark:bg-darkbg-surface rounded-2xl border border-slate-200 dark:border-darkbg-border max-w-sm w-full p-5 shadow-2xl space-y-4 animate-fadeIn">
            <div className="flex items-start gap-3">
              <div className="w-9 h-9 rounded-xl bg-amber-100 dark:bg-amber-950/60 text-amber-600 dark:text-amber-400 flex items-center justify-center shrink-0">
                <AlertTriangle className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-sm font-bold text-slate-900 dark:text-slate-100">
                  Tüm Öğretmenler Kaldırılıyor
                </h3>
                <p className="text-xs text-slate-500 dark:text-slate-400 mt-1 leading-relaxed">
                  <span className="font-bold text-slate-700 dark:text-slate-200">{confirmRemoveAllInstructors.courseCode}</span> dersi için seçili öğretmen kalmadığında bu ders sepetinizden silinecektir. Devam etmek istiyor musunuz?
                </p>
              </div>
            </div>

            <div className="flex items-center justify-end gap-2 pt-2 border-t border-slate-100 dark:border-darkbg-border">
              <button
                onClick={() => setConfirmRemoveAllInstructors(null)}
                className="px-3.5 py-2 text-xs font-medium rounded-xl text-slate-600 hover:text-slate-800 dark:text-slate-300 dark:hover:text-white bg-slate-100 hover:bg-slate-200 dark:bg-darkbg-card dark:hover:bg-darkbg-border transition-all"
              >
                Vazgeç
              </button>
              <button
                onClick={() => {
                  removeCourseFromBasket(confirmRemoveAllInstructors.courseCode);
                  setConfirmRemoveAllInstructors(null);
                }}
                className="px-3.5 py-2 text-xs font-bold rounded-xl text-white bg-red-600 hover:bg-red-700 transition-all shadow-xs"
              >
                Dersi Sepetten Kaldır
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Error Alert if any */}
      {combinationError && (
        <div className="p-3 mx-3 mb-2 rounded-lg bg-red-50 dark:bg-red-950/40 border border-red-200 dark:border-red-800/60 text-red-700 dark:text-red-300 text-xs flex items-start gap-2">
          <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
          <div className="flex-1">
            <p className="font-semibold">Kombinasyon Hatası</p>
            <p className="text-[11px] mt-0.5">{combinationError}</p>
          </div>
        </div>
      )}

      {/* Action Footer */}
      <div className="p-3.5 border-t border-slate-200/80 dark:border-darkbg-border bg-slate-50/70 dark:bg-darkbg-card/50">
        <button
          onClick={generateSchedule}
          disabled={selectedList.length === 0 || isLoadingCombinations}
          className="w-full py-2.5 px-4 rounded-xl text-xs font-extrabold text-slate-950 bg-amber-400 hover:bg-amber-500 dark:bg-amber-400 dark:hover:bg-amber-300 dark:text-slate-950 hover:opacity-95 disabled:opacity-50 disabled:cursor-not-allowed shadow-md shadow-amber-400/25 dark:shadow-glow-yellow transition-all flex items-center justify-center gap-2 active:scale-98"
        >
          {isLoadingCombinations ? (
            <>
              <div className="w-4 h-4 border-2 border-slate-950 border-t-transparent rounded-full animate-spin" />
              <span>Hesaplanıyor...</span>
            </>
          ) : (
            <>
              <Sparkles className="w-4 h-4" />
              <span>Program Kombinasyonlarını Oluştur</span>
            </>
          )}
        </button>
      </div>

    </div>
  );
};
