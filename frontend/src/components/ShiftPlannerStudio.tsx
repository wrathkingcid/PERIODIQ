import React, { useState, useEffect } from "react";
import { Institution, api } from "../services/api";
import { 
  Clock, 
  CheckCircle2, 
  AlertTriangle, 
  Users, 
  Building2, 
  TrendingUp, 
  DollarSign, 
  ArrowRight,
  ShieldAlert,
  Sparkles,
  Layers
} from "lucide-react";

interface ShiftPlannerStudioProps {
  institution: Institution;
  onUpdateInstitution: (updated: Institution) => void;
}

export const ShiftPlannerStudio: React.FC<ShiftPlannerStudioProps> = ({
  institution,
  onUpdateInstitution,
}) => {
  const [analysis, setAnalysis] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [selectedScenarioId, setSelectedScenarioId] = useState<string>("single_shift");
  const [isApplying, setIsApplying] = useState(false);
  const [applySuccess, setApplySuccess] = useState(false);

  useEffect(() => {
    loadAnalysis();
  }, [institution.id]);

  const loadAnalysis = async () => {
    setLoading(true);
    try {
      const data = await api.analyzeShifts(institution.id);
      setAnalysis(data);
      if (data?.recommended_scenario_id) {
        setSelectedScenarioId(data.recommended_scenario_id);
      }
    } catch (err) {
      console.error("Shift analysis error", err);
    } finally {
      setLoading(false);
    }
  };

  const handleApplyShift = async (scenario: any) => {
    setIsApplying(true);
    try {
      const updated = await api.updateInstitution(institution.id, {
        shifts: scenario.shifts,
      });
      onUpdateInstitution(updated);
      setApplySuccess(true);
      setTimeout(() => setApplySuccess(false), 3000);
    } catch (err) {
      console.error("Apply shift error", err);
    } finally {
      setIsApplying(false);
    }
  };

  if (loading || !analysis) {
    return (
      <div className="p-12 text-center text-slate-400 glass-panel rounded-xl">
        <Clock className="w-8 h-8 animate-spin mx-auto text-brand-400 mb-3" />
        <p className="text-sm">Evaluating institutional capacity & shift alternatives...</p>
      </div>
    );
  }

  const { summary, deficits, recommendation_reason, scenarios } = analysis;

  return (
    <div className="space-y-6">
      {/* Overview Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="p-4 rounded-xl glass-panel">
          <div className="flex items-center justify-between text-slate-400 text-xs">
            <span>Weekly Curriculum Demand</span>
            <Layers className="w-4 h-4 text-brand-400" />
          </div>
          <div className="text-2xl font-bold text-white mt-2">
            {summary.total_weekly_demand_periods}{" "}
            <span className="text-xs font-normal text-slate-400">periods/wk</span>
          </div>
          <div className="text-xs text-slate-400 mt-1">
            Across {summary.total_divisions} active class divisions
          </div>
        </div>

        <div className="p-4 rounded-xl glass-panel">
          <div className="flex items-center justify-between text-slate-400 text-xs">
            <span>Faculty Capacity</span>
            <Users className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-2xl font-bold text-emerald-400 mt-2">
            {summary.total_faculty_capacity_periods}{" "}
            <span className="text-xs font-normal text-slate-400">hrs/wk max</span>
          </div>
          <div className="text-xs text-slate-400 mt-1">
            {summary.total_teachers} active instructors
          </div>
        </div>

        <div className="p-4 rounded-xl glass-panel">
          <div className="flex items-center justify-between text-slate-400 text-xs">
            <span>Classrooms vs Divisions</span>
            <Building2 className="w-4 h-4 text-accent-teal" />
          </div>
          <div className="text-2xl font-bold text-white mt-2">
            {summary.total_classrooms}{" "}
            <span className="text-xs font-normal text-slate-400">rooms</span> /{" "}
            <span className="text-brand-300">{summary.total_divisions}</span> divs
          </div>
          <div className="text-xs text-slate-400 mt-1">
            {summary.total_classrooms >= summary.total_divisions
              ? "✓ Sufficient concurrent rooms"
              : "⚠️ Room bottleneck in single shift"}
          </div>
        </div>

        <div className="p-4 rounded-xl glass-panel">
          <div className="flex items-center justify-between text-slate-400 text-xs">
            <span>Recommended Mode</span>
            <Sparkles className="w-4 h-4 text-amber-400" />
          </div>
          <div className="text-lg font-bold text-amber-300 mt-2 capitalize">
            {analysis.recommended_scenario_id.replace("_", " ")}
          </div>
          <div className="text-xs text-slate-400 mt-1 line-clamp-1">
            {summary.single_shift_feasible ? "Single shift feasible" : "Multi-shift required"}
          </div>
        </div>
      </div>

      {/* Fundamental Deficits Notice */}
      {deficits && deficits.length > 0 && (
        <div className="space-y-3">
          {deficits.map((d: any, idx: number) => (
            <div
              key={idx}
              className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 flex items-start gap-3"
            >
              <ShieldAlert className="w-5 h-5 text-rose-400 mt-0.5 shrink-0" />
              <div>
                <h4 className="text-sm font-semibold text-rose-300">{d.type}</h4>
                <p className="text-xs text-rose-200/90 mt-0.5">{d.message}</p>
                <p className="text-xs text-rose-400 font-medium mt-1">Recommendation: {d.solution}</p>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Engine Recommendation Banner */}
      <div className="p-4 rounded-xl bg-brand-500/10 border border-brand-500/25 flex items-start gap-3">
        <Sparkles className="w-5 h-5 text-brand-400 mt-0.5 shrink-0" />
        <div className="flex-1">
          <h4 className="text-sm font-semibold text-brand-300">Intelligent Capacity Evaluation</h4>
          <p className="text-xs text-slate-300 mt-0.5 leading-relaxed">{recommendation_reason}</p>
        </div>
      </div>

      {/* Scenarios Comparison Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {scenarios.map((sc: any) => {
          const isSelected = selectedScenarioId === sc.id;
          const isRecommended = analysis.recommended_scenario_id === sc.id;

          return (
            <div
              key={sc.id}
              onClick={() => setSelectedScenarioId(sc.id)}
              className={`p-5 rounded-xl border transition-all cursor-pointer flex flex-col justify-between ${
                isSelected
                  ? "bg-slate-900/90 border-brand-500 ring-1 ring-brand-500 shadow-glow-indigo"
                  : "glass-panel hover:border-slate-700"
              }`}
            >
              <div>
                {/* Header */}
                <div className="flex items-center justify-between mb-3">
                  <h3 className="font-bold text-white text-sm">{sc.name}</h3>
                  {isRecommended && (
                    <span className="text-[10px] font-semibold uppercase px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                      Recommended
                    </span>
                  )}
                </div>

                {/* Feasibility pill */}
                <div className="mb-4">
                  {sc.is_feasible ? (
                    <span className="inline-flex items-center gap-1 text-xs text-emerald-400 font-medium">
                      <CheckCircle2 className="w-3.5 h-3.5" /> Feasible Arrangement
                    </span>
                  ) : (
                    <span className="inline-flex items-center gap-1 text-xs text-rose-400 font-medium">
                      <AlertTriangle className="w-3.5 h-3.5" /> Room Deficit Constraint
                    </span>
                  )}
                </div>

                {/* Shifts Timings Schedule */}
                <div className="space-y-2 mb-4">
                  {sc.shifts.map((s: any, sIdx: number) => (
                    <div
                      key={sIdx}
                      className="p-2.5 rounded-lg bg-slate-950/60 border border-slate-800 text-xs"
                    >
                      <div className="font-semibold text-slate-200 flex items-center justify-between">
                        <span>{s.name}</span>
                        <span className="text-[11px] text-brand-300 font-mono">
                          {s.start_time} - {s.end_time}
                        </span>
                      </div>
                      <div className="text-[10px] text-slate-400 mt-1">
                        {s.periods} periods • {s.target_divisions}
                      </div>
                    </div>
                  ))}
                </div>

                {/* Metrics Breakdown */}
                <div className="grid grid-cols-2 gap-2 text-xs py-2 border-t border-b border-slate-800 mb-4">
                  <div>
                    <span className="text-slate-400 block text-[10px]">Room Utilization</span>
                    <span className="font-semibold text-white">
                      {sc.metrics.room_utilization_pct}%
                    </span>
                  </div>
                  <div>
                    <span className="text-slate-400 block text-[10px]">Operating Cost</span>
                    <span className="font-semibold text-slate-300">
                      {sc.metrics.operating_cost_index}
                    </span>
                  </div>
                  <div>
                    <span className="text-slate-400 block text-[10px]">Faculty Convenience</span>
                    <span className="font-semibold text-emerald-400">
                      {sc.metrics.faculty_convenience_score}%
                    </span>
                  </div>
                  <div>
                    <span className="text-slate-400 block text-[10px]">Student Convenience</span>
                    <span className="font-semibold text-accent-teal">
                      {sc.metrics.student_convenience_score}%
                    </span>
                  </div>
                </div>

                {/* Pros and Cons */}
                <div className="space-y-2 text-xs">
                  <div>
                    <span className="text-[11px] font-semibold text-emerald-400">Advantages:</span>
                    <ul className="list-disc list-inside text-slate-300 space-y-0.5 text-[11px] mt-0.5">
                      {sc.pros.map((p: string, pIdx: number) => (
                        <li key={pIdx}>{p}</li>
                      ))}
                    </ul>
                  </div>
                  {sc.cons.length > 0 && (
                    <div className="mt-2">
                      <span className="text-[11px] font-semibold text-amber-400">Trade-offs:</span>
                      <ul className="list-disc list-inside text-slate-400 space-y-0.5 text-[11px] mt-0.5">
                        {sc.cons.map((c: string, cIdx: number) => (
                          <li key={cIdx}>{c}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </div>

              {/* Action Button */}
              <div className="mt-5 pt-3 border-t border-slate-800">
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    handleApplyShift(sc);
                  }}
                  disabled={isApplying}
                  className="w-full py-2 px-3 rounded-lg bg-brand-600 hover:bg-brand-500 disabled:opacity-50 text-white font-medium text-xs flex items-center justify-center gap-1.5 transition-colors"
                >
                  <Clock className="w-3.5 h-3.5" />
                  <span>Apply This Shift Layout</span>
                </button>
              </div>
            </div>
          );
        })}
      </div>

      {applySuccess && (
        <div className="p-3 rounded-lg bg-emerald-500/20 border border-emerald-500/40 text-emerald-300 text-xs text-center font-medium">
          ✓ Shift schedule successfully applied to institution profile!
        </div>
      )}
    </div>
  );
};
