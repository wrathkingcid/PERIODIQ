const API_BASE = "http://127.0.0.1:8000/api/v1";

export interface Institution {
  id: number;
  name: string;
  type: "SCHOOL" | "COLLEGE" | "COACHING";
  code: string;
  description: string;
  contact_email: string;
  working_days: string[];
  periods_per_day: number;
  period_duration_minutes: number;
  day_start_time: string;
  breaks: Array<{ name: string; after_period: number; duration_minutes: number }>;
  shifts: Array<{ name: string; start_time: string; end_time: string; periods: number }>;
  features: Record<string, boolean>;
}

export interface TimetableEntry {
  id: number;
  scenario_id: number;
  day_index: number;
  day_name: string;
  slot_index: number;
  slot_label: string;
  division_id: number;
  class_group_id: number;
  subject_id: number;
  teacher_id: number;
  room_id: number;
  is_locked: boolean;
  is_manual_override?: boolean;
}

export interface TimetableScenario {
  id: number;
  institution_id: number;
  name: string;
  academic_year: string;
  term: string;
  status: "DRAFT" | "GENERATING" | "OPTIMAL" | "FEASIBLE" | "INFEASIBLE" | "APPROVED" | "PUBLISHED";
  solver_status: string;
  solver_time_seconds: number;
  quality_score: number;
  metrics: {
    teacher_idle_gaps: number;
    student_idle_gaps: number;
    room_utilization_pct: number;
    subject_balance_score: number;
    total_assigned_periods?: number;
  };
  infeasibility_report?: {
    status: string;
    severity: string;
    diagnostic_count: number;
    diagnostics: Array<{ category: string; entity: string; demanded?: any; available?: any; message: string }>;
    recommendations: string[];
    possible_solutions: string[];
  };
  is_published: boolean;
  created_at: string;
}

export interface AcademicData {
  classes: Array<{ id: number; name: string; code: string; divisions: Array<{ id: number; name: string; student_count: number }> }>;
  subjects: Array<{ id: number; class_group_id: number; name: string; code: string; weekly_hours: number; consecutive_periods: number; is_lab: boolean; preferred_room_type: string; color_code: string }>;
  teachers: Array<{ id: number; name: string; code: string; email: string; designation: string; max_hours_per_day: number; max_hours_per_week: number; competent_subject_ids: number[]; blackout_slots: number[][]; preferred_slots: number[][] }>;
  rooms: Array<{ id: number; name: string; code: string; room_type: string; capacity: number; building: string }>;
}

export const api = {
  // Institutions
  getInstitutions: async (): Promise<Institution[]> => {
    const res = await fetch(`${API_BASE}/institutions/`);
    return res.json();
  },
  getInstitution: async (id: number): Promise<Institution> => {
    const res = await fetch(`${API_BASE}/institutions/${id}`);
    return res.json();
  },
  updateInstitution: async (id: number, data: Partial<Institution>): Promise<Institution> => {
    const res = await fetch(`${API_BASE}/institutions/${id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    return res.json();
  },
  seedSamples: async (type: string = "ALL") => {
    const res = await fetch(`${API_BASE}/institutions/1/seed-samples?sample_type=${type}`, { method: "POST" });
    return res.json();
  },

  // Academic Entities
  getAcademicData: async (instId: number): Promise<AcademicData> => {
    const [classes, subjects, teachers, rooms] = await Promise.all([
      fetch(`${API_BASE}/academic/institutions/${instId}/classes`).then((r) => r.json()),
      fetch(`${API_BASE}/academic/institutions/${instId}/subjects`).then((r) => r.json()),
      fetch(`${API_BASE}/academic/institutions/${instId}/teachers`).then((r) => r.json()),
      fetch(`${API_BASE}/academic/institutions/${instId}/rooms`).then((r) => r.json()),
    ]);
    return { classes, subjects, teachers, rooms };
  },

  // Timetables
  generateTimetable: async (
    instId: number,
    params: { scenario_name: string; academic_year: string; term: string; timeout_seconds: number; enable_soft_constraints: boolean }
  ) => {
    const res = await fetch(`${API_BASE}/institutions/${instId}/generate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(params),
    });
    return res.json();
  },

  getScenarios: async (instId: number): Promise<TimetableScenario[]> => {
    const res = await fetch(`${API_BASE}/institutions/${instId}/scenarios`);
    return res.json();
  },

  getScenario: async (scenarioId: number): Promise<{ scenario: TimetableScenario; entries: TimetableEntry[] }> => {
    const res = await fetch(`${API_BASE}/scenarios/${scenarioId}`);
    return res.json();
  },

  toggleLock: async (entryId: number): Promise<{ id: number; is_locked: boolean }> => {
    const res = await fetch(`${API_BASE}/entries/${entryId}/toggle-lock`, { method: "POST" });
    return res.json();
  },

  swapEntry: async (
    entryId: number,
    data: { target_day_index: number; target_slot_index: number; target_room_id?: number; target_teacher_id?: number }
  ) => {
    const res = await fetch(`${API_BASE}/entries/${entryId}/swap`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    return res.json();
  },

  publishScenario: async (scenarioId: number) => {
    const res = await fetch(`${API_BASE}/scenarios/${scenarioId}/publish`, { method: "POST" });
    return res.json();
  },

  getExcelDownloadUrl: (scenarioId: number) => `${API_BASE}/scenarios/${scenarioId}/export-excel`,

  compareScenarios: async (instId: number, sc1Id: number, sc2Id: number) => {
    const res = await fetch(`${API_BASE}/institutions/${instId}/compare-scenarios?sc1_id=${sc1Id}&sc2_id=${sc2Id}`);
    return res.json();
  },

  // Shift Planning
  analyzeShifts: async (instId: number) => {
    const res = await fetch(`${API_BASE}/shifts/institutions/${instId}/analyze`, { method: "POST" });
    return res.json();
  },

  // Document Ingestion
  uploadDocument: async (instId: number, file: File) => {
    const formData = new FormData();
    formData.append("file", file);
    const res = await fetch(`${API_BASE}/upload/institutions/${instId}/parse-file`, {
      method: "POST",
      body: formData,
    });
    return res.json();
  },

  commitIngest: async (instId: number, data: any) => {
    const res = await fetch(`${API_BASE}/upload/institutions/${instId}/commit-ingest`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    return res.json();
  },

  // Analytics
  getDashboardAnalytics: async (instId: number) => {
    const res = await fetch(`${API_BASE}/analytics/institutions/${instId}/dashboard-summary`);
    return res.json();
  },
};
