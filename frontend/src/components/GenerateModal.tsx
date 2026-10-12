import React, { useState } from "react";
import { Institution, api } from "../services/api";
import { 
  Sparkles, 
  X, 
  Clock, 
  Sliders, 
  CheckCircle2, 
  Cpu, 
  Layers, 
  ShieldCheck,
  AlertTriangle
} from "lucide-react";

interface GenerateModalProps {
  institution: Institution;
  isOpen: boolean;
  onClose: () => void;
  onSuccess: (scenario: any) => void;
  onInfeasible: (infeasibilityReport: any) => void;
}

export const GenerateModal: React.FC<GenerateModalProps> = ({
  institution,
  isOpen,
  onClose,
  onSuccess,
  onInfeasible,
}) => {
  const [scenarioName, setScenarioName] = useState(
    `${institution.name.split(" ")[0]} Master Schedule`
  );
  const [academicYear, setAcademicYear] = useState("2026-2027");
  const [term, setTerm] = useState("Semester 1");
  const [timeoutSeconds, setTimeoutSeconds] = useState(30);
  const [enableSoftConstraints, setEnableSoftConstraints] = useState(true);
  const [minimizeTeacherGaps, setMinimizeTeacherGaps] = useState(true);
  const [balanceDailySubjects, setBalanceDailySubjects] = useState(true);
  const [respectTeacherPreferences, setRespectTeacherPreferences] = useState(true);

  const [isSolving, setIsSolving] = useState(false);
  const [solvingStep, setSolvingStep] = useState<string>("");

  if (!isOpen) return null;

  const handleGenerate = async () => {
    setIsSolving(true);
    setSolvingStep("Initializing CP-SAT Decision Variables...");

    const stepTimer1 = setTimeout(() => {
      setSolvingStep("Enforcing Teacher, Room, and Division Hard Constraints...");
    }, 1200);

    const stepTimer2 = setTimeout(() => {
      setSolvingStep("Searching Optimal Conflict-Free Solutions & Minimizing Gaps...");
    }, 2800);

    try {
      const res = await api.generateTimetable(institution.id, {
        scenario_name: scenarioName,
        academic_year: academicYear,
        term: term,
        timeout_seconds: timeoutSeconds,
        enable_soft_constraints: enableSoftConstraints,
      });

      clearTimeout(stepTimer1);
      clearTimeout(stepTimer2);

      if (res.result?.status === "INFEASIBLE") {
        onInfeasible(res.result.infeasibility_report);
        onClose();
      } else {
        onSuccess(res.scenario);
        onClose();
      }
    } catch (err: any) {
      alert("Solver error: " + err.message);
    } finally {
      setIsSolving(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
      <div className="bg-slate-900 border border-slate-700/80 rounded-2xl w-full max-w-lg overflow-hidden shadow-2xl animate-in fade-in zoom-in-95 duration-200">
        {/* Header */}
        <div className="p-5 border-b border-slate-800 flex items-center justify-between bg-slate-950/40">
          <div className="flex items-center gap-3">
            <div className="h-9 w-9 rounded-xl bg-brand-600/20 border border-brand-500/30 flex items-center justify-center text-brand-400">
              <Sparkles className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-bold text-white text-base">Generate Optimized Timetable</h3>
              <p className="text-xs text-slate-400">Google OR-Tools CP-SAT Constraint Engine</p>
            </div>
          </div>
          <button
            onClick={onClose}
            disabled={isSolving}
            className="text-slate-400 hover:text-white transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Form Body */}
        <div className="p-6 space-y-5 text-xs text-slate-300">
          {/* Scenario Name */}
          <div className="space-y-1.5">
            <label className="font-medium text-slate-200">Scenario Name</label>
            <input
              type="text"
              value={scenarioName}
              onChange={(e) => setScenarioName(e.target.value)}
              className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-white focus:ring-1 focus:ring-brand-500 outline-none"
              placeholder="e.g., Master Timetable 2026"
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1.5">
              <label className="font-medium text-slate-200">Academic Year</label>
              <input
                type="text"
                value={academicYear}
                onChange={(e) => setAcademicYear(e.target.value)}
                className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-white focus:ring-1 focus:ring-brand-500 outline-none"
              />
            </div>
            <div className="space-y-1.5">
              <label className="font-medium text-slate-200">Academic Term</label>
              <input
                type="text"
                value={term}
                onChange={(e) => setTerm(e.target.value)}
                className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-white focus:ring-1 focus:ring-brand-500 outline-none"
              />
            </div>
          </div>

          {/* Solver Timeout Slider */}
          <div className="space-y-2 pt-2 border-t border-slate-800">
            <div className="flex items-center justify-between">
              <label className="font-medium text-slate-200 flex items-center gap-1.5">
                <Clock className="w-3.5 h-3.5 text-brand-400" />
                <span>Solver Search Timeout</span>
              </label>
              <span className="font-mono text-brand-300 font-bold">{timeoutSeconds} seconds</span>
            </div>
            <input
              type="range"
              min="10"
              max="90"
              step="5"
              value={timeoutSeconds}
              onChange={(e) => setTimeoutSeconds(Number(e.target.value))}
              className="w-full accent-brand-500 cursor-pointer"
            />
            <div className="flex justify-between text-[10px] text-slate-500">
              <span>Fast (10s)</span>
              <span>Balanced (30s)</span>
              <span>Deep Exhaustive (90s)</span>
            </div>
          </div>

          {/* Soft Constraints & Heuristics */}
          <div className="space-y-2.5 pt-2 border-t border-slate-800">
            <span className="font-medium text-slate-200 block">Optimization Priorities:</span>

            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={balanceDailySubjects}
                onChange={(e) => setBalanceDailySubjects(e.target.checked)}
                className="rounded border-slate-700 text-brand-600 focus:ring-brand-500"
              />
              <span>Distribute subjects evenly across days (avoid back-to-back lectures)</span>
            </label>

            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={minimizeTeacherGaps}
                onChange={(e) => setMinimizeTeacherGaps(e.target.checked)}
                className="rounded border-slate-700 text-brand-600 focus:ring-brand-500"
              />
              <span>Minimize idle gap periods in teacher schedules</span>
            </label>

            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={respectTeacherPreferences}
                onChange={(e) => setRespectTeacherPreferences(e.target.checked)}
                className="rounded border-slate-700 text-brand-600 focus:ring-brand-500"
              />
              <span>Reward assignments in faculty preferred teaching windows</span>
            </label>
          </div>

          {/* Solving Progress Animation */}
          {isSolving && (
            <div className="p-4 rounded-xl bg-brand-500/10 border border-brand-500/30 text-center space-y-2">
              <Cpu className="w-6 h-6 animate-spin text-brand-400 mx-auto" />
              <div className="font-semibold text-brand-200 text-xs">
                Google OR-Tools CP-SAT Engine Running...
              </div>
              <p className="text-[11px] text-brand-300/80 animate-pulse">{solvingStep}</p>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-4 bg-slate-950/60 border-t border-slate-800 flex items-center justify-end gap-3">
          <button
            onClick={onClose}
            disabled={isSolving}
            className="px-4 py-2 rounded-lg text-slate-300 hover:text-white text-xs font-medium transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={handleGenerate}
            disabled={isSolving}
            className="px-5 py-2 rounded-lg bg-brand-600 hover:bg-brand-500 text-white text-xs font-bold shadow-glow-indigo transition-all flex items-center gap-2"
          >
            <Sparkles className="w-4 h-4" />
            <span>{isSolving ? "Optimizing..." : "Start Optimization"}</span>
          </button>
        </div>
      </div>
    </div>
  );
};
