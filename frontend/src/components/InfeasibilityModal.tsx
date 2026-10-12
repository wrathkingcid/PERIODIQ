import React from "react";
import { 
  AlertTriangle, 
  X, 
  Lightbulb, 
  Clock, 
  Users, 
  Building2, 
  ShieldAlert,
  ArrowRight
} from "lucide-react";

interface InfeasibilityModalProps {
  report: any;
  isOpen: boolean;
  onClose: () => void;
  onNavigateToShifts: () => void;
}

export const InfeasibilityModal: React.FC<InfeasibilityModalProps> = ({
  report,
  isOpen,
  onClose,
  onNavigateToShifts,
}) => {
  if (!isOpen || !report) return null;

  const { diagnostics, recommendations, possible_solutions } = report;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
      <div className="bg-slate-900 border border-rose-500/50 rounded-2xl w-full max-w-2xl overflow-hidden shadow-2xl animate-in fade-in zoom-in-95 duration-200">
        {/* Header */}
        <div className="p-5 border-b border-slate-800 flex items-center justify-between bg-rose-500/10">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-xl bg-rose-500/20 border border-rose-500/40 flex items-center justify-center text-rose-400">
              <ShieldAlert className="w-6 h-6" />
            </div>
            <div>
              <h3 className="font-bold text-white text-base">Infeasible Timetable Requirements</h3>
              <p className="text-xs text-rose-300">
                Diagnostic Analysis & Conflict Resolution Guidance
              </p>
            </div>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-white transition-colors">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-5 max-h-[75vh] overflow-y-auto text-xs text-slate-300">
          <p className="text-slate-300 leading-relaxed">
            Google OR-Tools CP-SAT proved that no mathematically conflict-free timetable can exist under the current constraints. PERIODIQ has analyzed your institutional structure and identified the following specific root bottlenecks:
          </p>

          {/* Diagnostics Cards */}
          <div className="space-y-3">
            <h4 className="font-bold text-white text-xs uppercase tracking-wider flex items-center gap-1.5">
              <AlertTriangle className="w-4 h-4 text-rose-400" />
              <span>Identified Bottlenecks ({diagnostics?.length || 0})</span>
            </h4>

            {diagnostics?.map((diag: any, idx: number) => (
              <div
                key={idx}
                className="p-3.5 rounded-xl bg-slate-950/70 border border-slate-800 space-y-2"
              >
                <div className="flex items-center justify-between">
                  <span className="font-bold text-rose-300 text-xs">{diag.entity}</span>
                  <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-rose-500/15 text-rose-400 border border-rose-500/30">
                    {diag.category}
                  </span>
                </div>
                <p className="text-xs text-slate-300 leading-relaxed">{diag.message}</p>
                {diag.demanded !== null && diag.available !== null && (
                  <div className="flex items-center gap-4 text-[11px] pt-1 border-t border-slate-800/80">
                    <span className="text-rose-400">
                      Demanded: <strong className="font-semibold">{diag.demanded}</strong>
                    </span>
                    <span className="text-emerald-400">
                      Available: <strong className="font-semibold">{diag.available}</strong>
                    </span>
                  </div>
                )}
              </div>
            ))}
          </div>

          {/* Actionable Recommendations */}
          {recommendations?.length > 0 && (
            <div className="space-y-2 pt-2">
              <h4 className="font-bold text-amber-300 text-xs uppercase tracking-wider flex items-center gap-1.5">
                <Lightbulb className="w-4 h-4 text-amber-400" />
                <span>Recommended Fixes</span>
              </h4>
              <ul className="space-y-1.5 pl-1">
                {recommendations.map((rec: string, idx: number) => (
                  <li key={idx} className="flex items-start gap-2 text-xs text-slate-200">
                    <span className="text-amber-400 font-bold">•</span>
                    <span>{rec}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* General solutions */}
          {possible_solutions?.length > 0 && (
            <div className="p-3.5 rounded-xl bg-slate-950/40 border border-slate-800 text-slate-400 space-y-1.5">
              <span className="font-semibold text-slate-300 block text-[11px]">Next Steps:</span>
              <ul className="list-disc list-inside space-y-1 text-[11px]">
                {possible_solutions.map((sol: string, idx: number) => (
                  <li key={idx}>{sol}</li>
                ))}
              </ul>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-4 bg-slate-950/80 border-t border-slate-800 flex items-center justify-between">
          <button
            onClick={() => {
              onClose();
              onNavigateToShifts();
            }}
            className="px-4 py-2 rounded-lg bg-brand-600/30 hover:bg-brand-600/50 border border-brand-500/40 text-brand-300 text-xs font-semibold flex items-center gap-1.5 transition-colors"
          >
            <span>Open Shift Planning Studio</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>

          <button
            onClick={onClose}
            className="px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-white text-xs font-medium transition-colors"
          >
            Dismiss
          </button>
        </div>
      </div>
    </div>
  );
};
