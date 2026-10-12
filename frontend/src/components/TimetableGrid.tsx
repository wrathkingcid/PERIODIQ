import React, { useState } from "react";
import { 
  Institution, 
  TimetableScenario, 
  TimetableEntry, 
  AcademicData, 
  api 
} from "../services/api";
import { 
  Lock, 
  Unlock, 
  Move, 
  AlertCircle, 
  Sparkles, 
  Filter, 
  Layers, 
  User, 
  MapPin, 
  Clock,
  FlaskConical,
  CheckCircle2,
  AlertTriangle
} from "lucide-react";

interface TimetableGridProps {
  institution: Institution;
  scenario: TimetableScenario | null;
  entries: TimetableEntry[];
  academicData: AcademicData;
  onRefreshScenario: () => void;
  onOpenInfeasibilityModal: () => void;
}

export const TimetableGrid: React.FC<TimetableGridProps> = ({
  institution,
  scenario,
  entries,
  academicData,
  onRefreshScenario,
  onOpenInfeasibilityModal
}) => {
  const [viewMode, setViewMode] = useState<"DIVISION" | "TEACHER" | "ROOM">("DIVISION");
  const [selectedDivisionId, setSelectedDivisionId] = useState<number | null>(
    academicData.classes[0]?.divisions[0]?.id || null
  );
  const [selectedTeacherId, setSelectedTeacherId] = useState<number | null>(
    academicData.teachers[0]?.id || null
  );
  const [selectedRoomId, setSelectedRoomId] = useState<number | null>(
    academicData.rooms[0]?.id || null
  );

  // Drag / Swap State
  const [movingEntry, setMovingEntry] = useState<TimetableEntry | null>(null);
  const [swapConflictError, setSwapConflictError] = useState<string | null>(null);
  const [isSwapping, setIsSwapping] = useState(false);

  // Lookup maps
  const subjectMap = new Map(academicData.subjects.map((s) => [s.id, s]));
  const teacherMap = new Map(academicData.teachers.map((t) => [t.id, t]));
  const roomMap = new Map(academicData.rooms.map((r) => [r.id, r]));
  const divisionList = academicData.classes.flatMap((c) =>
    c.divisions.map((d) => ({ ...d, className: c.name }))
  );
  const divisionMap = new Map(divisionList.map((d) => [d.id, d]));

  // Auto pick first division if not selected
  React.useEffect(() => {
    if (!selectedDivisionId && divisionList.length > 0) {
      setSelectedDivisionId(divisionList[0].id);
    }
  }, [divisionList, selectedDivisionId]);

  // Filter entries based on viewMode
  const filteredEntries = entries.filter((e) => {
    if (viewMode === "DIVISION") return e.division_id === selectedDivisionId;
    if (viewMode === "TEACHER") return e.teacher_id === selectedTeacherId;
    if (viewMode === "ROOM") return e.room_id === selectedRoomId;
    return true;
  });

  // Build grid map: key = `${day_index}-${slot_index}`
  const gridMap = new Map<string, TimetableEntry>();
  filteredEntries.forEach((e) => {
    gridMap.set(`${e.day_index}-${e.slot_index}`, e);
  });

  const days = institution.working_days || ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"];
  const periodsCount = institution.periods_per_day || 7;
  const breaks = institution.breaks || [];

  // Toggle lock handler
  const handleToggleLock = async (entry: TimetableEntry, e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      await api.toggleLock(entry.id);
      onRefreshScenario();
    } catch (err) {
      console.error("Lock error", err);
    }
  };

  // Move / Swap target click
  const handleSlotClick = async (dayIndex: number, slotIndex: number) => {
    if (!movingEntry) return;

    if (movingEntry.day_index === dayIndex && movingEntry.slot_index === slotIndex) {
      setMovingEntry(null);
      return;
    }

    setIsSwapping(true);
    setSwapConflictError(null);

    try {
      const res = await api.swapEntry(movingEntry.id, {
        target_day_index: dayIndex,
        target_slot_index: slotIndex,
      });

      if (res.has_conflicts) {
        setSwapConflictError(res.conflicts.join(" "));
      } else {
        setMovingEntry(null);
        onRefreshScenario();
      }
    } catch (err: any) {
      setSwapConflictError("Failed to move session. Check server constraints.");
    } finally {
      setIsSwapping(false);
    }
  };

  // Helper to compute slot time label
  const getSlotTiming = (slotIndex: number) => {
    const [h, m] = institution.day_start_time.split(":").map(Number);
    const duration = institution.period_duration_minutes;
    // Simple start time calc
    let totalMin = h * 60 + m + slotIndex * duration;
    // Add breaks duration if passed
    breaks.forEach((b) => {
      if (slotIndex >= b.after_period) {
        totalMin += b.duration_minutes;
      }
    });
    const startH = Math.floor(totalMin / 60) % 24;
    const startM = totalMin % 60;
    const endMin = totalMin + duration;
    const endH = Math.floor(endMin / 60) % 24;
    const endM = endMin % 60;

    const pad = (n: number) => (n < 10 ? `0${n}` : n);
    return `${pad(startH)}:${pad(startM)} - ${pad(endH)}:${pad(endM)}`;
  };

  return (
    <div className="space-y-4">
      {/* Infeasibility Banner if unsolvable */}
      {scenario?.status === "INFEASIBLE" && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 flex items-start justify-between gap-4">
          <div className="flex items-start gap-3">
            <AlertTriangle className="w-5 h-5 text-rose-400 mt-0.5 shrink-0" />
            <div>
              <h4 className="text-sm font-semibold text-rose-300">
                Timetable Requirements Are Infeasible
              </h4>
              <p className="text-xs text-rose-200/80 mt-1">
                The constraint solver determined that the current combination of teacher workloads, classroom counts, or weekly hours cannot be satisfied without conflicts.
              </p>
            </div>
          </div>
          <button
            onClick={onOpenInfeasibilityModal}
            className="px-3 py-1.5 rounded-lg bg-rose-600 hover:bg-rose-500 text-white text-xs font-medium shrink-0 transition-colors"
          >
            Diagnose & Fix
          </button>
        </div>
      )}

      {/* Header Controls & Quality Metrics */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 p-4 rounded-xl glass-panel">
        {/* Left: View Filter Mode */}
        <div className="flex flex-wrap items-center gap-3">
          <div className="flex rounded-lg bg-slate-900 p-1 border border-slate-800">
            <button
              onClick={() => setViewMode("DIVISION")}
              className={`px-3 py-1 text-xs font-medium rounded-md transition-all ${
                viewMode === "DIVISION"
                  ? "bg-brand-600 text-white shadow"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              Class / Section
            </button>
            <button
              onClick={() => setViewMode("TEACHER")}
              className={`px-3 py-1 text-xs font-medium rounded-md transition-all ${
                viewMode === "TEACHER"
                  ? "bg-brand-600 text-white shadow"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              Faculty View
            </button>
            <button
              onClick={() => setViewMode("ROOM")}
              className={`px-3 py-1 text-xs font-medium rounded-md transition-all ${
                viewMode === "ROOM"
                  ? "bg-brand-600 text-white shadow"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              Room / Lab
            </button>
          </div>

          {/* Context Dropdown */}
          {viewMode === "DIVISION" && (
            <select
              className="bg-slate-900 border border-slate-700 text-slate-200 text-xs rounded-lg px-3 py-1.5 focus:ring-1 focus:ring-brand-500 outline-none"
              value={selectedDivisionId || ""}
              onChange={(e) => setSelectedDivisionId(Number(e.target.value))}
            >
              {divisionList.map((d) => (
                <option key={d.id} value={d.id}>
                  {d.className} — {d.name} ({d.student_count} students)
                </option>
              ))}
            </select>
          )}

          {viewMode === "TEACHER" && (
            <select
              className="bg-slate-900 border border-slate-700 text-slate-200 text-xs rounded-lg px-3 py-1.5 focus:ring-1 focus:ring-brand-500 outline-none"
              value={selectedTeacherId || ""}
              onChange={(e) => setSelectedTeacherId(Number(e.target.value))}
            >
              {academicData.teachers.map((t) => (
                <option key={t.id} value={t.id}>
                  {t.name} ({t.designation})
                </option>
              ))}
            </select>
          )}

          {viewMode === "ROOM" && (
            <select
              className="bg-slate-900 border border-slate-700 text-slate-200 text-xs rounded-lg px-3 py-1.5 focus:ring-1 focus:ring-brand-500 outline-none"
              value={selectedRoomId || ""}
              onChange={(e) => setSelectedRoomId(Number(e.target.value))}
            >
              {academicData.rooms.map((r) => (
                <option key={r.id} value={r.id}>
                  {r.name} ({r.room_type} • Cap: {r.capacity})
                </option>
              ))}
            </select>
          )}

          {movingEntry && (
            <div className="flex items-center gap-2 px-2.5 py-1 rounded bg-amber-500/10 border border-amber-500/30 text-amber-300 text-xs">
              <span>Moving session. Click target slot to place.</span>
              <button
                onClick={() => setMovingEntry(null)}
                className="text-amber-200 underline hover:text-white"
              >
                Cancel
              </button>
            </div>
          )}
        </div>

        {/* Right: Quality & Analytics Metrics */}
        {scenario && scenario.status !== "INFEASIBLE" && (
          <div className="flex items-center gap-4 text-xs">
            <div className="flex items-center gap-2">
              <span className="text-slate-400">Score:</span>
              <span className="font-bold text-brand-300 bg-brand-500/15 px-2 py-0.5 rounded border border-brand-500/30">
                {scenario.quality_score}%
              </span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-slate-400">Room Utilization:</span>
              <span className="font-semibold text-emerald-400">
                {scenario.metrics?.room_utilization_pct || 0}%
              </span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-slate-400">Teacher Gaps:</span>
              <span className="font-semibold text-slate-200">
                {scenario.metrics?.teacher_idle_gaps || 0}
              </span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-slate-400">Solver Time:</span>
              <span className="font-semibold text-slate-200">
                {scenario.solver_time_seconds || 0}s
              </span>
            </div>
          </div>
        )}
      </div>

      {/* Conflict error banner if manual swap causes double-booking */}
      {swapConflictError && (
        <div className="p-3 rounded-lg bg-rose-500/20 border border-rose-500/40 text-rose-300 text-xs flex items-center justify-between">
          <div className="flex items-center gap-2">
            <AlertCircle className="w-4 h-4 text-rose-400" />
            <span>Conflict Detected: {swapConflictError}</span>
          </div>
          <button
            onClick={() => setSwapConflictError(null)}
            className="text-rose-200 hover:text-white font-bold"
          >
            ✕
          </button>
        </div>
      )}

      {/* Timetable Weekly Matrix Table */}
      <div className="overflow-x-auto rounded-xl border border-slate-800 glass-panel shadow-2xl">
        <table className="w-full text-left border-collapse min-w-[850px]">
          <thead>
            <tr className="border-b border-slate-800 bg-slate-900/90 text-slate-300 text-xs">
              <th className="p-3 w-28 text-center font-semibold uppercase tracking-wider text-slate-400">
                Day
              </th>
              {Array.from({ length: periodsCount }).map((_, pIdx) => {
                const isBreakAfter = breaks.find((b) => b.after_period === pIdx + 1);
                return (
                  <React.Fragment key={pIdx}>
                    <th className="p-3 text-center border-l border-slate-800/60 font-semibold min-w-[140px]">
                      <div>Period {pIdx + 1}</div>
                      <div className="text-[10px] text-slate-500 font-normal mt-0.5">
                        {getSlotTiming(pIdx)}
                      </div>
                    </th>
                    {isBreakAfter && (
                      <th className="p-2 w-10 text-center bg-slate-950/80 border-l border-slate-800 text-[10px] uppercase text-slate-500 font-bold writing-mode-vertical">
                        {isBreakAfter.name}
                      </th>
                    )}
                  </React.Fragment>
                );
              })}
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60 text-xs">
            {days.map((dayName, dIdx) => (
              <tr key={dayName} className="hover:bg-slate-900/30 transition-colors">
                {/* Day Header Cell */}
                <td className="p-3 text-center font-bold text-brand-300 bg-slate-900/50 border-r border-slate-800">
                  {dayName}
                </td>

                {/* Period Slot Cells */}
                {Array.from({ length: periodsCount }).map((_, pIdx) => {
                  const entry = gridMap.get(`${dIdx}-${pIdx}`);
                  const isBreakAfter = breaks.find((b) => b.after_period === pIdx + 1);
                  const isMovingTarget = movingEntry !== null;

                  return (
                    <React.Fragment key={pIdx}>
                      <td
                        onClick={() => isMovingTarget && handleSlotClick(dIdx, pIdx)}
                        className={`p-2 border-l border-slate-800/60 h-28 align-top transition-all ${
                          isMovingTarget
                            ? "cursor-pointer hover:bg-brand-500/10 hover:border-brand-500/40"
                            : ""
                        } ${
                          movingEntry?.id === entry?.id
                            ? "ring-2 ring-amber-400 bg-amber-500/10"
                            : ""
                        }`}
                      >
                        {entry ? (
                          <div className="h-full flex flex-col justify-between p-2 rounded-lg bg-slate-900/90 border border-slate-700/60 hover:border-brand-500/50 hover:shadow-md transition-all group relative">
                            {/* Accent indicator bar */}
                            <div
                              className="absolute left-0 top-0 bottom-0 w-1 rounded-l-lg"
                              style={{
                                backgroundColor:
                                  subjectMap.get(entry.subject_id)?.color_code || "#6366f1",
                              }}
                            />

                            {/* Top row: Subject Code & Action Buttons */}
                            <div className="flex items-start justify-between gap-1 pl-1">
                              <div>
                                <span className="font-bold text-slate-100 text-xs leading-tight block">
                                  {subjectMap.get(entry.subject_id)?.name || "Subject"}
                                </span>
                                <span className="text-[10px] text-slate-400 font-mono">
                                  {subjectMap.get(entry.subject_id)?.code}
                                </span>
                              </div>

                              <div className="flex items-center gap-1 opacity-70 group-hover:opacity-100 transition-opacity">
                                <button
                                  onClick={(e) => handleToggleLock(entry, e)}
                                  className={`p-1 rounded hover:bg-slate-800 transition-colors ${
                                    entry.is_locked ? "text-amber-400" : "text-slate-500"
                                  }`}
                                  title={entry.is_locked ? "Locked period (Pinned)" : "Lock this slot"}
                                >
                                  {entry.is_locked ? (
                                    <Lock className="w-3 h-3" />
                                  ) : (
                                    <Unlock className="w-3 h-3" />
                                  )}
                                </button>
                                <button
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    setMovingEntry(entry);
                                  }}
                                  className="p-1 rounded hover:bg-slate-800 text-slate-500 hover:text-brand-300 transition-colors"
                                  title="Move / Swap session"
                                >
                                  <Move className="w-3 h-3" />
                                </button>
                              </div>
                            </div>

                            {/* Middle / Bottom info */}
                            <div className="mt-2 space-y-1 pl-1 text-[11px]">
                              {/* Teacher info */}
                              <div className="flex items-center gap-1.5 text-slate-300">
                                <User className="w-3 h-3 text-slate-400 shrink-0" />
                                <span className="truncate">
                                  {teacherMap.get(entry.teacher_id)?.name || "Faculty"}
                                </span>
                              </div>

                              {/* Room & Lab info */}
                              <div className="flex items-center justify-between text-slate-400 text-[10px]">
                                <div className="flex items-center gap-1">
                                  <MapPin className="w-2.5 h-2.5 text-slate-500" />
                                  <span>{roomMap.get(entry.room_id)?.name}</span>
                                </div>

                                {subjectMap.get(entry.subject_id)?.is_lab && (
                                  <span className="flex items-center gap-0.5 text-emerald-400 bg-emerald-500/10 px-1 py-0.2 rounded font-medium">
                                    <FlaskConical className="w-2.5 h-2.5" /> Lab
                                  </span>
                                )}
                              </div>
                            </div>
                          </div>
                        ) : (
                          <div className="h-full flex items-center justify-center text-slate-700/50 text-[11px] hover:text-slate-500">
                            {isMovingTarget ? "Click to drop" : "—"}
                          </div>
                        )}
                      </td>

                      {/* Visual Break separator cell */}
                      {isBreakAfter && (
                        <td className="w-8 bg-slate-950/60 border-l border-slate-800 text-center text-slate-600">
                          <span className="text-[9px] font-semibold tracking-widest uppercase writing-vertical">
                            {isBreakAfter.name}
                          </span>
                        </td>
                      )}
                    </React.Fragment>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
