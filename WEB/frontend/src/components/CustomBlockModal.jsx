import React, { useState, useEffect } from 'react';
import { useSchedule } from '../context/ScheduleContext';
import { X, Trash2, Check, Clock, Calendar, Sparkles } from 'lucide-react';

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

const PRESET_TITLES = [
  { label: '🍔 Yemek Arası', value: 'Yemek Arası', color: 'amber' },
  { label: '☕ Kahve / Mola', value: 'Mola', color: 'slate' },
  { label: '📚 Ders Çalışma', value: 'Ders Çalışma', color: 'blue' },
  { label: '🏋️ Spor', value: 'Spor', color: 'emerald' },
];

const COLOR_OPTIONS = [
  { id: 'amber', label: 'Sarı / Amber', class: 'bg-amber-400' },
  { id: 'blue', label: 'Mavi', class: 'bg-blue-400' },
  { id: 'emerald', label: 'Yeşil', class: 'bg-emerald-400' },
  { id: 'rose', label: 'Kırmızı', class: 'bg-rose-400' },
  { id: 'slate', label: 'Gri', class: 'bg-slate-400' },
];

export const CustomBlockModal = () => {
  const { modalState, closeModal, addCustomBlock, removeCustomBlock } = useSchedule();
  const modalData = modalState.data;

  const [day, setDay] = useState('Pazartesi');
  const [timeSlot, setTimeSlot] = useState('12:00 - 12:50');
  const [title, setTitle] = useState('');
  const [note, setNote] = useState('');
  const [color, setColor] = useState('amber');

  const isEditing = !!modalData?.block;

  useEffect(() => {
    if (modalData) {
      if (modalData.day) setDay(modalData.day);
      if (modalData.time_slot) setTimeSlot(modalData.time_slot);
      if (modalData.block) {
        setTitle(modalData.block.title || '');
        setNote(modalData.block.note || '');
        setColor(modalData.block.color || 'amber');
      } else {
        setTitle('Yemek Arası');
        setNote('');
        setColor('amber');
      }
    }
  }, [modalData]);

  if (modalState.type !== 'customBlock') return null;

  const handleSave = async (e) => {
    e.preventDefault();
    if (!title.trim()) return;

    await addCustomBlock({
      day,
      time_slot: timeSlot,
      title: title.trim(),
      note: note.trim(),
      color
    });
    closeModal();
  };

  const handleDelete = async () => {
    await removeCustomBlock(day, timeSlot);
    closeModal();
  };

  return (
    <div className="fixed inset-0 z-50 bg-slate-900/50 backdrop-blur-xs flex items-center justify-center p-4">
      <div className="bg-white dark:bg-darkbg-surface rounded-2xl border border-slate-200 dark:border-darkbg-border max-w-md w-full shadow-2xl overflow-hidden animate-fadeIn">

        {/* Header */}
        <div className="p-4 border-b border-slate-200 dark:border-darkbg-border flex items-center justify-between bg-slate-50/60 dark:bg-darkbg-card/60">
          <h2 className="text-sm font-bold text-slate-900 dark:text-white flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-amber-500 dark:text-amber-400" />
            <span>{isEditing ? 'Özel Etkinliği Düzenle' : 'Özel Etkinlik / Mola Ekle'}</span>
          </h2>
          <button
            onClick={closeModal}
            className="p-1.5 rounded-lg text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-darkbg-border"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSave} className="p-5 space-y-4">

          {/* Day & Time Selectors */}
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400 mb-1 block">
                Gün
              </label>
              <select
                value={day}
                onChange={(e) => setDay(e.target.value)}
                className="w-full text-xs py-2 px-2.5 rounded-lg bg-slate-50 dark:bg-darkbg-card border border-slate-200 dark:border-darkbg-border text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-1 focus:ring-amber-400 dark:focus:ring-amber-400"
              >
                {DAYS.map(d => (
                  <option key={d} value={d}>{d}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400 mb-1 block">
                Saat Dilimi
              </label>
              <select
                value={timeSlot}
                onChange={(e) => setTimeSlot(e.target.value)}
                className="w-full text-xs py-2 px-2.5 rounded-lg bg-slate-50 dark:bg-darkbg-card border border-slate-200 dark:border-darkbg-border text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-1 focus:ring-amber-400 dark:focus:ring-amber-400"
              >
                {TIME_SLOTS.map(ts => (
                  <option key={ts} value={ts}>{ts}</option>
                ))}
              </select>
            </div>
          </div>

          {/* Title Input */}
          <div>
            <label className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400 mb-1 block">
              Başlık <span className="text-red-500">*</span>
            </label>
            <div className="space-y-1.5">
              <input
                type="text"
                placeholder="örn. Öğle Yemeği, Çalışma, Spor, vb."
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                required
                className="w-full text-xs py-2 px-3 rounded-lg bg-slate-50 dark:bg-darkbg-card border border-slate-200 dark:border-darkbg-border text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-1 focus:ring-amber-400 dark:focus:ring-amber-400"
              />
              {/* Quick Presets */}
              <div className="flex flex-wrap gap-1">
                {['Öğle Yemeği', 'Çalışma', 'Spor', 'Yol', 'Toplantı'].map(preset => (
                  <button
                    type="button"
                    key={preset}
                    onClick={() => setTitle(preset)}
                    className="text-[10px] px-2 py-0.5 rounded-md bg-slate-100 dark:bg-darkbg-border text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors"
                  >
                    {preset}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Note Input */}
          <div>
            <label className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400 mb-1 block">
              Not (İsteğe Bağlı)
            </label>
            <input
              type="text"
              placeholder="Ek açıklama..."
              value={note}
              onChange={(e) => setNote(e.target.value)}
              className="w-full text-xs py-2 px-3 rounded-lg bg-slate-50 dark:bg-darkbg-card border border-slate-200 dark:border-darkbg-border text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-1 focus:ring-amber-400 dark:focus:ring-amber-400"
            />
          </div>

          {/* Color Selector */}
          <div>
            <label className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400 mb-1.5 block">
              Renk Etiketi
            </label>
            <div className="flex items-center gap-2">
              {COLOR_OPTIONS.map((c) => (
                <button
                  type="button"
                  key={c.id}
                  onClick={() => setColor(c.id)}
                  className={`w-7 h-7 rounded-full ${c.class} flex items-center justify-center transition-all ${color === c.id ? 'ring-2 ring-offset-2 ring-amber-400 dark:ring-offset-darkbg-surface scale-110' : 'opacity-70 hover:opacity-100'
                    }`}
                  title={c.label}
                >
                  {color === c.id && <Check className="w-3.5 h-3.5 text-white" />}
                </button>
              ))}
            </div>
          </div>

          {/* Actions */}
          <div className="pt-3 border-t border-slate-200 dark:border-darkbg-border flex items-center justify-between gap-2">
            {isEditing ? (
              <button
                type="button"
                onClick={handleDelete}
                className="px-3 py-1.5 rounded-lg text-xs font-medium text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-950/40 transition-colors flex items-center gap-1"
              >
                <Trash2 className="w-3.5 h-3.5" />
                <span>Sil</span>
              </button>
            ) : <div />}

            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={closeModal}
                className="px-3 py-1.5 rounded-lg text-xs font-medium text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-darkbg-card transition-colors"
              >
                Vazgeç
              </button>
              <button
                type="submit"
                className="px-4 py-1.5 rounded-lg text-xs font-bold text-slate-950 bg-amber-400 hover:bg-amber-500 dark:bg-amber-400 dark:text-slate-950 dark:hover:bg-amber-300 transition-all shadow-xs active:scale-95"
              >
                Kaydet
              </button>
            </div>
          </div>

        </form>

      </div>
    </div>
  );
};
