import React from 'react';
import { useSchedule } from '../context/ScheduleContext';
import { 
  ChevronLeft, 
  ChevronRight, 
  Filter, 
  Download, 
  Share2, 
  Clock, 
  CalendarDays,
  Sparkles
} from 'lucide-react';
import html2canvas from 'html2canvas';

export const CombinationBar = () => {
  const { 
    combinations, 
    currentCombinationIndex, 
    setCurrentCombinationIndex, 
    currentCombination,
    preferences, 
    togglePreference,
    generateSchedule,
    isLoadingCombinations
  } = useSchedule();

  const handlePrev = () => {
    if (currentCombinationIndex > 0) {
      setCurrentCombinationIndex(currentCombinationIndex - 1);
    }
  };

  const handleNext = () => {
    if (currentCombinationIndex < combinations.length - 1) {
      setCurrentCombinationIndex(currentCombinationIndex + 1);
    }
  };

  const exportAsPng = async () => {
    const timetableEl = document.getElementById('timetable-export-area');
    if (!timetableEl) return;

    try {
      const canvas = await html2canvas(timetableEl, {
        scale: 2,
        backgroundColor: '#ffffff',
        useCORS: true
      });
      const dataUrl = canvas.toDataURL('image/png');
      const link = document.createElement('a');
      link.download = `cankaya_ders_programi_kombinasyon_${currentCombinationIndex + 1}.png`;
      link.href = dataUrl;
      link.click();
    } catch (err) {
      console.error('Failed to export PNG:', err);
    }
  };

  const exportAsJson = () => {
    if (!currentCombination) return;
    const jsonStr = JSON.stringify(currentCombination, null, 2);
    const blob = new Blob([jsonStr], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.download = `cankaya_program_${currentCombinationIndex + 1}.json`;
    link.href = url;
    link.click();
  };

  return (
    <div className="p-3 bg-white dark:bg-darkbg-surface border-b border-slate-200/80 dark:border-darkbg-border flex flex-wrap items-center justify-between gap-3 shadow-2xs">
      
      {/* Combinations Navigation */}
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-1 bg-slate-100 dark:bg-darkbg-card p-1 rounded-xl border border-slate-200 dark:border-darkbg-border">
          <button
            onClick={handlePrev}
            disabled={currentCombinationIndex <= 0 || combinations.length === 0}
            className="p-1.5 rounded-lg text-slate-700 dark:text-slate-200 hover:bg-white dark:hover:bg-darkbg-surface disabled:opacity-30 disabled:cursor-not-allowed transition-all active:scale-95"
            title="Önceki Kombinasyon"
          >
            <ChevronLeft className="w-4 h-4" />
          </button>

          <span className="text-xs font-bold px-3 text-amber-700 dark:text-amber-400 min-w-[130px] text-center">
            {combinations.length > 0 ? (
              <>Kombinasyon {currentCombinationIndex + 1} / {combinations.length}</>
            ) : (
              <span className="text-slate-400 font-normal">Kombinasyon Yok</span>
            )}
          </span>

          <button
            onClick={handleNext}
            disabled={currentCombinationIndex >= combinations.length - 1 || combinations.length === 0}
            className="p-1.5 rounded-lg text-slate-700 dark:text-slate-200 hover:bg-white dark:hover:bg-darkbg-surface disabled:opacity-30 disabled:cursor-not-allowed transition-all active:scale-95"
            title="Sonraki Kombinasyon"
          >
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>

        {/* Current Combination Metrics */}
        {currentCombination && (
          <div className="hidden sm:flex items-center gap-2 text-xs">
            <span className="px-2 py-1 rounded-md bg-amber-50 dark:bg-amber-950/40 text-amber-800 dark:text-amber-300 font-medium border border-amber-200 dark:border-amber-900">
              {currentCombination.total_credits} Kredi
            </span>
            <span className="px-2 py-1 rounded-md bg-slate-100 dark:bg-darkbg-card text-slate-800 dark:text-slate-200 font-medium border border-slate-200 dark:border-darkbg-border">
              {currentCombination.total_ects} AKTS
            </span>
            <span className="px-2 py-1 rounded-md bg-emerald-50 dark:bg-emerald-950/40 text-emerald-700 dark:text-emerald-300 font-medium border border-emerald-200 dark:border-emerald-900 flex items-center gap-1">
              <Clock className="w-3 h-3" />
              {currentCombination.total_hours} Saat / Hafta
            </span>
            <span className="px-2 py-1 rounded-md bg-amber-50 dark:bg-amber-950/40 text-amber-700 dark:text-amber-300 font-medium border border-amber-200 dark:border-amber-900 flex items-center gap-1">
              <CalendarDays className="w-3 h-3" />
              {currentCombination.days_count} Gün
            </span>
          </div>
        )}
      </div>

      {/* Preferences & Export Actions */}
      <div className="flex flex-wrap items-center gap-2">
        
        {/* Preference Filters */}
        <div className="flex items-center gap-1.5 bg-slate-50 dark:bg-darkbg-card px-2 py-1 rounded-lg border border-slate-200 dark:border-darkbg-border">
          <Filter className="w-3.5 h-3.5 text-slate-400" />
          
          <button
            onClick={() => { togglePreference('free_friday'); generateSchedule(); }}
            className={`text-xs font-medium px-2 py-1 rounded-md transition-all ${
              preferences.free_friday
                ? 'bg-amber-400 text-slate-950 font-bold dark:bg-amber-400 dark:text-black shadow-xs'
                : 'text-slate-600 dark:text-slate-400 hover:bg-slate-200 dark:hover:bg-darkbg-border'
            }`}
          >
            Cuma Boş
          </button>

          <button
            onClick={() => { togglePreference('free_monday'); generateSchedule(); }}
            className={`text-xs font-medium px-2 py-1 rounded-md transition-all ${
              preferences.free_monday
                ? 'bg-amber-400 text-slate-950 font-bold dark:bg-amber-400 dark:text-black shadow-xs'
                : 'text-slate-600 dark:text-slate-400 hover:bg-slate-200 dark:hover:bg-darkbg-border'
            }`}
          >
            Pzt Boş
          </button>

          <button
            onClick={() => { togglePreference('no_morning'); generateSchedule(); }}
            className={`text-xs font-medium px-2 py-1 rounded-md transition-all ${
              preferences.no_morning
                ? 'bg-amber-400 text-slate-950 font-bold dark:bg-amber-400 dark:text-black shadow-xs'
                : 'text-slate-600 dark:text-slate-400 hover:bg-slate-200 dark:hover:bg-darkbg-border'
            }`}
          >
            Sabah Dersi Yok
          </button>
        </div>

        {/* Export Buttons */}
        {currentCombination && (
          <div className="flex items-center gap-1">
            <button
              onClick={exportAsPng}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium bg-white dark:bg-darkbg-card text-slate-700 dark:text-slate-200 border border-slate-200 dark:border-darkbg-border hover:bg-amber-50 dark:hover:bg-darkbg-surface hover:text-amber-700 dark:hover:text-amber-400 shadow-xs transition-all active:scale-95"
              title="Ders Programını PNG Olarak İndir"
            >
              <Download className="w-3.5 h-3.5 text-amber-600 dark:text-amber-400" />
              <span>PNG İndir</span>
            </button>

            <button
              onClick={exportAsJson}
              className="inline-flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-xs font-medium bg-white dark:bg-darkbg-card text-slate-700 dark:text-slate-200 border border-slate-200 dark:border-darkbg-border hover:bg-slate-50 dark:hover:bg-darkbg-surface shadow-xs transition-all active:scale-95"
              title="JSON Olarak Dışa Aktar"
            >
              <Share2 className="w-3.5 h-3.5 text-slate-500" />
            </button>
          </div>
        )}

      </div>

    </div>
  );
};
