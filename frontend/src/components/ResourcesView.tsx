import React, { useState } from "react";
import { AcademicData, Institution } from "../services/api";
import { 
  Users, 
  Building2, 
  BookOpen, 
  Layers, 
  Clock, 
  ShieldCheck, 
  FlaskConical, 
  Search,
  Filter
} from "lucide-react";

interface ResourcesViewProps {
  institution: Institution;
  academicData: AcademicData;
}

export const ResourcesView: React.FC<ResourcesViewProps> = ({
  institution,
  academicData,
}) => {
  const [activeTab, setActiveTab] = useState<"FACULTY" | "ROOMS" | "SUBJECTS" | "CLASSES">("FACULTY");
  const [searchQuery, setSearchQuery] = useState("");

  const { teachers, rooms, subjects, classes } = academicData;

  const filteredTeachers = teachers.filter((t) =>
    t.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    t.code.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const filteredRooms = rooms.filter((r) =>
    r.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    r.room_type.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const filteredSubjects = subjects.filter((s) =>
    s.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    s.code.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="space-y-5">
      {/* Search and Tabs Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-4 rounded-xl glass-panel">
        <div className="flex flex-wrap rounded-lg bg-slate-900 p-1 border border-slate-800">
          <button
            onClick={() => setActiveTab("FACULTY")}
            className={`px-3 py-1.5 text-xs font-medium rounded-md transition-all flex items-center gap-1.5 ${
              activeTab === "FACULTY"
                ? "bg-brand-600 text-white shadow"
                : "text-slate-400 hover:text-slate-200"
            }`}
          >
            <Users className="w-3.5 h-3.5" />
            <span>Faculty ({teachers.length})</span>
          </button>
          <button
            onClick={() => setActiveTab("ROOMS")}
            className={`px-3 py-1.5 text-xs font-medium rounded-md transition-all flex items-center gap-1.5 ${
              activeTab === "ROOMS"
                ? "bg-brand-600 text-white shadow"
                : "text-slate-400 hover:text-slate-200"
            }`}
          >
            <Building2 className="w-3.5 h-3.5" />
            <span>Rooms & Labs ({rooms.length})</span>
          </button>
          <button
            onClick={() => setActiveTab("SUBJECTS")}
            className={`px-3 py-1.5 text-xs font-medium rounded-md transition-all flex items-center gap-1.5 ${
              activeTab === "SUBJECTS"
                ? "bg-brand-600 text-white shadow"
                : "text-slate-400 hover:text-slate-200"
            }`}
          >
            <BookOpen className="w-3.5 h-3.5" />
            <span>Curriculum ({subjects.length})</span>
          </button>
          <button
            onClick={() => setActiveTab("CLASSES")}
            className={`px-3 py-1.5 text-xs font-medium rounded-md transition-all flex items-center gap-1.5 ${
              activeTab === "CLASSES"
                ? "bg-brand-600 text-white shadow"
                : "text-slate-400 hover:text-slate-200"
            }`}
          >
            <Layers className="w-3.5 h-3.5" />
            <span>Cohorts & Sections ({classes.length})</span>
          </button>
        </div>

        {/* Search */}
        <div className="relative w-full sm:w-64">
          <Search className="w-4 h-4 text-slate-500 absolute left-3 top-2.5" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search catalog..."
            className="w-full bg-slate-900 border border-slate-700/80 rounded-lg pl-9 pr-3 py-1.5 text-xs text-white placeholder-slate-500 focus:ring-1 focus:ring-brand-500 outline-none"
          />
        </div>
      </div>

      {/* Tab 1: Faculty */}
      {activeTab === "FACULTY" && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredTeachers.map((t) => (
            <div
              key={t.id}
              className="p-4 rounded-xl glass-panel hover:border-brand-500/40 transition-all space-y-3"
            >
              <div className="flex items-start justify-between">
                <div>
                  <h4 className="font-bold text-white text-sm">{t.name}</h4>
                  <span className="text-[11px] text-slate-400 font-mono">{t.code}</span>
                </div>
                <span className="text-[10px] px-2 py-0.5 rounded bg-brand-500/10 text-brand-300 border border-brand-500/20">
                  {t.designation}
                </span>
              </div>

              <div className="grid grid-cols-2 gap-2 text-xs py-2 border-t border-b border-slate-800">
                <div>
                  <span className="text-[10px] text-slate-500 block">Weekly Limit</span>
                  <span className="font-semibold text-slate-200">{t.max_hours_per_week} hrs/wk</span>
                </div>
                <div>
                  <span className="text-[10px] text-slate-500 block">Daily Limit</span>
                  <span className="font-semibold text-slate-200">{t.max_hours_per_day} hrs/day</span>
                </div>
              </div>

              {/* Blackouts & Preferences */}
              <div className="text-[11px] space-y-1">
                {t.blackout_slots?.length > 0 ? (
                  <div className="text-amber-400/90 flex items-center gap-1">
                    <Clock className="w-3 h-3" />
                    <span>{t.blackout_slots.length} blackout slots configured</span>
                  </div>
                ) : (
                  <div className="text-emerald-400/90 flex items-center gap-1">
                    <ShieldCheck className="w-3 h-3" />
                    <span>Full schedule availability</span>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Tab 2: Rooms & Labs */}
      {activeTab === "ROOMS" && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredRooms.map((r) => {
            const isLab = r.room_type.includes("lab");
            return (
              <div
                key={r.id}
                className="p-4 rounded-xl glass-panel hover:border-brand-500/40 transition-all space-y-3"
              >
                <div className="flex items-start justify-between">
                  <div>
                    <h4 className="font-bold text-white text-sm flex items-center gap-1.5">
                      {isLab && <FlaskConical className="w-4 h-4 text-emerald-400" />}
                      <span>{r.name}</span>
                    </h4>
                    <span className="text-[11px] text-slate-400 font-mono">{r.code}</span>
                  </div>
                  <span
                    className={`text-[10px] px-2 py-0.5 rounded font-medium ${
                      isLab
                        ? "bg-emerald-500/15 text-emerald-300 border border-emerald-500/30"
                        : "bg-slate-800 text-slate-300 border border-slate-700"
                    }`}
                  >
                    {r.room_type}
                  </span>
                </div>

                <div className="flex items-center justify-between text-xs py-2 border-t border-slate-800">
                  <span className="text-slate-400">Seating Capacity:</span>
                  <span className="font-bold text-white">{r.capacity} seats</span>
                </div>

                <div className="text-[11px] text-slate-500">
                  Building: {r.building || "Campus Center"}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Tab 3: Curriculum / Subjects */}
      {activeTab === "SUBJECTS" && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredSubjects.map((s) => (
            <div
              key={s.id}
              className="p-4 rounded-xl glass-panel hover:border-brand-500/40 transition-all space-y-3 relative overflow-hidden"
            >
              <div
                className="absolute top-0 left-0 bottom-0 w-1"
                style={{ backgroundColor: s.color_code || "#6366f1" }}
              />
              <div className="flex items-start justify-between pl-2">
                <div>
                  <h4 className="font-bold text-white text-sm">{s.name}</h4>
                  <span className="text-[11px] text-slate-400 font-mono">{s.code}</span>
                </div>
                {s.is_lab && (
                  <span className="text-[10px] px-2 py-0.5 rounded bg-emerald-500/15 text-emerald-300 border border-emerald-500/30 flex items-center gap-1">
                    <FlaskConical className="w-3 h-3" /> Lab Block
                  </span>
                )}
              </div>

              <div className="grid grid-cols-2 gap-2 text-xs py-2 border-t border-slate-800 pl-2">
                <div>
                  <span className="text-[10px] text-slate-500 block">Weekly Demand</span>
                  <span className="font-semibold text-white">{s.weekly_hours} periods/wk</span>
                </div>
                <div>
                  <span className="text-[10px] text-slate-500 block">Consecutive Block</span>
                  <span className="font-semibold text-brand-300">{s.consecutive_periods} periods</span>
                </div>
              </div>

              <div className="text-[11px] text-slate-400 pl-2">
                Preferred Venue: <span className="text-slate-300">{s.preferred_room_type}</span>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Tab 4: Classes & Cohorts */}
      {activeTab === "CLASSES" && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {classes.map((c) => (
            <div key={c.id} className="p-4 rounded-xl glass-panel space-y-3">
              <div className="flex items-center justify-between">
                <h4 className="font-bold text-white text-sm">{c.name}</h4>
                <span className="text-xs text-brand-300 font-mono">{c.code}</span>
              </div>
              <div className="space-y-2 pt-2 border-t border-slate-800">
                <span className="text-[11px] text-slate-400 block font-medium">
                  Active Divisions / Sections ({c.divisions.length}):
                </span>
                <div className="grid grid-cols-2 gap-2">
                  {c.divisions.map((d) => (
                    <div
                      key={d.id}
                      className="p-2.5 rounded-lg bg-slate-900 border border-slate-800 text-xs flex items-center justify-between"
                    >
                      <span className="font-medium text-slate-200">{d.name}</span>
                      <span className="text-[11px] text-slate-400">{d.student_count} students</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
