import React, { useState } from 'react';
import { useSchedule } from '../context/ScheduleContext';
import { api } from '../services/api';
import { 
  X, 
  Upload, 
  FileText, 
  CheckCircle2, 
  AlertCircle, 
  Sparkles,
  ArrowRight
} from 'lucide-react';

export const TranscriptModal = () => {
  const { modalState, closeModal, refreshProfile } = useSchedule();

  const [activeTab, setActiveTab] = useState('upload'); // 'upload' | 'text'
  const [textInput, setTextInput] = useState('');
  const [selectedFile, setSelectedFile] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [parsedData, setParsedData] = useState(null);
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState(null);

  if (modalState.type !== 'transcript') return null;

  const handleFileUpload = async (file) => {
    if (!file) return;
    setIsLoading(true);
    setError(null);
    setParsedData(null);
    setSuccessMessage(null);

    try {
      const data = await api.uploadTranscriptFile(file);
      setParsedData(data);
    } catch (err) {
      console.error(err);
      setError('Transkript dosyası okunurken hata oluştu.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleTextParse = async () => {
    if (!textInput.trim()) return;
    setIsLoading(true);
    setError(null);
    setParsedData(null);
    setSuccessMessage(null);

    try {
      const data = await api.parseTranscriptText(textInput);
      setParsedData(data);
    } catch (err) {
      console.error(err);
      setError('Transkript metni çözümlenirken hata oluştu.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleApply = async () => {
    if (!parsedData) return;
    setIsLoading(true);
    setError(null);

    try {
      await api.applyTranscript({
        primary_dept: parsedData.primary_dept,
        secondary_dept: parsedData.secondary_dept,
        secondary_type: parsedData.secondary_type,
        passed_courses: parsedData.passed_courses || {}
      });
      await refreshProfile();
      setSuccessMessage('Transkript başarıyla profilinize uygulandı ve müfredat güncellendi!');
      setTimeout(() => {
        closeModal();
      }, 1500);
    } catch (err) {
      console.error(err);
      setError('Transkript uygulanırken hata oluştu.');
    } finally {
      setIsLoading(false);
    }
  };

  const passedCount = parsedData ? Object.keys(parsedData.passed_courses || {}).length : 0;
  const failedCount = parsedData ? Object.keys(parsedData.failed_courses || {}).length : 0;

  return (
    <div className="fixed inset-0 z-50 bg-slate-900/50 backdrop-blur-xs flex items-center justify-center p-4">
      <div className="bg-white dark:bg-darkbg-surface rounded-2xl border border-slate-200 dark:border-darkbg-border max-w-2xl w-full max-h-[90vh] flex flex-col shadow-2xl overflow-hidden animate-fadeIn">
        
        {/* Header */}
        <div className="p-4 border-b border-slate-200 dark:border-darkbg-border flex items-center justify-between bg-slate-50/60 dark:bg-darkbg-card/60">
          <h2 className="text-sm font-bold text-slate-900 dark:text-white flex items-center gap-2">
            <FileText className="w-4 h-4 text-amber-500 dark:text-amber-400" />
            <span>Transkript Yükle & Müfredatı Değerlendir</span>
          </h2>
          <button
            onClick={closeModal}
            className="p-1.5 rounded-lg text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-darkbg-border"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Tab Switcher */}
        <div className="flex border-b border-slate-200 dark:border-darkbg-border px-4 bg-slate-50/30 dark:bg-darkbg-card/30">
          <button
            onClick={() => setActiveTab('upload')}
            className={`py-2.5 px-4 text-xs font-bold border-b-2 transition-all ${
              activeTab === 'upload'
                ? 'border-amber-400 text-amber-800 dark:border-amber-400 dark:text-amber-300'
                : 'border-transparent text-slate-500 hover:text-slate-700 dark:hover:text-slate-300'
            }`}
          >
            PDF Dosyası Yükle
          </button>
          <button
            onClick={() => setActiveTab('text')}
            className={`py-2.5 px-4 text-xs font-bold border-b-2 transition-all ${
              activeTab === 'text'
                ? 'border-amber-400 text-amber-800 dark:border-amber-400 dark:text-amber-300'
                : 'border-transparent text-slate-500 hover:text-slate-700 dark:hover:text-slate-300'
            }`}
          >
            Metin Olarak Yapıştır
          </button>
        </div>

        {/* Modal Body */}
        <div className="flex-1 overflow-y-auto p-5 space-y-4">
          
          {/* Input Method */}
          {activeTab === 'upload' ? (
            <div className="border-2 border-dashed border-slate-200 dark:border-darkbg-border rounded-xl p-6 text-center hover:border-amber-400 dark:hover:border-amber-400 transition-colors bg-slate-50/50 dark:bg-darkbg-card/40">
              <input
                type="file"
                id="pdf-upload"
                accept=".pdf,.txt"
                className="hidden"
                onChange={(e) => {
                  const file = e.target.files?.[0];
                  if (file) {
                    setSelectedFile(file);
                    handleFileUpload(file);
                  }
                }}
              />
              <label htmlFor="pdf-upload" className="cursor-pointer flex flex-col items-center gap-2">
                <div className="w-12 h-12 rounded-full bg-amber-400/20 dark:bg-amber-400/15 flex items-center justify-center text-amber-800 dark:text-amber-400">
                  <Upload className="w-6 h-6" />
                </div>
                <div>
                  <p className="text-xs font-bold text-slate-800 dark:text-slate-200">
                    PDF transkriptinizi buraya sürükleyin veya seçin
                  </p>
                  <p className="text-[11px] text-slate-400 mt-0.5">
                    Çankaya web sitesinden veya e-devletten indirilen PDF transkriptler desteklenir.
                  </p>
                </div>
                {selectedFile && (
                  <span className="text-xs font-bold text-amber-800 dark:text-amber-300 mt-2 px-3 py-1 bg-amber-50 dark:bg-darkbg-surface border border-amber-200 dark:border-darkbg-border rounded-full">
                    {selectedFile.name}
                  </span>
                )}
              </label>
            </div>
          ) : (
            <div className="space-y-2">
              <textarea
                rows={5}
                placeholder="Transkript metnini buraya yapıştırın (Ders kodları ve harf notları)..."
                value={textInput}
                onChange={(e) => setTextInput(e.target.value)}
                className="w-full text-xs p-3 rounded-xl bg-slate-50 dark:bg-darkbg-card border border-slate-200 dark:border-darkbg-border text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-1 focus:ring-amber-400 dark:focus:ring-amber-400 font-mono"
              />
              <button
                onClick={handleTextParse}
                disabled={!textInput.trim() || isLoading}
                className="px-4 py-2 rounded-xl text-xs font-bold text-slate-950 bg-amber-400 hover:bg-amber-500 dark:bg-amber-400 dark:hover:bg-amber-300 dark:text-slate-950 transition-all disabled:opacity-50"
              >
                Metni Çözümle
              </button>
            </div>
          )}

          {/* Loading */}
          {isLoading && (
            <div className="flex items-center justify-center p-6 gap-2 text-slate-400">
              <div className="w-5 h-5 border-2 border-amber-500 dark:border-amber-400 border-t-transparent rounded-full animate-spin" />
              <span className="text-xs font-medium">Transkript taranıyor...</span>
            </div>
          )}

          {/* Error */}
          {error && (
            <div className="p-3 rounded-xl bg-red-50 dark:bg-red-950/40 border border-red-200 dark:border-red-800 text-red-700 dark:text-red-300 text-xs flex items-center gap-2">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          {/* Success */}
          {successMessage && (
            <div className="p-3 rounded-xl bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-800 text-emerald-700 dark:text-emerald-300 text-xs flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 shrink-0" />
              <span>{successMessage}</span>
            </div>
          )}

          {/* Parsed Results Overview */}
          {parsedData && (
            <div className="space-y-4 animate-fadeIn">
              
              {/* Detection Summary Cards */}
              <div className="grid grid-cols-3 gap-2 text-center text-xs">
                <div className="p-2.5 rounded-xl bg-slate-50 dark:bg-darkbg-card border border-slate-200 dark:border-darkbg-border">
                  <span className="text-[10px] font-bold text-slate-400 uppercase">Ana Bölüm</span>
                  <p className="font-extrabold text-slate-900 dark:text-white mt-0.5">
                    {parsedData.primary_dept || 'Belirlenemedi'}
                  </p>
                </div>

                <div className="p-2.5 rounded-xl bg-slate-50 dark:bg-darkbg-card border border-slate-200 dark:border-darkbg-border">
                  <span className="text-[10px] font-bold text-slate-400 uppercase">Geçilen Dersler</span>
                  <p className="font-extrabold text-emerald-600 dark:text-emerald-400 mt-0.5">
                    {passedCount} Ders
                  </p>
                </div>

                <div className="p-2.5 rounded-xl bg-slate-50 dark:bg-darkbg-card border border-slate-200 dark:border-darkbg-border">
                  <span className="text-[10px] font-bold text-slate-400 uppercase">Tekrar / Başarısız</span>
                  <p className="font-extrabold text-amber-600 dark:text-amber-400 mt-0.5">
                    {failedCount} Ders
                  </p>
                </div>
              </div>

              {/* Passed Courses Badges */}
              <div className="space-y-1.5">
                <h3 className="text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider">
                  Tespit Edilen Geçilmiş Dersler ({passedCount})
                </h3>
                <div className="flex flex-wrap gap-1.5 max-h-40 overflow-y-auto p-2 bg-slate-50 dark:bg-darkbg-card rounded-xl border border-slate-200 dark:border-darkbg-border">
                  {Object.entries(parsedData.passed_courses || {}).map(([code, info]) => (
                    <span 
                      key={code}
                      className="px-2 py-0.5 rounded-md bg-white dark:bg-darkbg-surface border border-slate-200 dark:border-darkbg-border text-[11px] font-bold text-slate-700 dark:text-slate-300 flex items-center gap-1 shadow-2xs"
                    >
                      <span>{code}</span>
                      <span className="text-emerald-600 dark:text-emerald-400 font-extrabold">
                        ({typeof info === 'object' ? info.grade : info})
                      </span>
                    </span>
                  ))}
                </div>
              </div>

              {/* Apply Button */}
              <button
                onClick={handleApply}
                disabled={isLoading}
                className="w-full py-2.5 rounded-xl text-xs font-bold text-white bg-emerald-600 hover:bg-emerald-700 dark:bg-emerald-500 dark:text-slate-950 dark:hover:bg-emerald-400 transition-all shadow-md shadow-emerald-600/20 flex items-center justify-center gap-2 active:scale-98"
              >
                <Sparkles className="w-4 h-4" />
                <span>Bu Bilgileri Profile Uygula ve Müfredatı Güncelle</span>
              </button>

            </div>
          )}

        </div>

      </div>
    </div>
  );
};
