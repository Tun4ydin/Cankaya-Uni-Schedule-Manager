import React, { useState, useEffect, useMemo } from 'react';
import { useSchedule } from '../context/ScheduleContext';
import { api } from '../services/api';
import { 
  Search, 
  Plus, 
  Check, 
  Info, 
  X, 
  Filter, 
  Sparkles, 
  AlertTriangle, 
  CheckCircle2, 
  GraduationCap, 
  AlertCircle 
} from 'lucide-react';

export const CourseSearchPanel = () => {
  const { 
    profile, 
    departments, 
    basket, 
    addCourseToBasket, 
    removeCourseFromBasket,
    openModal 
  } = useSchedule();

  const [query, setQuery] = useState('');
  const [selectedDept, setSelectedDept] = useState('');
  const [selectedType, setSelectedType] = useState('TÜMÜ');
  const [selectedStatus, setSelectedStatus] = useState('ALL'); // 'ALL' | 'AVAILABLE' | 'PASSED' | 'MISSING_PREREQ'
  const [courses, setCourses] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [pendingCourse, setPendingCourse] = useState(null); // { course, isPassed, hasMissingPrereq }

  // Debounced search
  useEffect(() => {
    const timer = setTimeout(async () => {
      setIsLoading(true);
      try {
        const results = await api.searchCourses({
          query,
          dept: selectedDept,
          courseType: selectedType,
          primaryDept: profile.primary_dept,
          secondaryDept: profile.secondary_dept,
          secondaryType: profile.secondary_type
        });
        setCourses(results);
      } catch (err) {
        console.error('Course search error:', err);
      } finally {
        setIsLoading(false);
      }
    }, 200);

    return () => clearTimeout(timer);
  }, [query, selectedDept, selectedType, profile.primary_dept, profile.secondary_dept, profile.secondary_type]);

  const typePills = [
    { id: 'TÜMÜ', label: 'Tümü' },
    { id: 'ZORUNLU', label: '📌 Zorunlu' },
    ...(profile.secondary_type === 'CAP' ? [{ id: 'ZORUNLU_CAP', label: '🟣 ÇAP' }] : []),
    ...(profile.secondary_type === 'YANDAL' ? [{ id: 'ZORUNLU_YANDAL', label: '🔵 Yandal' }] : []),
    { id: 'SECMELI', label: '🔹 Seçmeli' }
  ];

  const statusPills = [
    { id: 'ALL', label: 'Tüm Durumlar' },
    { id: 'AVAILABLE', label: '✅ Alınabilir' },
    { id: 'PASSED', label: '🎓 Geçilenler' },
    { id: 'MISSING_PREREQ', label: '⚠️ Ön Koşul Eksik' }
  ];

  const filteredCourses = useMemo(() => {
    return courses.filter(c => {
      if (selectedStatus === 'PASSED') {
        return !!c.passed_info?.is_passed;
      }
      if (selectedStatus === 'MISSING_PREREQ') {
        return c.prerequisites && !c.prerequisites.can_take;
      }
      if (selectedStatus === 'AVAILABLE') {
        return (!c.prerequisites || c.prerequisites.can_take) && !c.passed_info?.is_passed;
      }
      return true;
    });
  }, [courses, selectedStatus]);

  const getTypeBadgeStyle = (type) => {
    switch (type) {
      case 'ZORUNLU':
        return 'bg-amber-100 text-amber-800 dark:bg-amber-950/60 dark:text-amber-300 border-amber-200 dark:border-amber-800';
      case 'ZORUNLU_CAP':
        return 'bg-purple-100 text-purple-800 dark:bg-purple-950/60 dark:text-purple-300 border-purple-200 dark:border-purple-800';
      case 'ZORUNLU_YANDAL':
        return 'bg-blue-100 text-blue-800 dark:bg-blue-950/60 dark:text-blue-300 border-blue-200 dark:border-blue-800';
      case 'TEKNIK_SECMELI':
        return 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950/60 dark:text-emerald-300 border-emerald-200 dark:border-emerald-800';
      default:
        return 'bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300 border-slate-200 dark:border-slate-700';
    }
  };

  const handleAddClick = (course) => {
    if (basket[course.code]) {
      removeCourseFromBasket(course.code);
      return;
    }

    const isPassed = !!course.passed_info?.is_passed;
    const hasMissingPrereq = course.prerequisites && !course.prerequisites.can_take;

    if (isPassed || hasMissingPrereq) {
      setPendingCourse({
        course,
        isPassed,
        hasMissingPrereq
      });
    } else {
      addCourseToBasket(course);
    }
  };

  const confirmAddPendingCourse = () => {
    if (pendingCourse?.course) {
      addCourseToBasket(pendingCourse.course);
    }
    setPendingCourse(null);
  };

  return (
    <div className="flex flex-col h-full bg-white dark:bg-darkbg-surface border-r border-slate-200/80 dark:border-darkbg-border">
      
      {/* Search & Filters Header */}
      <div className="p-3.5 border-b border-slate-200/80 dark:border-darkbg-border space-y-2.5">
        
        {/* Search Input */}
        <div className="relative">
          <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            placeholder="Ders kodu veya hoca adı ara... (örn. CENG111)"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="w-full pl-9 pr-8 py-2 text-xs rounded-lg bg-slate-50 dark:bg-darkbg-card border border-slate-200 dark:border-darkbg-border focus:outline-none focus:ring-2 focus:ring-amber-400 dark:focus:ring-amber-400 text-slate-900 dark:text-slate-100 placeholder:text-slate-400"
          />
          {query && (
            <button
              onClick={() => setQuery('')}
              className="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          )}
        </div>

        {/* Department Filter & Total Count */}
        <div className="flex items-center gap-2">
          <div className="relative flex-1">
            <select
              value={selectedDept}
              onChange={(e) => setSelectedDept(e.target.value)}
              className="w-full text-xs py-1.5 px-2.5 rounded-lg bg-slate-50 dark:bg-darkbg-card border border-slate-200 dark:border-darkbg-border text-slate-700 dark:text-slate-300 focus:outline-none focus:ring-1 focus:ring-amber-400 dark:focus:ring-amber-400 cursor-pointer"
            >
              <option value="">Tüm Bölümler</option>
              {departments.map(d => (
                <option key={d.code} value={d.code}>
                  {d.code} - {d.name.split('(')[0]}
                </option>
              ))}
            </select>
          </div>
          <span className="text-[11px] font-medium text-slate-500 dark:text-slate-400 shrink-0 px-2 py-1 bg-slate-100 dark:bg-darkbg-card rounded-md">
            {filteredCourses.length} / {courses.length} Ders
          </span>
        </div>

        {/* Type Filter Pills */}
        <div className="flex flex-wrap gap-1.5 pt-0.5">
          {typePills.map(pill => (
            <button
              key={pill.id}
              onClick={() => setSelectedType(pill.id)}
              className={`text-[11px] font-medium px-2 py-1 rounded-md transition-all ${
                selectedType === pill.id
                  ? 'bg-amber-400 text-slate-950 font-bold dark:bg-amber-400 dark:text-black shadow-xs'
                  : 'bg-slate-100 text-slate-600 hover:bg-slate-200 dark:bg-darkbg-card dark:text-slate-300 dark:hover:bg-darkbg-border'
              }`}
            >
              {pill.label}
            </button>
          ))}
        </div>

        {/* Prerequisite & Taken Status Filter Pills */}
        <div className="flex flex-wrap gap-1 pt-1 border-t border-slate-100 dark:border-darkbg-border/60">
          {statusPills.map(pill => (
            <button
              key={pill.id}
              onClick={() => setSelectedStatus(pill.id)}
              className={`text-[10px] font-semibold px-2 py-0.5 rounded-full transition-all ${
                selectedStatus === pill.id
                  ? 'bg-slate-900 text-amber-400 dark:bg-amber-400 dark:text-black font-bold shadow-2xs'
                  : 'bg-slate-50 text-slate-600 hover:bg-slate-200 dark:bg-darkbg-surface dark:text-slate-400 dark:hover:bg-darkbg-card border border-slate-200/80 dark:border-darkbg-border'
              }`}
            >
              {pill.label}
            </button>
          ))}
        </div>

      </div>

      {/* Courses List */}
      <div className="flex-1 overflow-y-auto p-3 space-y-2">
        {isLoading ? (
          <div className="flex flex-col items-center justify-center h-48 text-slate-400 gap-2">
            <div className="w-5 h-5 border-2 border-amber-500 dark:border-amber-400 border-t-transparent rounded-full animate-spin" />
            <span className="text-xs">Dersler yükleniyor...</span>
          </div>
        ) : filteredCourses.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-48 text-center p-4">
            <Sparkles className="w-8 h-8 text-slate-300 dark:text-slate-600 mb-2" />
            <p className="text-xs font-medium text-slate-600 dark:text-slate-300">Ders bulunamadı</p>
            <p className="text-[11px] text-slate-400 mt-1">Arama veya durum filtrelerinizi değiştirmeyi deneyebilirsiniz.</p>
          </div>
        ) : (
          filteredCourses.map((course) => {
            const isSelected = !!basket[course.code];
            const isPassed = !!course.passed_info?.is_passed;
            const hasPrereqs = !!course.prerequisites?.has_prereqs;
            const canTake = course.prerequisites?.can_take ?? true;
            const missingPrereqs = course.prerequisites?.missing_prereqs || [];

            return (
              <div
                key={course.code}
                className={`p-3 rounded-xl border transition-all ${
                  isSelected
                    ? 'border-cankaya-gold dark:border-cankaya-gold/80 bg-cankaya-gold/5 dark:bg-cankaya-gold/10 shadow-xs'
                    : 'border-slate-200/90 dark:border-darkbg-border bg-white dark:bg-darkbg-card hover:border-slate-300 dark:hover:border-slate-600'
                }`}
              >
                <div className="flex items-start justify-between gap-2">
                  <div className="space-y-1">
                    <div className="flex items-center gap-1.5 flex-wrap">
                      <span className="font-bold text-sm text-slate-900 dark:text-slate-100">
                        {course.code}
                      </span>
                      <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full border ${getTypeBadgeStyle(course.course_type)}`}>
                        {course.type_label}
                      </span>

                      {/* Passed Course Badge */}
                      {isPassed && (
                        <span className="text-[10px] font-bold px-2 py-0.5 rounded-full border bg-emerald-100 text-emerald-800 dark:bg-emerald-950/70 dark:text-emerald-300 border-emerald-300 dark:border-emerald-700 flex items-center gap-1 shadow-2xs">
                          <Check className="w-3 h-3 text-emerald-600 dark:text-emerald-400" />
                          <span>Geçildi ({course.passed_info.grade || 'Başarılı'})</span>
                        </span>
                      )}

                      {/* Prerequisite Badge */}
                      {hasPrereqs ? (
                        canTake ? (
                          <span 
                            title={`Kural: ${course.prerequisites.rule_description}`}
                            className="text-[10px] font-semibold px-2 py-0.5 rounded-full border bg-teal-50 text-teal-700 dark:bg-teal-950/60 dark:text-teal-300 border-teal-200 dark:border-teal-800 flex items-center gap-1 cursor-help"
                          >
                            <CheckCircle2 className="w-3 h-3 text-teal-600 dark:text-teal-400" />
                            <span>Ön Koşul Sağlandı</span>
                          </span>
                        ) : (
                          <span 
                            title={`Kural: ${course.prerequisites.rule_description} | Eksik: ${missingPrereqs.join(', ')}`}
                            className="text-[10px] font-bold px-2 py-0.5 rounded-full border bg-rose-100 text-rose-800 dark:bg-rose-950/70 dark:text-rose-300 border-rose-300 dark:border-rose-700 flex items-center gap-1 cursor-help"
                          >
                            <AlertTriangle className="w-3 h-3 text-rose-600 dark:text-rose-400 shrink-0" />
                            <span className="truncate max-w-[170px]">Ön Koşul Eksik: {missingPrereqs.join(', ')}</span>
                          </span>
                        )
                      ) : (
                        <span className="text-[10px] font-medium px-1.5 py-0.5 rounded-md bg-slate-100 text-slate-500 dark:bg-darkbg-card dark:text-slate-400 border border-slate-200 dark:border-darkbg-border">
                          Ön Koşulsuz
                        </span>
                      )}
                    </div>

                    <div className="flex items-center gap-2 text-[11px] text-slate-500 dark:text-slate-400">
                      <span>{course.credit} Kredi</span>
                      <span>•</span>
                      <span>{course.ects} AKTS</span>
                      <span>•</span>
                      <span>{course.sections_count} Şube</span>
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="flex items-center gap-1 shrink-0">
                    <button
                      onClick={() => openModal('courseDetail', course.code)}
                      className="p-1.5 rounded-lg text-slate-400 hover:text-amber-600 dark:hover:text-amber-400 hover:bg-slate-100 dark:hover:bg-darkbg-surface transition-colors"
                      title="Ders Detayları ve İzlence"
                    >
                      <Info className="w-4 h-4" />
                    </button>

                    <button
                      onClick={() => handleAddClick(course)}
                      className={`px-2.5 py-1.5 rounded-lg text-xs font-medium flex items-center gap-1 transition-all active:scale-95 ${
                        isSelected
                          ? 'bg-emerald-600 text-white hover:bg-emerald-700 shadow-xs'
                          : 'bg-amber-400 hover:bg-amber-500 text-slate-950 font-bold dark:bg-amber-400 dark:hover:bg-amber-300 dark:text-slate-950 shadow-xs'
                      }`}
                    >
                      {isSelected ? (
                        <>
                          <Check className="w-3.5 h-3.5" />
                          <span>Eklendi</span>
                        </>
                      ) : (
                        <>
                          <Plus className="w-3.5 h-3.5" />
                          <span>Ekle</span>
                        </>
                      )}
                    </button>
                  </div>
                </div>

                {/* Section Instructors Preview */}
                {course.sections && course.sections.length > 0 && (
                  <div className="mt-2 pt-2 border-t border-slate-100 dark:border-darkbg-border/60 text-[11px] text-slate-500 dark:text-slate-400">
                    <span className="font-medium text-slate-600 dark:text-slate-300">Şubeler: </span>
                    {course.sections.slice(0, 3).map((sec, i) => (
                      <span key={sec.section_no}>
                        {i > 0 && ', '}
                        Şb.{sec.section_no} ({sec.instructor.split(' ')[0]})
                      </span>
                    ))}
                    {course.sections.length > 3 && ` +${course.sections.length - 3} daha`}
                  </div>
                )}

              </div>
            );
          })
        )}
      </div>

      {/* Course Add Warning / Confirmation Modal */}
      {pendingCourse && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white dark:bg-darkbg-surface rounded-2xl border border-slate-200 dark:border-darkbg-border max-w-md w-full p-5 shadow-2xl space-y-4 animate-fadeIn">
            
            {/* Modal Header */}
            <div className="flex items-start justify-between">
              <div className="flex items-center gap-2.5">
                <div className={`w-9 h-9 rounded-xl flex items-center justify-center ${
                  pendingCourse.hasMissingPrereq
                    ? 'bg-rose-100 dark:bg-rose-950/60 text-rose-600 dark:text-rose-400'
                    : 'bg-amber-100 dark:bg-amber-950/60 text-amber-600 dark:text-amber-400'
                }`}>
                  {pendingCourse.hasMissingPrereq ? (
                    <AlertTriangle className="w-5 h-5" />
                  ) : (
                    <GraduationCap className="w-5 h-5" />
                  )}
                </div>
                <div>
                  <h3 className="text-sm font-bold text-slate-900 dark:text-slate-100">
                    {pendingCourse.hasMissingPrereq && pendingCourse.isPassed
                      ? 'Ders Ekleme Uyarısı (Ön Koşul & Geçilmiş Ders)'
                      : pendingCourse.hasMissingPrereq
                      ? 'Ön Koşul Uyarısı'
                      : 'Not Yükseltme / Geçilmiş Ders'}
                  </h3>
                  <p className="text-xs text-slate-500 dark:text-slate-400">
                    {pendingCourse.course.code}
                  </p>
                </div>
              </div>

              <button
                onClick={() => setPendingCourse(null)}
                className="p-1.5 rounded-lg text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-darkbg-card"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* Warning Details */}
            <div className="space-y-2.5 text-xs">
              {/* Missing Prerequisite Warning */}
              {pendingCourse.hasMissingPrereq && (
                <div className="p-3 rounded-xl bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-800/60 text-rose-900 dark:text-rose-200 space-y-1">
                  <div className="flex items-center gap-1.5 font-bold text-rose-700 dark:text-rose-300">
                    <AlertCircle className="w-4 h-4 shrink-0" />
                    <span>Ön Koşul Şartı Sağlanmamış</span>
                  </div>
                  <p className="text-[11px] leading-relaxed">
                    Bu dersin resmi ön koşulu transkriptinizde eksik görünmektedir:
                  </p>
                  <p className="font-semibold text-rose-800 dark:text-rose-200 pl-2 border-l-2 border-rose-400">
                    Eksik: {pendingCourse.course.prerequisites?.missing_prereqs?.join(', ')}
                  </p>
                  <p className="text-[10px] opacity-80 pt-0.5">
                    Kural: {pendingCourse.course.prerequisites?.rule_description}
                  </p>
                  <p className="text-[10px] text-rose-700 dark:text-rose-300 italic pt-1">
                    * Resmi kayıt esnasında bu dersi seçmenize sistem veya danışmanınız izin vermeyebilir.
                  </p>
                </div>
              )}

              {/* Already Passed Warning */}
              {pendingCourse.isPassed && (
                <div className="p-3 rounded-xl bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-800/60 text-emerald-900 dark:text-emerald-200 space-y-1">
                  <div className="flex items-center gap-1.5 font-bold text-emerald-700 dark:text-emerald-300">
                    <CheckCircle2 className="w-4 h-4 shrink-0" />
                    <span>Ders Daha Önce Verildi</span>
                  </div>
                  <p className="text-[11px] leading-relaxed">
                    Bu dersi daha önce <span className="font-bold text-emerald-800 dark:text-emerald-200">{pendingCourse.course.passed_info?.grade}</span> harf notu ile geçtiniz.
                  </p>
                  <p className="text-[10px] opacity-85">
                    Not yükseltmek amacıyla bu dersi tekrar almak istiyorsanız taslak programınıza ekleyebilirsiniz.
                  </p>
                </div>
              )}
            </div>

            {/* Action Buttons */}
            <div className="flex items-center justify-end gap-2 pt-2 border-t border-slate-100 dark:border-darkbg-border">
              <button
                onClick={() => setPendingCourse(null)}
                className="px-3.5 py-2 text-xs font-medium rounded-xl text-slate-600 hover:text-slate-800 dark:text-slate-300 dark:hover:text-white bg-slate-100 hover:bg-slate-200 dark:bg-darkbg-card dark:hover:bg-darkbg-border transition-all"
              >
                Vazgeç
              </button>
              
              <button
                onClick={confirmAddPendingCourse}
                className="px-4 py-2 text-xs font-bold rounded-xl text-white bg-cankaya-navy hover:bg-cankaya-navy-light dark:bg-cankaya-gold dark:text-slate-950 dark:hover:bg-cankaya-gold-light transition-all shadow-xs"
              >
                {pendingCourse.isPassed && !pendingCourse.hasMissingPrereq
                  ? 'Not Yükseltmek İçin Ekle'
                  : 'Yine de Ekle'}
              </button>
            </div>

          </div>
        </div>
      )}

    </div>
  );
};

