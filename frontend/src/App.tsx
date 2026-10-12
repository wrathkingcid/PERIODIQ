import React, { useState, useEffect } from "react";
import { 
  Institution, 
  TimetableScenario, 
  TimetableEntry, 
  AcademicData, 
  api 
} from "./services/api";
import { Navbar } from "./components/Navbar";
import { TimetableGrid } from "./components/TimetableGrid";
import { ShiftPlannerStudio } from "./components/ShiftPlannerStudio";
import { IngestionWizard } from "./components/IngestionWizard";
import { ResourcesView } from "./components/ResourcesView";
import { AnalyticsView } from "./components/AnalyticsView";
import { GenerateModal } from "./components/GenerateModal";
import { InfeasibilityModal } from "./components/InfeasibilityModal";
import { 
  Calendar, 
  Sparkles, 
  Building2, 
  GraduationCap, 
  Target, 
  Layers, 
  CheckCircle2, 
  AlertCircle 
} from "lucide-react";

export function App() {
  const [institutions, setInstitutions] = useState<Institution[]>([]);
  const [currentInstitution, setCurrentInstitution] = useState<Institution | null>(null);
  const [academicData, setAcademicData] = useState<AcademicData | null>(null);
  
  const [scenarios, setScenarios] = useState<TimetableScenario[]>([]);
  const [activeScenario, setActiveScenario] = useState<TimetableScenario | null>(null);
  const [entries, setEntries] = useState<TimetableEntry[]>([]);
  
  const [activeTab, setActiveTab] = useState<string>("studio");
  const [loading, setLoading] = useState<boolean>(true);

  // Modals
  const [isGenerateModalOpen, setIsGenerateModalOpen] = useState(false);
  const [isInfeasibilityModalOpen, setIsInfeasibilityModalOpen] = useState(false);
  const [infeasibilityReport, setInfeasibilityReport] = useState<any>(null);

  // Initial load
  useEffect(() => {
    loadInstitutions();
  }, []);

  // When current institution changes, load its academic data & scenarios
  useEffect(() => {
    if (currentInstitution) {
      loadInstitutionDetails(currentInstitution.id);
    }
  }, [currentInstitution?.id]);

  const loadInstitutions = async () => {
    setLoading(true);
    try {
      const insts = await api.getInstitutions();
      setInstitutions(insts);
      if (insts.length > 0) {
        setCurrentInstitution(insts[0]);
      }
    } catch (err) {
      console.error("Failed to load institutions", err);
    } finally {
      setLoading(false);
    }
  };

  const loadInstitutionDetails = async (instId: number) => {
    try {
      const [acad, scens] = await Promise.all([
        api.getAcademicData(instId),
        api.getScenarios(instId),
      ]);
      setAcademicData(acad);
      setScenarios(scens);

      if (scens.length > 0) {
        const topScen = scens[0];
        setActiveScenario(topScen);
        if (topScen.status !== "INFEASIBLE") {
          const detail = await api.getScenario(topScen.id);
          setEntries(detail.entries);
        } else {
          setEntries([]);
          setInfeasibilityReport(topScen.infeasibility_report);
        }
      } else {
        // No scenarios yet, generate initial optimal schedule automatically!
        setActiveScenario(null);
        setEntries([]);
      }
    } catch (err) {
      console.error("Failed to load institution details", err);
    }
  };

  const handleRefreshScenario = async () => {
    if (!activeScenario) return;
    try {
      const detail = await api.getScenario(activeScenario.id);
      setActiveScenario(detail.scenario);
      setEntries(detail.entries);
    } catch (err) {
      console.error("Refresh error", err);
    }
  };

  const handleSelectInstitution = (inst: Institution) => {
    setCurrentInstitution(inst);
  };

  const handleGenerateSuccess = async (scenario: any) => {
    if (currentInstitution) {
      await loadInstitutionDetails(currentInstitution.id);
    }
  };

  const handleInfeasible = (report: any) => {
    setInfeasibilityReport(report);
    setIsInfeasibilityModalOpen(true);
  };

  const handleExportExcel = () => {
    if (activeScenario) {
      window.open(api.getExcelDownloadUrl(activeScenario.id), "_blank");
    }
  };

  const handlePrint = () => {
    window.print();
  };

  const handleSeedSample = async (type: string) => {
    try {
      await api.seedSamples(type);
      await loadInstitutions();
    } catch (err) {
      console.error("Seed error", err);
    }
  };

  if (loading || !currentInstitution) {
    return (
      <div className="min-h-screen bg-slate-950 flex flex-col items-center justify-center text-slate-300">
        <div className="h-12 w-12 rounded-2xl bg-brand-600/20 border border-brand-500/40 flex items-center justify-center text-brand-400 mb-4 animate-pulse">
          <Calendar className="w-6 h-6" />
        </div>
        <h2 className="text-lg font-bold text-white">Loading PERIODIQ Timetable Engine...</h2>
        <p className="text-xs text-slate-500 mt-1">Connecting to OR-Tools CP-SAT Backend</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      {/* Navbar Header */}
      <Navbar
        institutions={institutions}
        currentInstitution={currentInstitution}
        onSelectInstitution={handleSelectInstitution}
        activeScenario={activeScenario}
        activeTab={activeTab}
        onSelectTab={setActiveTab}
        onOpenGenerateModal={() => setIsGenerateModalOpen(true)}
        onOpenUploadWizard={() => setActiveTab("ingestion")}
        onExportExcel={handleExportExcel}
        onPrint={handlePrint}
        onSeedSample={handleSeedSample}
      />

      {/* Main Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
        {/* Sample Switcher Quick Chips for instant live evaluation */}
        <div className="flex flex-wrap items-center justify-between gap-3 p-3 rounded-xl bg-slate-900/40 border border-slate-800/80 text-xs no-print">
          <div className="flex items-center gap-2 text-slate-400">
            <span className="font-semibold text-slate-300">Sample Institutions:</span>
            <span className="hidden sm:inline">Explore pre-configured academic profiles:</span>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            {institutions.map((inst) => (
              <button
                key={inst.id}
                onClick={() => handleSelectInstitution(inst)}
                className={`px-3 py-1 rounded-lg text-xs font-medium transition-all flex items-center gap-1.5 ${
                  currentInstitution.id === inst.id
                    ? "bg-brand-600 text-white shadow-glow-indigo"
                    : "bg-slate-800/80 hover:bg-slate-800 text-slate-300 border border-slate-700/60"
                }`}
              >
                {inst.type === "SCHOOL" && <Building2 className="w-3 h-3 text-emerald-400" />}
                {inst.type === "COLLEGE" && <GraduationCap className="w-3 h-3 text-indigo-400" />}
                {inst.type === "COACHING" && <Target className="w-3 h-3 text-amber-400" />}
                <span>{inst.name.split(" ")[0]}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Tab 1: Timetable Studio */}
        {activeTab === "studio" && academicData && (
          <div>
            {!activeScenario ? (
              <div className="p-12 text-center rounded-2xl glass-panel space-y-4">
                <div className="h-16 w-16 rounded-2xl bg-brand-600/10 border border-brand-500/25 flex items-center justify-center text-brand-400 mx-auto">
                  <Sparkles className="w-8 h-8" />
                </div>
                <div>
                  <h3 className="text-base font-bold text-white">No Timetable Generated Yet</h3>
                  <p className="text-xs text-slate-400 max-w-md mx-auto mt-1">
                    Click Generate to run Google OR-Tools CP-SAT and produce a conflict-free master schedule for {currentInstitution.name}.
                  </p>
                </div>
                <button
                  onClick={() => setIsGenerateModalOpen(true)}
                  className="px-5 py-2.5 rounded-xl bg-brand-600 hover:bg-brand-500 text-white font-semibold text-xs shadow-glow-indigo transition-all"
                >
                  Generate Timetable Now
                </button>
              </div>
            ) : (
              <TimetableGrid
                institution={currentInstitution}
                scenario={activeScenario}
                entries={entries}
                academicData={academicData}
                onRefreshScenario={handleRefreshScenario}
                onOpenInfeasibilityModal={() => setIsInfeasibilityModalOpen(true)}
              />
            )}
          </div>
        )}

        {/* Tab 2: Shift Planning & Capacity Studio */}
        {activeTab === "shifts" && (
          <ShiftPlannerStudio
            institution={currentInstitution}
            onUpdateInstitution={(updated) => {
              setCurrentInstitution(updated);
              loadInstitutions();
            }}
          />
        )}

        {/* Tab 3: Document Ingestion Wizard */}
        {activeTab === "ingestion" && (
          <IngestionWizard
            institution={currentInstitution}
            onIngestSuccess={() => {
              loadInstitutionDetails(currentInstitution.id);
              setActiveTab("resources");
            }}
          />
        )}

        {/* Tab 4: Academic Resources Catalog */}
        {activeTab === "resources" && academicData && (
          <ResourcesView
            institution={currentInstitution}
            academicData={academicData}
          />
        )}

        {/* Tab 5: Workload Analytics & Audit */}
        {activeTab === "analytics" && (
          <AnalyticsView
            institution={currentInstitution}
            scenarios={scenarios}
          />
        )}
      </main>

      {/* Modals */}
      <GenerateModal
        institution={currentInstitution}
        isOpen={isGenerateModalOpen}
        onClose={() => setIsGenerateModalOpen(false)}
        onSuccess={handleGenerateSuccess}
        onInfeasible={handleInfeasible}
      />

      <InfeasibilityModal
        report={infeasibilityReport}
        isOpen={isInfeasibilityModalOpen}
        onClose={() => setIsInfeasibilityModalOpen(false)}
        onNavigateToShifts={() => setActiveTab("shifts")}
      />
    </div>
  );
}

export default App;
