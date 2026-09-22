import React, { useMemo } from 'react';
import { useSchedule } from '../context/ScheduleContext';
import { MapPin, User, Plus, Clock } from 'lucide-react';

const DAYS = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi"];

const TIME_SLOTS = [
  "08:40 - 09:30",
  "09:00 - 09:50",
  "10:00 - 10:50",
  "11:00 - 11:50",
  "12:00 - 12:50",
  "13:00 - 13:50",
  "14:00 - 14:50",
  "15:00 - 15:50",
  "16:00 - 16:50",
  "17:00 - 17:50",
  "18:00 - 18:50",
  "19:00 - 19:50",
  "20:00 - 20:50",
];

// Rich curated color palette for courses
const COURSE_PALETTES = [
  { bg: 'bg-amber-400/20 dark:bg-amber-400/15', border: 'border-amber-400/60 dark:border-amber-400/50', text: 'text-amber-950 dark:text-amber-300', tag: 'bg-amber-400 text-slate-950 font-bold' },
  { bg: 'bg-emerald-500/15 dark:bg-emerald-500/25', border: 'border-emerald-500/40 dark:border-emerald-400/50', text: 'text-emerald-900 dark:text-emerald-200', tag: 'bg-emerald-500 text-white' },
  { bg: 'bg-blue-500/15 dark:bg-blue-500/25', border: 'border-blue-500/40 dark:border-blue-400/50', text: 'text-blue-900 dark:text-blue-200', tag: 'bg-blue-500 text-white' },
  { bg: 'bg-purple-500/15 dark:bg-purple-500/25', border: 'border-purple-500/40 dark:border-purple-400/50', text: 'text-purple-900 dark:text-purple-200', tag: 'bg-purple-500 text-white' },
  { bg: 'bg-rose-500/15 dark:bg-rose-500/25', border: 'border-rose-500/40 dark:border-rose-400/50', text: 'text-rose-900 dark:text-rose-200', tag: 'bg-rose-500 text-white' },
  { bg: 'bg-cyan-500/15 dark:bg-cyan-500/25', border: 'border-cyan-500/40 dark:border-cyan-400/50', text: 'text-cyan-900 dark:text-cyan-200', tag: 'bg-cyan-500 text-white' },
  { bg: 'bg-teal-500/15 dark:bg-teal-500/25', border: 'border-teal-500/40 dark:border-teal-400/50', text: 'text-teal-900 dark:text-teal-200', tag: 'bg-teal-500 text-white' },
  { bg: 'bg-orange-500/15 dark:bg-orange-500/25', border: 'border-orange-500/40 dark:border-orange-400/50', text: 'text-orange-900 dark:text-orange-200', tag: 'bg-orange-500 text-white' },
];

const CUSTOM_BLOCK_COLORS = {
  amber: 'bg-amber-100 dark:bg-amber-950/60 border-amber-300 dark:border-amber-800 text-amber-900 dark:text-amber-200',
  blue: 'bg-blue-100 dark:bg-blue-950/60 border-blue-300 dark:border-blue-800 text-blue-900 dark:text-blue-200',
  emerald: 'bg-emerald-100 dark:bg-emerald-950/60 border-emerald-300 dark:border-emerald-800 text-emerald-900 dark:text-emerald-200',
  rose: 'bg-rose-100 dark:bg-rose-950/60 border-rose-300 dark:border-rose-800 text-rose-900 dark:text-rose-200',
  slate: 'bg-slate-100 dark:bg-slate-800 border-slate-300 dark:border-slate-700 text-slate-900 dark:text-slate-200',
};

