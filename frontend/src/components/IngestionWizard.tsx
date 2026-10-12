import React, { useState } from "react";
import { Institution, api } from "../services/api";
import { 
  UploadCloud, 
  FileText, 
  CheckCircle2, 
  AlertTriangle, 
  HelpCircle, 
  ArrowRight, 
  BookOpen, 
  Users, 
  Building2, 
  Save,
  Sparkles,
  Layers
} from "lucide-react";

interface IngestionWizardProps {
  institution: Institution;
  onIngestSuccess: () => void;
}

export const IngestionWizard: React.FC<IngestionWizardProps> = ({
  institution,
  onIngestSuccess,
}) => {
  const [file, setFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [extractedResult, setExtractedResult] = useState<any>(null);
  const [activePreviewTab, setActivePreviewTab] = useState<"SUBJECTS" | "TEACHERS" | "ROOMS">("SUBJECTS");
  const [clarificationAnswers, setClarificationAnswers] = useState<Record<string, string>>({});
  const [isCommitting, setIsCommitting] = useState(false);
  const [commitSuccess, setCommitSuccess] = useState(false);

  // File input change
  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selected = e.target.files[0];
      setFile(selected);
      await processUpload(selected);
    }
  };

  const processUpload = async (fileToUpload: File) => {
    setIsUploading(true);
    setCommitSuccess(false);
    try {
      const res = await api.uploadDocument(institution.id, fileToUpload);
      setExtractedResult(res.extracted);
    } catch (err: any) {
      alert("Failed to parse file: " + err.message);
    } finally {
      setIsUploading(false);
    }
  };

  // Demo sample loader for quick test
  const handleLoadDemoSyllabus = async () => {
    // Generate synthetic Excel / CSV payload to parse
    const demoCsv = `Subject,Code,Hours,Type,Teacher,Room,Capacity
Advanced Calculus,MTH-301,4,Theory,Dr. Alan Turing,LH-101,60
Data Structures,CS-302,3,Theory,Prof. Donald Knuth,LH-102,60
Data Structures Lab,CS-302L,2,Lab,Prof. Donald Knuth,COMP-LAB,45
Digital Electronics,EC-303,3,Theory,Dr. Claude Shannon,LH-101,60
Digital Electronics Lab,EC-303L,2,Lab,Dr. Claude Shannon,HARDWARE-LAB,40
Database Systems,CS-304,3,Theory,Prof. Grace Hopper,LH-102,60
Database Systems Lab,CS-304L,2,Lab,Prof. Grace Hopper,COMP-LAB,45`;

    const blob = new Blob([demoCsv], { type: "text/csv" });
    const demoFile = new File([blob], "engineering_curriculum.csv");
    setFile(demoFile);
    await processUpload(demoFile);
  };

  const handleCommit = async () => {
    if (!extractedResult) return;
    setIsCommitting(true);
    try {
      await api.commitIngest(institution.id, extractedResult.data);
      setCommitSuccess(true);
      onIngestSuccess();
      setTimeout(() => setCommitSuccess(false), 4000);
    } catch (err: any) {
      alert("Failed to commit data: " + err.message);
    } finally {
      setIsCommitting(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="p-5 rounded-xl glass-panel">
        <h3 className="text-base font-bold text-white flex items-center gap-2">
          <UploadCloud className="w-5 h-5 text-brand-400" />
          <span>Intelligent Curriculum & Faculty Ingestion Wizard</span>
        </h3>
        <p className="text-xs text-slate-300 mt-1 max-w-3xl leading-relaxed">
          Upload curriculum syllabi, faculty directories, classroom capacity schedules, or institutional calendars in Excel (.xlsx), CSV, or PDF format. PERIODIQ automatically extracts subjects, weekly periods, practical lab blocks, qualified teachers, and room parameters.
        </p>
      </div>

      {/* Upload Dropzone */}
      <div className="border-2 border-dashed border-slate-700/80 hover:border-brand-500/60 rounded-xl p-8 text-center transition-all glass-panel">
        <input
          type="file"
          id="file-upload"
          accept=".xlsx,.xls,.csv,.pdf"
          onChange={handleFileSelect}
          className="hidden"
        />
        <label
          htmlFor="file-upload"
          className="cursor-pointer flex flex-col items-center justify-center space-y-3"
        >
          <div className="h-12 w-12 rounded-full bg-brand-500/10 border border-brand-500/25 flex items-center justify-center text-brand-400">
            {isUploading ? (
              <UploadCloud className="w-6 h-6 animate-pulse" />
            ) : (
              <FileText className="w-6 h-6" />
            )}
          </div>
          <div>
            <span className="text-sm font-semibold text-brand-300 hover:text-brand-200 underline">
              {file ? file.name : "Click to select a file"}
            </span>{" "}
            <span className="text-slate-400 text-sm">or drag and drop here</span>
            <p className="text-[11px] text-slate-500 mt-1">
              Supports Excel (.xlsx, .xls), CSV, or PDF Academic Timetable Documents
            </p>
          </div>
        </label>

        <div className="mt-4 pt-4 border-t border-slate-800/80 flex items-center justify-center gap-3">
          <span className="text-xs text-slate-400">Want to test right away?</span>
          <button
            onClick={handleLoadDemoSyllabus}
            className="px-3 py-1.5 rounded-lg bg-slate-900 hover:bg-slate-800 border border-slate-700 text-brand-300 text-xs font-medium transition-colors flex items-center gap-1.5"
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>Load Demo Curriculum Sample</span>
          </button>
        </div>
      </div>

      {/* Extracted Data Review Screen */}
      {extractedResult && (
        <div className="space-y-6">
          {/* Extracted Counters */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <div className="p-3 rounded-lg glass-panel flex items-center gap-3">
              <BookOpen className="w-6 h-6 text-brand-400" />
              <div>
                <span className="text-lg font-bold text-white block">
                  {extractedResult.counts.subjects}
                </span>
                <span className="text-[11px] text-slate-400">Subjects Identified</span>
              </div>
            </div>

            <div className="p-3 rounded-lg glass-panel flex items-center gap-3">
              <Users className="w-6 h-6 text-emerald-400" />
              <div>
                <span className="text-lg font-bold text-white block">
                  {extractedResult.counts.teachers}
                </span>
                <span className="text-[11px] text-slate-400">Faculty Members</span>
              </div>
            </div>

            <div className="p-3 rounded-lg glass-panel flex items-center gap-3">
              <Building2 className="w-6 h-6 text-accent-teal" />
              <div>
                <span className="text-lg font-bold text-white block">
                  {extractedResult.counts.rooms}
                </span>
                <span className="text-[11px] text-slate-400">Rooms & Labs</span>
              </div>
            </div>

            <div className="p-3 rounded-lg glass-panel flex items-center gap-3">
              <Layers className="w-6 h-6 text-purple-400" />
              <div>
                <span className="text-lg font-bold text-white block">
                  {extractedResult.counts.divisions}
                </span>
                <span className="text-[11px] text-slate-400">Classes & Divisions</span>
              </div>
            </div>
          </div>

          {/* Warnings & Contradictions */}
          {extractedResult.warnings?.length > 0 && (
            <div className="p-4 rounded-xl bg-amber-500/10 border border-amber-500/30 space-y-2">
              <div className="flex items-center gap-2 text-amber-300 font-semibold text-xs">
                <AlertTriangle className="w-4 h-4 text-amber-400" />
                <span>Detected Inconsistencies & Flags ({extractedResult.warnings.length})</span>
              </div>
              <div className="space-y-1.5 pl-6">
                {extractedResult.warnings.map((w: any, idx: number) => (
                  <p key={idx} className="text-xs text-amber-200/90">
                    <span className="font-semibold text-amber-300">{w.entity}:</span> {w.message}
                  </p>
                ))}
              </div>
            </div>
          )}

          {/* Minimal Clarification Questions */}
          {extractedResult.clarification_questions?.length > 0 && (
            <div className="p-4 rounded-xl bg-slate-900 border border-slate-700/80 space-y-3">
              <div className="flex items-center gap-2 text-brand-300 font-semibold text-xs">
                <HelpCircle className="w-4 h-4 text-brand-400" />
                <span>Essential Clarifications Required from Administrator</span>
              </div>
              <div className="space-y-3">
                {extractedResult.clarification_questions.map((q: any) => (
                  <div key={q.id} className="p-3 rounded-lg bg-slate-950/60 border border-slate-800 text-xs">
                    <p className="text-slate-200 font-medium mb-2">{q.question}</p>
                    <div className="flex flex-wrap gap-2">
                      {q.options.map((opt: string) => {
                        const isChosen = clarificationAnswers[q.id] === opt;
                        return (
                          <button
                            key={opt}
                            onClick={() =>
                              setClarificationAnswers((prev) => ({ ...prev, [q.id]: opt }))
                            }
                            className={`px-3 py-1.5 rounded-md text-xs font-medium transition-all ${
                              isChosen
                                ? "bg-brand-600 text-white"
                                : "bg-slate-800 text-slate-300 hover:bg-slate-700"
                            }`}
                          >
                            {opt}
                          </button>
                        );
                      })}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Editable Preview Tables */}
          <div className="glass-panel rounded-xl overflow-hidden border border-slate-800">
            <div className="flex border-b border-slate-800 bg-slate-900/60 px-4 pt-2 gap-2">
              <button
                onClick={() => setActivePreviewTab("SUBJECTS")}
                className={`px-3 py-2 text-xs font-semibold border-b-2 transition-all ${
                  activePreviewTab === "SUBJECTS"
                    ? "border-brand-500 text-brand-300"
                    : "border-transparent text-slate-400 hover:text-slate-200"
                }`}
              >
                Extracted Subjects ({extractedResult.data.subjects?.length})
              </button>
              <button
                onClick={() => setActivePreviewTab("TEACHERS")}
                className={`px-3 py-2 text-xs font-semibold border-b-2 transition-all ${
                  activePreviewTab === "TEACHERS"
                    ? "border-brand-500 text-brand-300"
                    : "border-transparent text-slate-400 hover:text-slate-200"
                }`}
              >
                Extracted Faculty ({extractedResult.data.teachers?.length})
              </button>
              <button
                onClick={() => setActivePreviewTab("ROOMS")}
                className={`px-3 py-2 text-xs font-semibold border-b-2 transition-all ${
                  activePreviewTab === "ROOMS"
                    ? "border-brand-500 text-brand-300"
                    : "border-transparent text-slate-400 hover:text-slate-200"
                }`}
              >
                Extracted Rooms ({extractedResult.data.rooms?.length})
              </button>
            </div>

            <div className="p-4 max-h-72 overflow-y-auto">
              {activePreviewTab === "SUBJECTS" && (
                <table className="w-full text-left text-xs text-slate-300">
                  <thead className="text-slate-500 uppercase border-b border-slate-800 text-[10px]">
                    <tr>
                      <th className="pb-2">Name</th>
                      <th className="pb-2">Code</th>
                      <th className="pb-2">Weekly Hours</th>
                      <th className="pb-2">Type</th>
                      <th className="pb-2">Preferred Venue</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60">
                    {extractedResult.data.subjects?.map((s: any, idx: number) => (
                      <tr key={idx} className="hover:bg-slate-900/40">
                        <td className="py-2 font-medium text-white">{s.name}</td>
                        <td className="py-2 font-mono text-slate-400">{s.code}</td>
                        <td className="py-2">{s.weekly_hours} hrs/wk</td>
                        <td className="py-2">
                          {s.is_lab ? (
                            <span className="text-emerald-400 bg-emerald-500/10 px-1.5 py-0.5 rounded text-[10px]">
                              Practical Lab ({s.consecutive_periods} periods block)
                            </span>
                          ) : (
                            <span className="text-slate-400">Theory Lecture</span>
                          )}
                        </td>
                        <td className="py-2 text-slate-400">{s.preferred_room_type}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}

              {activePreviewTab === "TEACHERS" && (
                <table className="w-full text-left text-xs text-slate-300">
                  <thead className="text-slate-500 uppercase border-b border-slate-800 text-[10px]">
                    <tr>
                      <th className="pb-2">Name</th>
                      <th className="pb-2">Code</th>
                      <th className="pb-2">Max Workload</th>
                      <th className="pb-2">Email</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60">
                    {extractedResult.data.teachers?.map((t: any, idx: number) => (
                      <tr key={idx} className="hover:bg-slate-900/40">
                        <td className="py-2 font-medium text-white">{t.name}</td>
                        <td className="py-2 font-mono text-slate-400">{t.code}</td>
                        <td className="py-2">{t.max_hours_per_week} hrs/wk</td>
                        <td className="py-2 text-slate-400">{t.email || "—"}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}

              {activePreviewTab === "ROOMS" && (
                <table className="w-full text-left text-xs text-slate-300">
                  <thead className="text-slate-500 uppercase border-b border-slate-800 text-[10px]">
                    <tr>
                      <th className="pb-2">Room / Lab</th>
                      <th className="pb-2">Type</th>
                      <th className="pb-2">Capacity</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60">
                    {extractedResult.data.rooms?.map((r: any, idx: number) => (
                      <tr key={idx} className="hover:bg-slate-900/40">
                        <td className="py-2 font-medium text-white">{r.name}</td>
                        <td className="py-2 text-brand-300">{r.room_type}</td>
                        <td className="py-2">{r.capacity} seats</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
          </div>

          {/* Commit Button */}
          <div className="flex items-center justify-end gap-3 pt-2">
            <button
              onClick={handleCommit}
              disabled={isCommitting}
              className="px-5 py-2.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-xs sm:text-sm flex items-center gap-2 shadow-lg transition-all"
            >
              <Save className="w-4 h-4" />
              <span>{isCommitting ? "Committing Catalog..." : "Commit & Save to Institutional Catalog"}</span>
            </button>
          </div>

          {commitSuccess && (
            <div className="p-3 rounded-lg bg-emerald-500/20 border border-emerald-500/40 text-emerald-300 text-xs text-center font-medium">
              ✓ Successfully committed all extracted subjects, teachers, and rooms to the institution database!
            </div>
          )}
        </div>
      )}
    </div>
  );
};
