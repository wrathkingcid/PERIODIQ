import React, { useState, useEffect } from "react";
import { Institution, TimetableScenario, api } from "../services/api";
import { 
  TrendingUp, 
  Users, 
  Building2, 
  History, 
  GitCompare, 
  CheckCircle2, 
  AlertCircle,
  Clock
} from "lucide-react";

interface AnalyticsViewProps {
  institution: Institution;
  scenarios: TimetableScenario[];
}

export const AnalyticsView: React.FC<AnalyticsViewProps> = ({
  institution,
  scenarios,
}) => {
  const [analytics, setAnalytics] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  // Scenario comparison state
  const [sc1Id, setSc1Id] = useState<number | null>(scenarios[0]?.id || null);
  const [sc2Id, setSc2Id] = useState<number | null>(scenarios[1]?.id || scenarios[0]?.id || null);
  const [comparisonResult, setComparisonResult] = useState<any>(null);

  useEffect(() => {
    loadAnalytics();
  }, [institution.id]);

  useEffect(() => {
    if (sc1Id && sc2Id && sc1Id !== sc2Id) {
      loadComparison();
    }
  }, [sc1Id, sc2Id]);

  const loadAnalytics = async () => {
    setLoading(true);
    try {
      const data = await api.getDashboardAnalytics(institution.id);
      setAnalytics(data);
    } catch (err) {
      console.error("Analytics error", err);
    } finally {
      setLoading(false);
    }
  };

  const loadComparison = async () => {
    if (!sc1Id || !sc2Id) return;
    try {
      const data = await api.compareScenarios(institution.id, sc1Id, sc2Id);
      setComparisonResult(data);
    } catch (err) {
      console.error("Comparison error", err);
    }
  };

  if (loading || !analytics) {
    return (
      <div className="p-12 text-center text-slate-400 glass-panel rounded-xl">
        <TrendingUp className="w-8 h-8 animate-spin mx-auto text-brand-400 mb-3" />
        <p className="text-sm">Calculating institutional workload & utilization analytics...</p>
      </div>
    );
  }

  const { teacher_workloads, room_occupancies, recent_audits } = analytics;

  return (
    <div className="space-y-6">
      {/* Top KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="p-4 rounded-xl glass-panel">
          <div className="flex items-center justify-between text-slate-400 text-xs">
            <span>Faculty Workload Health</span>
            <Users className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-xl font-bold text-white mt-2">
            {teacher_workloads.filter((t: any) => t.status === "BALANCED").length} /{" "}
            {teacher_workloads.length}{" "}
            <span className="text-xs font-normal text-emerald-400">Balanced</span>
          </div>
          <div className="text-xs text-slate-400 mt-1">
            {teacher_workloads.filter((t: any) => t.status === "OVERLOAD").length > 0 ? (
              <span className="text-rose-400">⚠️ Overloaded faculty detected</span>
            ) : (
              <span className="text-emerald-400">✓ No faculty exceeding workload limits</span>
            )}
          </div>
        </div>

        <div className="p-4 rounded-xl glass-panel">
          <div className="flex items-center justify-between text-slate-400 text-xs">
            <span>Average Room Utilization</span>
            <Building2 className="w-4 h-4 text-accent-teal" />
          </div>
          <div className="text-xl font-bold text-white mt-2">
            {room_occupancies.length > 0
              ? Math.round(
                  room_occupancies.reduce((acc: number, r: any) => acc + r.utilization_pct, 0) /
                    room_occupancies.length
                )
              : 0}
            %
          </div>
          <div className="text-xs text-slate-400 mt-1">Across all classrooms & laboratories</div>
        </div>

        <div className="p-4 rounded-xl glass-panel">
          <div className="flex items-center justify-between text-slate-400 text-xs">
            <span>Audit Trail Entries</span>
            <History className="w-4 h-4 text-brand-400" />
          </div>
          <div className="text-xl font-bold text-white mt-2">{recent_audits.length} Events</div>
          <div className="text-xs text-slate-400 mt-1">Tracked institutional operations</div>
        </div>
      </div>

      {/* Scenario Comparison View */}
      {scenarios.length >= 2 && (
        <div className="p-5 rounded-xl glass-panel space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="font-bold text-white text-sm flex items-center gap-2">
              <GitCompare className="w-4 h-4 text-brand-400" />
              <span>Timetable Scenario Comparison</span>
            </h3>
            <span className="text-xs text-slate-400">Compare quality metrics side-by-side</span>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-xs text-slate-400 block mb-1">Scenario A</label>
              <select
                value={sc1Id || ""}
                onChange={(e) => setSc1Id(Number(e.target.value))}
                className="w-full bg-slate-900 border border-slate-700 text-xs text-slate-200 rounded-lg px-3 py-2 outline-none"
              >
                {scenarios.map((s) => (
                  <option key={s.id} value={s.id}>
                    {s.name} ({s.quality_score}%)
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="text-xs text-slate-400 block mb-1">Scenario B</label>
              <select
                value={sc2Id || ""}
                onChange={(e) => setSc2Id(Number(e.target.value))}
                className="w-full bg-slate-900 border border-slate-700 text-xs text-slate-200 rounded-lg px-3 py-2 outline-none"
              >
                {scenarios.map((s) => (
                  <option key={s.id} value={s.id}>
                    {s.name} ({s.quality_score}%)
                  </option>
                ))}
              </select>
            </div>
          </div>

          {comparisonResult && (
            <div className="grid grid-cols-3 gap-3 p-3 rounded-lg bg-slate-950/60 border border-slate-800 text-center text-xs">
              <div>
                <span className="text-[10px] text-slate-500 block uppercase">Quality Score Delta</span>
                <span
                  className={`font-bold text-sm ${
                    comparisonResult.comparison.quality_delta >= 0
                      ? "text-emerald-400"
                      : "text-rose-400"
                  }`}
                >
                  {comparisonResult.comparison.quality_delta > 0 ? "+" : ""}
                  {comparisonResult.comparison.quality_delta}%
                </span>
              </div>
              <div>
                <span className="text-[10px] text-slate-500 block uppercase">Teacher Gaps (A vs B)</span>
                <span className="font-semibold text-slate-200">
                  {comparisonResult.comparison.teacher_gaps_a} vs{" "}
                  {comparisonResult.comparison.teacher_gaps_b}
                </span>
              </div>
              <div>
                <span className="text-[10px] text-slate-500 block uppercase">Room Util (A vs B)</span>
                <span className="font-semibold text-accent-teal">
                  {comparisonResult.comparison.room_util_a}% vs{" "}
                  {comparisonResult.comparison.room_util_b}%
                </span>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Faculty Workload Breakdown */}
      <div className="p-5 rounded-xl glass-panel space-y-4">
        <h3 className="font-bold text-white text-sm flex items-center gap-2">
          <Users className="w-4 h-4 text-emerald-400" />
          <span>Faculty Teaching Hours & Capacity Meter</span>
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 max-h-72 overflow-y-auto pr-1">
          {teacher_workloads.map((t: any) => {
            const isOverload = t.status === "OVERLOAD";
            return (
              <div
                key={t.id}
                className="p-3 rounded-lg bg-slate-900/80 border border-slate-800 text-xs space-y-2"
              >
                <div className="flex items-center justify-between">
                  <span className="font-semibold text-white">{t.name}</span>
                  <span
                    className={`text-[10px] px-1.5 py-0.5 rounded font-medium ${
                      isOverload
                        ? "bg-rose-500/20 text-rose-300"
                        : "bg-emerald-500/20 text-emerald-300"
                    }`}
                  >
                    {t.assigned_hours} / {t.max_hours} hrs
                  </span>
                </div>

                {/* Progress bar */}
                <div className="w-full bg-slate-950 rounded-full h-1.5 overflow-hidden">
                  <div
                    className={`h-full rounded-full ${
                      isOverload ? "bg-rose-500" : "bg-emerald-500"
                    }`}
                    style={{ width: `${Math.min(100, t.utilization_pct)}%` }}
                  />
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Room Occupancy Heatmap */}
      <div className="p-5 rounded-xl glass-panel space-y-4">
        <h3 className="font-bold text-white text-sm flex items-center gap-2">
          <Building2 className="w-4 h-4 text-accent-teal" />
          <span>Room & Laboratory Utilization Rates</span>
        </h3>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
          {room_occupancies.map((r: any) => (
            <div
              key={r.id}
              className="p-3 rounded-lg bg-slate-900/80 border border-slate-800 text-xs space-y-2"
            >
              <div className="flex items-center justify-between">
                <div>
                  <span className="font-semibold text-white block">{r.name}</span>
                  <span className="text-[10px] text-slate-400">{r.type}</span>
                </div>
                <span className="font-bold text-accent-teal text-sm">{r.utilization_pct}%</span>
              </div>
              <div className="text-[10px] text-slate-500">
                Occupied: {r.occupied_slots} / {r.total_slots} available slots
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Audit Logs */}
      <div className="p-5 rounded-xl glass-panel space-y-3">
        <h3 className="font-bold text-white text-sm flex items-center gap-2">
          <History className="w-4 h-4 text-brand-400" />
          <span>Institutional Change & Generation Audit Trail</span>
        </h3>

        <div className="space-y-2 max-h-48 overflow-y-auto">
          {recent_audits.map((a: any) => (
            <div
              key={a.id}
              className="p-2.5 rounded-lg bg-slate-950/60 border border-slate-800/80 text-xs flex items-center justify-between gap-4"
            >
              <div className="flex items-center gap-2">
                <span className="font-mono text-[10px] uppercase px-1.5 py-0.5 rounded bg-brand-500/20 text-brand-300">
                  {a.action}
                </span>
                <span className="text-slate-300">{a.details}</span>
              </div>
              <span className="text-[10px] text-slate-500 shrink-0">
                {new Date(a.created_at).toLocaleTimeString([], {
                  hour: "2-digit",
                  minute: "2-digit",
                })}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