export const Timetable = () => {
  const {
    currentCombination,
    profile,
    openModal,
    basket,
    classroomMap
  } = useSchedule();

  // Assign distinct color palette to each course code
  const courseColorMap = useMemo(() => {
    const map = {};
    if (!currentCombination || !currentCombination.sections) return map;

    currentCombination.sections.forEach((sec, idx) => {
      if (!map[sec.course_code]) {
        const palette = COURSE_PALETTES[Object.keys(map).length % COURSE_PALETTES.length];
        map[sec.course_code] = palette;
      }
    });
    return map;
  }, [currentCombination]);

  // Map slots for quick lookup: { "Pazartesi:09:00 - 09:50": [ { sec, slot } ] }
  const slotMap = useMemo(() => {
    const map = {};
    if (!currentCombination || !currentCombination.sections) return map;

    currentCombination.sections.forEach(sec => {
      sec.slots.forEach(slot => {
        // Match slot time with our TIME_SLOTS
        const matchedTimeSlot = matchTimeSlot(slot.time_slot);
        if (matchedTimeSlot) {
          const key = `${slot.day}:${matchedTimeSlot}`;
          if (!map[key]) map[key] = [];
          map[key].push({ sec, slot });
        }
      });
    });
    return map;
  }, [currentCombination]);

  // Helper function to match scraped time format like "09:00/09:20" or "09:00-09:50" to TIME_SLOTS
  function matchTimeSlot(rawSlot) {
    if (!rawSlot) return null;
    const cleaned = rawSlot.replace('/', '-').trim();
    const parts = cleaned.split('-');
    const startHour = parts[0]?.trim();

    if (!startHour) return null;

    // Exact or substring match
    for (const ts of TIME_SLOTS) {
      if (ts.startsWith(startHour.slice(0, 2))) {
        return ts;
      }
    }
    return null;
  }

  const customBlocks = profile.custom_schedule_blocks || {};

  return (
    <div className="flex-1 overflow-auto bg-[#fafaf9] dark:bg-darkbg p-4">

      {/* Timetable Export Container */}
      <div
        id="timetable-export-area"
        className="min-w-[850px] bg-white dark:bg-darkbg-surface rounded-2xl border border-slate-200/80 dark:border-darkbg-border shadow-sm overflow-hidden"
      >

        {/* Schedule Header / Day Columns */}
        <div className="grid grid-cols-[90px_repeat(6,minmax(0,1fr))] border-b border-slate-200/80 dark:border-darkbg-border bg-white dark:bg-darkbg-card/90">

          {/* Top-Left Corner Cell */}
          <div className="p-3 text-center border-r border-slate-200/80 dark:border-darkbg-border flex items-center justify-center">
            <Clock className="w-4 h-4 text-amber-500 dark:text-amber-400" />
          </div>

          {/* Days */}
          {DAYS.map((day) => (
            <div
              key={day}
              className="py-3 px-2 text-center font-extrabold text-xs uppercase tracking-wider text-slate-900 dark:text-amber-400 border-r last:border-r-0 border-slate-200/80 dark:border-darkbg-border truncate"
            >
              {day}
            </div>
          ))}
        </div>

        {/* Schedule Grid Rows */}
        <div className="divide-y divide-slate-200/70 dark:divide-darkbg-border/70">
          {TIME_SLOTS.map((timeSlot) => (
            <div
              key={timeSlot}
              className="grid grid-cols-[90px_repeat(6,minmax(0,1fr))] min-h-[78px]"
            >

              {/* Time Label Column */}
              <div className="p-2 text-center border-r border-slate-200 dark:border-darkbg-border flex flex-col items-center justify-center bg-slate-50/40 dark:bg-darkbg-card/40 shrink-0">
                <span className="text-[11px] font-bold text-slate-600 dark:text-slate-400 leading-tight">
                  {timeSlot.split('-')[0].trim()}
                </span>
                <span className="text-[10px] text-slate-400 dark:text-slate-500">
                  {timeSlot.split('-')[1].trim()}
                </span>
              </div>

              {/* Day Cells */}
              {DAYS.map((day) => {
                const key = `${day}:${timeSlot}`;
                const entries = slotMap[key] || [];
                const customBlock = customBlocks[key];

                const hasCourse = entries.length > 0;
                const hasCustom = !!customBlock;

                return (
                  <div
                    key={day}
                    className="min-w-0 p-1 border-r last:border-r-0 border-slate-200/70 dark:border-darkbg-border/70 relative group transition-colors hover:bg-slate-50/50 dark:hover:bg-darkbg-card/30 flex flex-col overflow-hidden"
                  >
                    {/* Course Card */}
                    {hasCourse && (
                      <div className="flex flex-col gap-1 h-full min-w-0 overflow-hidden">
                        {entries.map(({ sec, slot }, i) => {
                          const palette = courseColorMap[sec.course_code] || COURSE_PALETTES[0];
                          const cData = classroomMap?.[sec.course_code]?.[String(sec.section_no)];
                          const slotKey = `${slot.day}:${slot.time_slot}`;
                          const basketCourse = basket?.[sec.course_code];
                          const rawSections = basketCourse?.sections;
                          const basketSec = Array.isArray(rawSections)
                            ? rawSections.find(s => String(s.section_no) === String(sec.section_no))
                            : rawSections?.[String(sec.section_no)];
                          const rawSlots = basketSec?.slots;
                          const basketSlot = Array.isArray(rawSlots)
                            ? rawSlots.find(s => s.day === slot.day && (s.time_slot === slot.time_slot || matchTimeSlot(s.time_slot) === matchTimeSlot(slot.time_slot)))
                            : null;

                          const classroom = slot.classroom
                            || sec.classroom
                            || cData?.slots?.[slotKey]
                            || cData?.classroom
                            || basketSlot?.classroom
                            || basketSec?.classroom
                            || "";

                          return (
                            <div
                              key={i}
                              onClick={() => openModal('courseDetail', sec.course_code)}
                              className={`flex-1 p-2 rounded-xl border ${palette.border} ${palette.bg} ${palette.text} cursor-pointer transition-all hover:scale-[1.01] hover:shadow-xs active:scale-99 flex flex-col justify-between min-w-0 overflow-hidden`}
                              title={`${sec.course_code} (Şb.${sec.section_no}) - ${sec.instructor}${classroom ? ` [${classroom}]` : ''}`}
                            >
                              <div className="min-w-0 overflow-hidden">
                                <div className="flex items-center justify-between gap-1 min-w-0">
                                  <span className="font-extrabold text-xs tracking-tight truncate">
                                    {sec.course_code}
                                  </span>
                                  <span className={`text-[10px] font-bold px-1.5 py-0.2 rounded-full shrink-0 ${palette.tag}`}>
                                    Şb.{sec.section_no}
                                  </span>
                                </div>

                                <div className="flex items-center gap-1 mt-1 text-[10px] opacity-85 min-w-0">
                                  <User className="w-3 h-3 shrink-0" />
                                  <span className="truncate block font-medium" title={sec.instructor}>
                                    {sec.instructor}
                                  </span>
                                </div>

                                {classroom && (
                                  <div className="flex items-center gap-1 mt-0.5 text-[10px] font-semibold opacity-90 min-w-0">
                                    <MapPin className="w-3 h-3 shrink-0" />
                                    <span className="truncate block" title={classroom}>
                                      {classroom}
                                    </span>
                                  </div>
                                )}
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    )}

                    {/* Custom Block Card */}
                    {hasCustom && !hasCourse && (
                      <div
                        onClick={() => openModal('customBlock', { day, time_slot: timeSlot, block: customBlock })}
                        className={`h-full p-2 rounded-xl border cursor-pointer transition-all hover:scale-[1.01] flex flex-col justify-between min-w-0 overflow-hidden ${CUSTOM_BLOCK_COLORS[customBlock.color || 'amber'] || CUSTOM_BLOCK_COLORS.amber
                          }`}
                        title={`${customBlock.title}${customBlock.note ? ` - ${customBlock.note}` : ''}`}
                      >
                        <div className="min-w-0 overflow-hidden">
                          <span className="font-bold text-xs truncate block">
                            {customBlock.title}
                          </span>
                          {customBlock.note && (
                            <p className="text-[10px] opacity-80 truncate block mt-0.5" title={customBlock.note}>
                              {customBlock.note}
                            </p>
                          )}
                        </div>
                        <span className="text-[9px] uppercase font-semibold opacity-70 shrink-0">
                          Özel Etkinlik
                        </span>
                      </div>
                    )}

                    {/* Empty Cell: Click to Add Custom Block */}
                    {!hasCourse && !hasCustom && (
                      <button
                        onClick={() => openModal('customBlock', { day, time_slot: timeSlot })}
                        className="w-full h-full rounded-lg border border-dashed border-transparent group-hover:border-amber-300 dark:group-hover:border-amber-800/60 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-all text-slate-400 hover:text-amber-600 dark:hover:text-amber-400"
                        title={`${day} ${timeSlot} için Özel Blok Ekle`}
                      >
                        <Plus className="w-4 h-4" />
                      </button>
                    )}

                  </div>
                );
              })}

            </div>
          ))}
        </div>

      </div>

    </div>
  );
};
