import React, { useState } from 'react';
import { ScheduleProvider, useSchedule } from './context/ScheduleContext';
import { Navbar } from './components/Navbar';
import { CourseSearchPanel } from './components/CourseSearchPanel';
import { BasketPanel } from './components/BasketPanel';
import { CombinationBar } from './components/CombinationBar';
import { Timetable } from './components/Timetable';
import { CourseDetailModal } from './components/CourseDetailModal';
import { CustomBlockModal } from './components/CustomBlockModal';
import { TranscriptModal } from './components/TranscriptModal';
import { CurriculumModal } from './components/CurriculumModal';
import { SyncModal } from './components/SyncModal';
import { Search, ShoppingBag } from 'lucide-react';

const MainLayout = () => {
  const { basket } = useSchedule();
  const [leftTab, setLeftTab] = useState('search'); // 'search' | 'basket'
  const basketCount = Object.keys(basket).length;

  return (
    <div className="flex flex-col h-screen overflow-hidden bg-[#fafaf9] dark:bg-darkbg text-slate-900 dark:text-slate-100">

      {/* Top Navigation Bar */}
      <Navbar />

      {/* Main Workspace: 2-Column Split Layout */}
      <div className="flex flex-1 overflow-hidden">

        {/* Left Sidebar: Course Search & Basket (420px width) */}
        <div className="w-[380px] lg:w-[440px] flex flex-col shrink-0 border-r border-slate-200/80 dark:border-darkbg-border bg-white dark:bg-darkbg-surface">

          {/* Tab Bar */}
          <div className="flex border-b border-slate-200/80 dark:border-darkbg-border bg-slate-50/70 dark:bg-darkbg-card/40 p-1.5 gap-1">
            <button
              onClick={() => setLeftTab('search')}
              className={`flex-1 py-1.5 px-3 rounded-lg text-xs font-bold flex items-center justify-center gap-1.5 transition-all ${leftTab === 'search'
                ? 'bg-amber-400 text-slate-950 dark:bg-amber-400 dark:text-slate-950 shadow-xs'
                : 'text-slate-500 hover:text-slate-800 dark:text-slate-400 dark:hover:text-amber-300'
                }`}
            >
              <Search className="w-3.5 h-3.5" />
              <span>Ders Arama</span>
            </button>

            <button
              onClick={() => setLeftTab('basket')}
              className={`flex-1 py-1.5 px-3 rounded-lg text-xs font-bold flex items-center justify-center gap-1.5 transition-all ${leftTab === 'basket'
                ? 'bg-amber-400 text-slate-950 dark:bg-amber-400 dark:text-slate-950 shadow-xs'
                : 'text-slate-500 hover:text-slate-800 dark:text-slate-400 dark:hover:text-amber-300'
                }`}
            >
              <ShoppingBag className="w-3.5 h-3.5" />
              <span>Sepetim</span>
              {basketCount > 0 && (
                <span className="text-[10px] font-extrabold px-1.5 py-0.2 rounded-full bg-slate-900 text-amber-400 dark:bg-black dark:text-amber-400">
                  {basketCount}
                </span>
              )}
            </button>
          </div>

          {/* Active Tab View */}
          <div className="flex-1 overflow-hidden">
            {leftTab === 'search' ? <CourseSearchPanel /> : <BasketPanel />}
          </div>

        </div>

        {/* Center / Right: Timetable & Combination Bar */}
        <div className="flex-1 flex flex-col overflow-hidden bg-slate-100/50 dark:bg-darkbg">
          <CombinationBar />
          <Timetable />
        </div>

      </div>

      {/* Global Modals */}
      <CourseDetailModal />
      <CustomBlockModal />
      <TranscriptModal />
      <CurriculumModal />
      <SyncModal />

    </div>
  );
};

export default function App() {
  return (
    <ScheduleProvider>
      <MainLayout />
    </ScheduleProvider>
  );
}
