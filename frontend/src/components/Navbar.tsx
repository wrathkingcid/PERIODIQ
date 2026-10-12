import React from "react";
import { Institution, TimetableScenario } from "../services/api";
import { 
  Calendar, 
  Sparkles, 
  Download, 
  Printer, 
  UploadCloud, 
  Clock, 
  Layers, 
  CheckCircle2, 
  AlertTriangle,
  Building2,
  GraduationCap,
  Target,
  RefreshCw
} from "lucide-react";

interface NavbarProps {
  institutions: Institution[];
  currentInstitution: Institution | null;
  onSelectInstitution: (inst: Institution) => void;
  activeScenario: TimetableScenario | null;
  activeTab: string;
  onSelectTab: (tab: string) => void;
  onOpenGenerateModal: () => void;
  onOpenUploadWizard: () => void;
  onExportExcel: () => void;
  onPrint: () => void;
  onSeedSample: (type: string) => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  institutions,
  currentInstitution,
  onSelectInstitution,
  activeScenario,
  activeTab,
  onSelectTab,
  onOpenGenerateModal,
  onOpenUploadWizard,
  onExportExcel,
  onPrint,
  onSeedSample,
}) => {
  const getInstTypeBadge = (type: string) => {
    switch (type) {
      case "SCHOOL":
        return <span className="inline-flex items-center gap-1 text-xs px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"><Building2 className="w-3 h-3" /> High School</span>;
      case "COLLEGE":
        return <span className="inline-flex items-center gap-1 text-xs px-2 py-0.5 rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/20"><GraduationCap className="w-3 h-3" /> College/Univ</span>;
      case "COACHING":
        return <span className="inline-flex items-center gap-1 text-xs px-2 py-0.5 rounded-full bg-amber-500/10 text-amber-400 border border-amber-500/20"><Target className="w-3 h-3" /> Coaching Prep</span>;
      default:
        return null;
    }
  };

  return (
    <header className="sticky top-0 z-40 w-full border-b border-slate-800 bg-slate-950/80 backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo & Institution Selector */}
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2.5">
              <div className="h-9 w-9 rounded-xl bg-gradient-to-tr from-brand-600 via-indigo-500 to-accent-teal flex items-center justify-center shadow-glow-indigo">
                <Calendar className="w-5 h-5 text-white" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <span className="font-extrabold text-lg tracking-tight bg-gradient-to-r from-white via-slate-100 to-indigo-200 bg-clip-text text-transparent">
                    PERIODIQ
                  </span>
                  <span className="text-[10px] font-semibold uppercase tracking-wider px-1.5 py-0.5 rounded bg-brand-500/20 text-brand-300 border border-brand-500/30">
                    CP-SAT v1.0
                  </span>
                </div>
                <p className="text-[11px] text-slate-400 hidden sm:block">Universal Timetable Engine</p>
              </div>
            </div>

            {/* Institution Switcher */}
            <div className="relative">
              <select
                className="bg-slate-900 border border-slate-700 hover:border-slate-600 text-slate-200 text-sm rounded-lg px-3 py-1.5 pr-8 focus:ring-2 focus:ring-brand-500 focus:outline-none transition-colors cursor-pointer"
                value={currentInstitution?.id || ""}
                onChange={(e) => {
                  const target = institutions.find((i) => i.id === Number(e.target.value));
                  if (target) onSelectInstitution(target);
                }}
              >
                {institutions.map((inst) => (
                  <option key={inst.id} value={inst.id}>
                    {inst.name} ({inst.type})
                  </option>
                ))}
              </select>
            </div>

            {currentInstitution && (
              <div className="hidden lg:block">
                {getInstTypeBadge(currentInstitution.type)}
              </div>
            )}
          </div>

          {/* Quick Action Buttons */}
          <div className="flex items-center gap-2">
            {/* Status indicator */}
            {activeScenario && (
              <div className="hidden md:flex items-center gap-2 px-2.5 py-1 rounded-lg bg-slate-900/80 border border-slate-800 text-xs">
                {activeScenario.status === "OPTIMAL" || activeScenario.status === "FEASIBLE" ? (
                  <span className="flex items-center gap-1.5 text-emerald-400 font-medium">
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    {activeScenario.status} ({activeScenario.quality_score}%)
                  </span>
                ) : activeScenario.status === "INFEASIBLE" ? (
                  <span className="flex items-center gap-1.5 text-rose-400 font-medium">
                    <AlertTriangle className="w-3.5 h-3.5" />
                    Infeasible Demands
                  </span>
                ) : (
                  <span className="text-slate-400">{activeScenario.status}</span>
                )}
              </div>
            )}

            <button
              onClick={onOpenGenerateModal}
              className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg bg-brand-600 hover:bg-brand-500 text-white font-medium text-xs sm:text-sm shadow-glow-indigo transition-all transform hover:-translate-y-0.5 active:translate-y-0"
              title="Run Google OR-Tools CP-SAT Timetable Optimizer"
            >
              <Sparkles className="w-4 h-4" />
              <span>Generate</span>
            </button>

            <button
              onClick={onOpenUploadWizard}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-900 hover:bg-slate-800 border border-slate-700 text-slate-200 text-xs sm:text-sm transition-colors"
              title="Upload syllabus or faculty list"
            >
              <UploadCloud className="w-4 h-4 text-brand-400" />
              <span className="hidden sm:inline">Ingest</span>
            </button>

            <button
              onClick={onExportExcel}
              disabled={!activeScenario || activeScenario.status === "INFEASIBLE"}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-900 hover:bg-slate-800 border border-slate-700 text-slate-200 text-xs sm:text-sm transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
              title="Download formatted Excel timetable"
            >
              <Download className="w-4 h-4 text-emerald-400" />
              <span className="hidden md:inline">Excel</span>
            </button>

            <button
              onClick={onPrint}
              disabled={!activeScenario || activeScenario.status === "INFEASIBLE"}
              className="p-1.5 rounded-lg bg-slate-900 hover:bg-slate-800 border border-slate-700 text-slate-300 hover:text-white transition-colors disabled:opacity-40"
              title="Print Timetable"
            >
              <Printer className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav className="flex space-x-1 sm:space-x-3 overflow-x-auto py-2 border-t border-slate-800/80 no-scrollbar">
          {[
            { id: "studio", label: "Timetable Studio", icon: Calendar },
            { id: "shifts", label: "Shift Planning", icon: Clock },
            { id: "ingestion", label: "Document Ingestion", icon: UploadCloud },
            { id: "resources", label: "Academic Catalog", icon: Layers },
            { id: "analytics", label: "Workload & Analytics", icon: CheckCircle2 },
          ].map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => onSelectTab(tab.id)}
                className={`flex items-center gap-2 px-3 py-1.5 rounded-md text-xs sm:text-sm font-medium whitespace-nowrap transition-all ${
                  isActive
                    ? "bg-brand-500/15 text-brand-300 border border-brand-500/30"
                    : "text-slate-400 hover:text-slate-200 hover:bg-slate-900/60"
                }`}
              >
                <Icon className={`w-3.5 h-3.5 ${isActive ? "text-brand-400" : "text-slate-400"}`} />
                {tab.label}
              </button>
            );
          })}
        </nav>
      </div>
    </header>
  );
};
