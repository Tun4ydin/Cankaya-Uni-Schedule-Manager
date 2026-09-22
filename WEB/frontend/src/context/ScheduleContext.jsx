import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { api } from '../services/api';

const ScheduleContext = createContext(null);

const STORAGE_KEYS = {
  BASKET: 'cankaya_schedule_basket',
  COMBINATIONS: 'cankaya_schedule_combinations',
  COMB_INDEX: 'cankaya_schedule_comb_index',
  PREFERENCES: 'cankaya_schedule_preferences',
  THEME: 'cankaya_schedule_theme',
  PROFILE: 'cankaya_schedule_profile_cache'
};

export const ScheduleProvider = ({ children }) => {
  // Theme state (initialized from localStorage)
  const [theme, setTheme] = useState(() => {
    try {
      return localStorage.getItem(STORAGE_KEYS.THEME) || 'light';
    } catch {
      return 'light';
    }
  });

  // Profile & Departments (initialized from localStorage cache as fallback)
  const [profile, setProfile] = useState(() => {
    try {
      const cached = localStorage.getItem(STORAGE_KEYS.PROFILE);
      return cached ? JSON.parse(cached) : {
        primary_dept: 'CENG',
        secondary_dept: 'YOK',
        secondary_type: 'YOK',
        custom_schedule_blocks: {},
        passed_courses: {}
      };
    } catch {
      return {
        primary_dept: 'CENG',
        secondary_dept: 'YOK',
        secondary_type: 'YOK',
        custom_schedule_blocks: {},
        passed_courses: {}
      };
    }
  });
  const [departments, setDepartments] = useState([]);
  const [classroomMap, setClassroomMap] = useState({});

  // Selected Courses (Basket) (initialized from localStorage)
  const [basket, setBasket] = useState(() => {
    try {
      const cached = localStorage.getItem(STORAGE_KEYS.BASKET);
      return cached ? JSON.parse(cached) : {};
    } catch {
      return {};
    }
  });

  // Combinations (initialized from localStorage)
  const [combinations, setCombinations] = useState(() => {
    try {
      const cached = localStorage.getItem(STORAGE_KEYS.COMBINATIONS);
      return cached ? JSON.parse(cached) : [];
    } catch {
      return [];
    }
  });

  const [currentCombinationIndex, setCurrentCombinationIndex] = useState(() => {
    try {
      const cached = localStorage.getItem(STORAGE_KEYS.COMB_INDEX);
      const val = cached !== null ? parseInt(cached, 10) : 0;
      return isNaN(val) ? 0 : val;
    } catch {
      return 0;
    }
  });

  const [isLoadingCombinations, setIsLoadingCombinations] = useState(false);
  const [combinationError, setCombinationError] = useState(null);

  // Preferences (initialized from localStorage)
  const [preferences, setPreferences] = useState(() => {
    try {
      const cached = localStorage.getItem(STORAGE_KEYS.PREFERENCES);
      return cached ? JSON.parse(cached) : {
        free_friday: false,
        free_monday: false,
        no_morning: false
      };
    } catch {
      return {
        free_friday: false,
        free_monday: false,
        no_morning: false
      };
    }
  });

  // Modal State
  const [modalState, setModalState] = useState({
    type: null, // 'courseDetail' | 'customBlock' | 'transcript' | 'curriculum' | 'conflict' | 'sync'
    data: null
  });

  // Persistence Effects
  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEYS.BASKET, JSON.stringify(basket));
    } catch (e) {
      console.error('Failed to save basket to localStorage:', e);
    }
  }, [basket]);

  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEYS.COMBINATIONS, JSON.stringify(combinations));
    } catch (e) {
      console.error('Failed to save combinations to localStorage:', e);
    }
  }, [combinations]);

  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEYS.COMB_INDEX, String(currentCombinationIndex));
    } catch (e) {
      console.error('Failed to save comb index to localStorage:', e);
    }
  }, [currentCombinationIndex]);

  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEYS.PREFERENCES, JSON.stringify(preferences));
    } catch (e) {
      console.error('Failed to save preferences to localStorage:', e);
    }
  }, [preferences]);

  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEYS.THEME, theme);
    } catch (e) {
      console.error('Failed to save theme to localStorage:', e);
    }
  }, [theme]);

  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEYS.PROFILE, JSON.stringify(profile));
    } catch (e) {
      console.error('Failed to save profile cache to localStorage:', e);
    }
  }, [profile]);

  // Initial load: Profile, Departments & Classrooms from API
  const loadInitialData = useCallback(async () => {
    try {
      const [profData, deptsData, classroomsData] = await Promise.all([
        api.getProfile(),
        api.getDepartments(),
        api.getClassrooms().catch(err => {
          console.error('Classrooms fetch failed:', err);
          return {};
        })
      ]);
      setProfile(profData);
      setDepartments(deptsData);
      setClassroomMap(classroomsData || {});
      if (profData.theme) {
        setTheme(profData.theme === 'dark' ? 'dark' : 'light');
      }
    } catch (err) {
      console.error('Initial data loading failed:', err);
    }
  }, []);

  useEffect(() => {
    loadInitialData();
  }, [loadInitialData]);

  // Auto-heal combinations and basket with classroom data when classroomMap is loaded
  useEffect(() => {
    if (!classroomMap || Object.keys(classroomMap).length === 0) return;

    setCombinations(prev => {
      if (!prev || prev.length === 0) return prev;
      let modified = false;
      const next = prev.map(combo => {
        const updatedSections = (combo.sections || []).map(sec => {
          const cData = classroomMap[sec.course_code]?.[String(sec.section_no)];
          const targetSecClassroom = sec.classroom || cData?.classroom || "";
          let secChanged = false;
          if (sec.classroom !== targetSecClassroom) secChanged = true;

          const updatedSlots = (sec.slots || []).map(sl => {
            const slotKey = `${sl.day}:${sl.time_slot}`;
            const targetSlotClassroom = sl.classroom || cData?.slots?.[slotKey] || targetSecClassroom || "";
            if (sl.classroom !== targetSlotClassroom) secChanged = true;
            return {
              ...sl,
              classroom: targetSlotClassroom
            };
          });

          if (secChanged) modified = true;
          return {
            ...sec,
            classroom: targetSecClassroom,
            slots: updatedSlots
          };
        });
        return { ...combo, sections: updatedSections };
      });
      return modified ? next : prev;
    });

    setBasket(prev => {
      if (!prev || Object.keys(prev).length === 0) return prev;
      let modified = false;
      const next = { ...prev };
      for (const [code, item] of Object.entries(next)) {
        if (Array.isArray(item.sections)) {
          const updatedSecs = item.sections.map(sec => {
            const cData = classroomMap[code]?.[String(sec.section_no)];
            const targetSecClassroom = sec.classroom || cData?.classroom || "";
            let secChanged = false;
            if (sec.classroom !== targetSecClassroom) secChanged = true;

            const updatedSlots = (sec.slots || []).map(sl => {
              const slotKey = `${sl.day}:${sl.time_slot}`;
              const targetSlotClassroom = sl.classroom || cData?.slots?.[slotKey] || targetSecClassroom || "";
              if (sl.classroom !== targetSlotClassroom) secChanged = true;
              return {
                ...sl,
                classroom: targetSlotClassroom
              };
            });

            if (secChanged) modified = true;
            return {
              ...sec,
              classroom: targetSecClassroom,
              slots: updatedSlots
            };
          });
          if (modified) {
            next[code] = { ...item, sections: updatedSecs };
          }
        }
      }
      return modified ? next : prev;
    });
  }, [classroomMap]);

  // Sync theme with HTML class
  useEffect(() => {
    const root = document.documentElement;
    if (theme === 'dark') {
      root.classList.add('dark');
    } else {
      root.classList.remove('dark');
    }
  }, [theme]);

  const toggleTheme = () => {
    const newTheme = theme === 'light' ? 'dark' : 'light';
    setTheme(newTheme);
    api.updateProfile({ theme: newTheme }).catch(console.error);
  };

  // Profile update
  const updateDepartments = async (primary_dept, secondary_dept, secondary_type) => {
    try {
      const updated = await api.updateProfile({ primary_dept, secondary_dept, secondary_type });
      setProfile(prev => ({ ...prev, ...updated }));
    } catch (err) {
      console.error('Failed to update departments:', err);
    }
  };

  // Basket operations
  const addCourseToBasket = (course) => {
    setBasket(prev => {
      if (prev[course.code]) return prev;
      const instructors = Array.from(new Set(
        (course.sections || [])
          .map(s => s.instructor)
          .filter(Boolean)
      ));

      return {
        ...prev,
        [course.code]: {
          code: course.code,
          name: course.name || course.code,
          lockedSection: 'auto',
          credit: course.credit || 3,
          ects: course.ects || 5,
          sections: course.sections || [],
          prerequisites: course.prerequisites,
          passed_info: course.passed_info,
          allowedInstructors: instructors
        }
      };
    });
  };

  const removeCourseFromBasket = (code) => {
    setBasket(prev => {
      const copy = { ...prev };
      delete copy[code];
      return copy;
    });
  };

  const updateLockedSection = (code, sectionNo) => {
    setBasket(prev => {
      if (!prev[code]) return prev;
      return {
        ...prev,
        [code]: {
          ...prev[code],
          lockedSection: sectionNo
        }
      };
    });
  };

  const updateAllowedInstructors = (code, instructors) => {
    setBasket(prev => {
      if (!prev[code]) return prev;
      const current = prev[code];
      let lockedSection = current.lockedSection;
      if (lockedSection && lockedSection !== 'auto') {
        const sec = (current.sections || []).find(s => String(s.section_no) === String(lockedSection));
        if (sec && !instructors.includes(sec.instructor)) {
          lockedSection = 'auto';
        }
      }

      return {
        ...prev,
        [code]: {
          ...current,
          allowedInstructors: instructors,
          lockedSection
        }
      };
    });
  };

  const clearBasket = () => {
    setBasket({});
    setCombinations([]);
    setCurrentCombinationIndex(0);
    try {
      localStorage.removeItem(STORAGE_KEYS.BASKET);
      localStorage.removeItem(STORAGE_KEYS.COMBINATIONS);
      localStorage.removeItem(STORAGE_KEYS.COMB_INDEX);
    } catch (e) {
      console.error('Failed to clear basket from localStorage:', e);
    }
  };

  // Preference toggle
  const togglePreference = (key) => {
    setPreferences(prev => ({
      ...prev,
      [key]: !prev[key]
    }));
  };

  // Generate Combinations
  const generateSchedule = async () => {
    const courseCodes = Object.keys(basket);
    if (courseCodes.length === 0) {
      setCombinations([]);
      setCurrentCombinationIndex(0);
      return;
    }

    setIsLoadingCombinations(true);
    setCombinationError(null);

    const lockedSections = {};
    const allowedInstructors = {};
    for (const [code, item] of Object.entries(basket)) {
      if (item.lockedSection && item.lockedSection !== 'auto') {
        lockedSections[code] = item.lockedSection;
      }
      const allInst = Array.from(new Set((item.sections || []).map(s => s.instructor).filter(Boolean)));
      allowedInstructors[code] = item.allowedInstructors ?? allInst;
    }

    try {
      const result = await api.generateCombinations({
        courses: courseCodes,
        lockedSections,
        allowedInstructors,
        preferences,
        customBlocks: profile.custom_schedule_blocks
      });

      setCombinations(result.combinations || []);
      setCurrentCombinationIndex(0);

      if (result.total_combinations === 0) {
        setCombinationError('Seçilen dersler veya şubeler arasında çakışma olduğu için geçerli bir kombinasyon bulunamadı.');
      }
    } catch (err) {
      console.error('Error generating combinations:', err);
      setCombinationError(err.message || 'Kombinasyon hesaplanırken bir hata meydana geldi.');
    } finally {
      setIsLoadingCombinations(false);
    }
  };

  // Custom blocks
  const addCustomBlock = async (blockData) => {
    try {
      const updatedBlocks = await api.setCustomBlock(blockData);
      setProfile(prev => ({
        ...prev,
        custom_schedule_blocks: updatedBlocks
      }));
    } catch (err) {
      console.error('Error adding custom block:', err);
    }
  };

  const removeCustomBlock = async (day, time_slot) => {
    try {
      const updatedBlocks = await api.deleteCustomBlock({ day, time_slot });
      setProfile(prev => ({
        ...prev,
        custom_schedule_blocks: updatedBlocks
      }));
    } catch (err) {
      console.error('Error removing custom block:', err);
    }
  };

  // Modal helpers
  const openModal = (type, data = null) => {
    setModalState({ type, data });
  };

  const closeModal = () => {
    setModalState({ type: null, data: null });
  };

  // Current active combination
  const currentCombination = combinations[currentCombinationIndex] || null;

  return (
    <ScheduleContext.Provider
      value={{
        theme,
        toggleTheme,
        profile,
        setProfile,
        departments,
        updateDepartments,
        classroomMap,
        basket,
        addCourseToBasket,
        removeCourseFromBasket,
        updateLockedSection,
        updateAllowedInstructors,
        clearBasket,
        combinations,
        currentCombinationIndex,
        setCurrentCombinationIndex,
        currentCombination,
        isLoadingCombinations,
        combinationError,
        preferences,
        togglePreference,
        generateSchedule,
        addCustomBlock,
        removeCustomBlock,
        modalState,
        openModal,
        closeModal,
        refreshProfile: loadInitialData
      }}
    >
      {children}
    </ScheduleContext.Provider>
  );
};

export const useSchedule = () => {
  const context = useContext(ScheduleContext);
  if (!context) {
    throw new Error('useSchedule must be used within a ScheduleProvider');
  }
  return context;
};
