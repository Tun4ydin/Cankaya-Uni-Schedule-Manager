import React, { useState, useEffect } from 'react';
import { useSchedule } from '../context/ScheduleContext';
import { api } from '../services/api';
import { 
  X, 
  ExternalLink, 
  CheckCircle2, 
  AlertCircle, 
  Clock, 
  User, 
  MapPin, 
  BookOpen,
  Calendar,
  GraduationCap
} from 'lucide-react';

export const CourseDetailModal = () => {
  const { modalState, closeModal, profile } = useSchedule();
  const courseCode = modalState.data;

  const [detail, setDetail] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (!courseCode) return;

    setIsLoading(true);
    api.getCourseDetail(courseCode, {
      primaryDept: profile.primary_dept,
      secondaryDept: profile.secondary_dept,
      secondaryType: profile.secondary_type
    })
      .then(setDetail)
      .catch(console.error)
      .finally(() => setIsLoading(false));
  }, [courseCode, profile.primary_dept, profile.secondary_dept, profile.secondary_type]);

  if (modalState.type !== 'courseDetail' || !courseCode) return null;

  return (
    <div className="fixed inset-0 z-50 bg-slate-900/50 backdrop-blur-xs flex items-center justify-center p-4">
      <div className="bg-white dark:bg-darkbg-surface rounded-2xl border border-slate-200 dark:border-darkbg-border max-w-2xl w-full max-h-[90vh] flex flex-col shadow-2xl overflow-hidden animate-fadeIn">
        
        {/* Modal Header */}
        <div className="p-4 border-b border-slate-200 dark:border-darkbg-border flex items-start justify-between bg-slate-50/60 dark:bg-darkbg-card/60">
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-lg font-extrabold text-slate-900 dark:text-white">
                {courseCode}
              </h2>
              {detail && (
                <span className="text-xs font-bold px-2 py-0.5 rounded-full bg-amber-400/20 text-amber-800 dark:text-amber-300 border border-amber-400/40">
                  {detail.type_label}
                </span>
              )}
            </div>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
              {detail?.name || 'Ders Bilgisi'}
            </p>
          </div>

          <button
            onClick={closeModal}
            className="p-1.5 rounded-lg text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-darkbg-border transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="flex-1 overflow-y-auto p-5 space-y-4">
          {isLoading ? (
            <div className="flex flex-col items-center justify-center h-48 text-slate-400 gap-2">
              <div className="w-6 h-6 border-2 border-cankaya-navy dark:border-cankaya-gold border-t-transparent rounded-full animate-spin" />
              <span className="text-xs">Ders ayrıntıları yükleniyor...</span>
            </div>
          ) : detail ? (
            <>
              {/* Quick Stats Grid */}
              <div className="grid grid-cols-3 gap-3">
                <div className="p-2.5 rounded-xl bg-slate-50 dark:bg-darkbg-card border border-slate-200 dark:border-darkbg-border text-center">
                  <span className="text-[10px] font-bold uppercase text-slate-400">Kredi</span>
                  <p className="text-base font-extrabold text-amber-600 dark:text-amber-400">
                    {detail.credit} Kredi
                  </p>
                </div>

                <div className="p-2.5 rounded-xl bg-slate-50 dark:bg-darkbg-card border border-slate-200 dark:border-darkbg-border text-center">
                  <span className="text-[10px] font-bold uppercase text-slate-400">AKTS</span>
                  <p className="text-base font-bold text-blue-600 dark:text-blue-400">
                    {detail.ects} AKTS
                  </p>
                </div>

                <div className="p-2.5 rounded-xl bg-slate-50 dark:bg-darkbg-card border border-slate-200 dark:border-darkbg-border text-center">
                  <span className="text-[10px] font-bold uppercase text-slate-400">Sınıf Düzeyi</span>
                  <p className="text-base font-bold text-slate-700 dark:text-slate-300">
                    {detail.level}. Sınıf
                  </p>
                </div>
              </div>

              {/* Passed Course Info Card */}
              {detail.passed_info?.is_passed && (
                <div className="p-3.5 rounded-xl border bg-emerald-50 dark:bg-emerald-950/40 border-emerald-200 dark:border-emerald-800 text-emerald-900 dark:text-emerald-200 flex items-start gap-3">
                  <GraduationCap className="w-5 h-5 text-emerald-600 dark:text-emerald-400 shrink-0 mt-0.5" />
                  <div className="text-xs space-y-1">
                    <p className="font-bold flex items-center gap-2">
                      <span>Bu Dersi Daha Önce Başarıyla Verdiniz</span>
                      <span className="px-2 py-0.5 rounded-md bg-emerald-200 dark:bg-emerald-800 text-emerald-900 dark:text-emerald-100 font-extrabold text-[11px]">
                        Harf Notu: {detail.passed_info.grade}
                      </span>
                    </p>
                    <p className="text-[11px] opacity-90">
                      Bu ders transkriptinizde kayıtlıdır. Notunuzu yükseltmek amacıyla tekrar seçebilirsiniz.
                    </p>
                  </div>
                </div>
              )}

              {/* Prerequisites Card */}
              {detail.prerequisites && (
                <div className={`p-3.5 rounded-xl border flex items-start gap-3 ${
                  detail.prerequisites.can_take
                    ? 'bg-emerald-50 dark:bg-emerald-950/40 border-emerald-200 dark:border-emerald-800 text-emerald-900 dark:text-emerald-200'
                    : 'bg-amber-50 dark:bg-amber-950/40 border-amber-200 dark:border-amber-800 text-amber-900 dark:text-amber-200'
                }`}>
                  {detail.prerequisites.can_take ? (
                    <CheckCircle2 className="w-5 h-5 text-emerald-600 dark:text-emerald-400 shrink-0 mt-0.5" />
                  ) : (
                    <AlertCircle className="w-5 h-5 text-amber-600 dark:text-amber-400 shrink-0 mt-0.5" />
                  )}
                  <div className="text-xs space-y-1">
                    <p className="font-bold">
                      {detail.prerequisites.can_take ? 'Ön Koşul Durumu: Alınabilir' : 'Ön Koşul Durumu: Eksik Var'}
                    </p>
                    <p className="text-[11px] opacity-90">
                      Kural: <span className="font-semibold">{detail.prerequisites.rule_description}</span>
                    </p>
                    {detail.prerequisites.missing_prereqs?.length > 0 && (
                      <p className="text-[11px] text-red-600 dark:text-red-400 font-medium">
                        Eksik Ön Koşullar: {detail.prerequisites.missing_prereqs.join(', ')}
                      </p>
                    )}
                  </div>
                </div>
              )}

              {/* Description / Syllabus */}
              <div className="space-y-1.5">
                <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700 dark:text-slate-300 flex items-center gap-1.5">
                  <BookOpen className="w-3.5 h-3.5 text-amber-600 dark:text-amber-400" />
                  <span>Ders Tanımı ve İzlence</span>
                </h3>
                <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed bg-slate-50 dark:bg-darkbg-card p-3 rounded-xl border border-slate-200/80 dark:border-darkbg-border">
                  {detail.description}
                </p>
              </div>

              {/* Sections Table */}
              <div className="space-y-2">
                <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700 dark:text-slate-300 flex items-center gap-1.5">
                  <Calendar className="w-3.5 h-3.5 text-amber-600 dark:text-amber-400" />
                  <span>Açılan Şubeler ve Saatleri</span>
                </h3>

                <div className="divide-y divide-slate-100 dark:divide-darkbg-border border border-slate-200 dark:border-darkbg-border rounded-xl overflow-hidden">
                  {detail.sections.map((sec) => (
                    <div key={sec.section_no} className="p-3 bg-white dark:bg-darkbg-card flex flex-wrap items-center justify-between gap-2 text-xs">
                      <div>
                        <span className="font-bold text-slate-900 dark:text-white">
                          Şube {sec.section_no}
                        </span>
                        <div className="flex items-center gap-1 text-slate-500 dark:text-slate-400 text-[11px] mt-0.5">
                          <User className="w-3 h-3" />
                          <span>{sec.instructor}</span>
                        </div>
                      </div>

                      {/* Slot pills */}
                      <div className="flex flex-wrap gap-1">
                        {sec.slots.map((s, idx) => (
                          <span 
                            key={idx}
                            className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md bg-slate-100 dark:bg-darkbg-surface border border-slate-200 dark:border-darkbg-border text-[10px] font-medium text-slate-700 dark:text-slate-300"
                          >
                            <Clock className="w-2.5 h-2.5" />
                            {s.day} {s.time_slot}
                            {s.classroom && (
                              <span className="text-cankaya-gold-dark dark:text-cankaya-gold-light font-bold">
                                ({s.classroom})
                              </span>
                            )}
                          </span>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* External Links */}
              <div className="pt-2 border-t border-slate-200 dark:border-darkbg-border flex flex-wrap gap-2">
                {detail.course_url && (
                  <a
                    href={detail.course_url}
                    target="_blank"
                    rel="noreferrer"
                    className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-bold rounded-lg bg-amber-400 hover:bg-amber-500 text-slate-950 dark:bg-amber-400 dark:hover:bg-amber-300 dark:text-slate-950 transition-all shadow-xs"
                  >
                    <span>Resmi Ders Sayfası</span>
                    <ExternalLink className="w-3 h-3" />
                  </a>
                )}

                {detail.ebs_url && (
                  <a
                    href={detail.ebs_url}
                    target="_blank"
                    rel="noreferrer"
                    className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg bg-slate-100 dark:bg-darkbg-card text-slate-700 dark:text-slate-200 hover:bg-slate-200 dark:hover:bg-darkbg-border transition-all"
                  >
                    <span>EBS Bilgi Paketi</span>
                    <ExternalLink className="w-3 h-3" />
                  </a>
                )}
              </div>
            </>
          ) : null}
        </div>

      </div>
    </div>
  );
};
