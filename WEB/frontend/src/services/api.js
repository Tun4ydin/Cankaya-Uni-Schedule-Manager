const API_BASE = '/api';

export const api = {
  // Departments & Courses
  async getDepartments() {
    const res = await fetch(`${API_BASE}/courses/departments`);
    if (!res.ok) throw new Error('Bölümler alınamadı');
    return res.json();
  },

  async getClassrooms() {
    const res = await fetch(`${API_BASE}/courses/classrooms`);
    if (!res.ok) throw new Error('Derslik bilgileri alınamadı');
    return res.json();
  },

  async searchCourses({ query = '', dept = '', courseType = '', primaryDept = '', secondaryDept = '', secondaryType = '' } = {}) {
    const params = new URLSearchParams();
    if (query) params.append('query', query);
    if (dept && dept !== 'TÜMÜ') params.append('dept', dept);
    if (courseType && courseType !== 'TÜMÜ') params.append('course_type', courseType);
    if (primaryDept) params.append('primary_dept', primaryDept);
    if (secondaryDept && secondaryDept !== 'YOK') params.append('secondary_dept', secondaryDept);
    if (secondaryType && secondaryType !== 'YOK') params.append('secondary_type', secondaryType);

    const res = await fetch(`${API_BASE}/courses?${params.toString()}`);
    if (!res.ok) throw new Error('Dersler aranırken hata oluştu');
    return res.json();
  },

  async getCourseDetail(code, { primaryDept = '', secondaryDept = '', secondaryType = '' } = {}) {
    const params = new URLSearchParams();
    if (primaryDept) params.append('primary_dept', primaryDept);
    if (secondaryDept) params.append('secondary_dept', secondaryDept);
    if (secondaryType) params.append('secondary_type', secondaryType);

    const res = await fetch(`${API_BASE}/courses/${encodeURIComponent(code)}?${params.toString()}`);
    if (!res.ok) throw new Error('Ders detayları alınamadı');
    return res.json();
  },

  // Scheduler
  async generateCombinations({ courses, lockedSections = {}, allowedInstructors = {}, preferences = {}, customBlocks = null }) {
    const res = await fetch(`${API_BASE}/scheduler/combinations`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        courses,
        locked_sections: lockedSections,
        allowed_instructors: allowedInstructors,
        preferences,
        custom_blocks: customBlocks
      })
    });
    if (!res.ok) throw new Error('Kombinasyonlar oluşturulurken hata oluştu');
    return res.json();
  },

  async checkConflicts(sections, customBlocks = null) {
    const res = await fetch(`${API_BASE}/scheduler/conflicts`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        sections,
        custom_blocks: customBlocks
      })
    });
    if (!res.ok) throw new Error('Çakışma kontrolü yapılamadı');
    return res.json();
  },

  // Student Profile
  async getProfile() {
    const res = await fetch(`${API_BASE}/profile`);
    if (!res.ok) throw new Error('Profil yüklenemedi');
    return res.json();
  },

  async updateProfile(data) {
    const res = await fetch(`${API_BASE}/profile`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    if (!res.ok) throw new Error('Profil güncellenemedi');
    return res.json();
  },

  async setCustomBlock({ day, time_slot, title, note = '', color = 'amber' }) {
    const res = await fetch(`${API_BASE}/profile/custom-block`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ day, time_slot, title, note, color })
    });
    if (!res.ok) throw new Error('Özel blok kaydedilemedi');
    return res.json();
  },

  async deleteCustomBlock({ day, time_slot }) {
    const res = await fetch(`${API_BASE}/profile/custom-block`, {
      method: 'DELETE',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ day, time_slot })
    });
    if (!res.ok) throw new Error('Özel blok silinemedi');
    return res.json();
  },

  async addPassedCourse({ code, grade = 'CC', name = '' }) {
    const res = await fetch(`${API_BASE}/profile/passed-courses`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ code, grade, name })
    });
    if (!res.ok) throw new Error('Ders eklenemedi');
    return res.json();
  },

  async deletePassedCourse(code) {
    const res = await fetch(`${API_BASE}/profile/passed-courses/${encodeURIComponent(code)}`, {
      method: 'DELETE'
    });
    if (!res.ok) throw new Error('Ders silinemedi');
    return res.json();
  },

  // Transcript & Curriculum
  async parseTranscriptText(text) {
    const res = await fetch(`${API_BASE}/transcript/parse-text`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text })
    });
    if (!res.ok) throw new Error('Transkript metni çözümlenemedi');
    return res.json();
  },

  async uploadTranscriptFile(file) {
    const formData = new FormData();
    formData.append('file', file);

    const res = await fetch(`${API_BASE}/transcript/upload`, {
      method: 'POST',
      body: formData
    });
    if (!res.ok) throw new Error('Transkript dosyası yüklenemedi');
    return res.json();
  },

  async applyTranscript({ primary_dept, secondary_dept, secondary_type, passed_courses }) {
    const res = await fetch(`${API_BASE}/transcript/apply`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ primary_dept, secondary_dept, secondary_type, passed_courses })
    });
    if (!res.ok) throw new Error('Transkript uygulanamadı');
    return res.json();
  },

  async getCurriculumProgress(primaryDept) {
    const params = primaryDept ? `?primary_dept=${encodeURIComponent(primaryDept)}` : '';
    const res = await fetch(`${API_BASE}/curriculum/progress${params}`);
    if (!res.ok) throw new Error('Müfredat durumu alınamadı');
    return res.json();
  },

  // Live Scraper / Sync
  async startSync({ syncCourses = true, syncCurricula = true, deptList = null } = {}) {
    const res = await fetch(`${API_BASE}/sync/start`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        sync_courses: syncCourses,
        sync_curricula: syncCurricula,
        dept_list: deptList
      })
    });
    if (!res.ok) throw new Error('Veri çekme başlatılamadı');
    return res.json();
  },

  async getSyncStatus() {
    const res = await fetch(`${API_BASE}/sync/status`);
    if (!res.ok) throw new Error('Veri çekme durumu alınamadı');
    return res.json();
  },

  async cancelSync() {
    const res = await fetch(`${API_BASE}/sync/cancel`, {
      method: 'POST'
    });
    if (!res.ok) throw new Error('İptal işlemi başarısız oldu');
    return res.json();
  }
};
