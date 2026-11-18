"use client";

import { useEffect, useState } from "react";
import {
  api,
  VaultData,
  JDAnalysis,
  JDScore,
  RefractionResult,
  ResumeData,
  GapProject,
  MockInterview,
} from "@/lib/api";
import {
  Layers,
  Sparkles,
  FileText,
  Target,
  Download,
  CheckCircle,
  AlertCircle,
  RefreshCw,
  MessageSquare,
  Code,
  Plus,
  Pencil,
  Trash2,
  X,
  Palette,
  Briefcase,
  Check,
} from "lucide-react";

const LENSES = [
  { id: "platform", name: "Platform Engineering", desc: "Scalability, API architecture, developer experience" },
  { id: "infrastructure", name: "Infrastructure / DevOps", desc: "Cloud architecture, CI/CD, reliability, SRE" },
  { id: "leadership", name: "Team Leadership", desc: "Mentorship, cross-functional collaboration, ownership" },
  { id: "business_impact", name: "Business Impact", desc: "Revenue, cost reduction, efficiency, measurable ROI" },
  { id: "data_engineering", name: "Data Engineering", desc: "Pipelines, data modeling, ETL, streaming" },
  { id: "security", name: "Security & Compliance", desc: "Access control, hardening, compliance, threat mitigation" },
];

const RESUME_TEMPLATES = [
  { id: "modern", name: "Modern Clean", desc: "Crisp sans-serif, standard ATS format" },
  { id: "classic", name: "Classic Ivy", desc: "Serif typography, Harvard executive styling" },
  { id: "minimal", name: "Tech Minimalist", desc: "High density 1-page layout with mono accents" },
  { id: "executive", name: "Executive Accent", desc: "Deep navy bands and leadership headers" },
];

export default function Home() {
  const [activeTab, setActiveTab] = useState<"vault" | "jd" | "resume" | "gap" | "chat">("vault");
  const [vault, setVault] = useState<VaultData | null>(null);
  const [loadingVault, setLoadingVault] = useState(true);
  const [apiOnline, setApiOnline] = useState<boolean | null>(null);

  // JD Analysis State
  const [jdText, setJdText] = useState("");
  const [analyzingJD, setAnalyzingJD] = useState(false);
  const [jdAnalysis, setJdAnalysis] = useState<JDAnalysis | null>(null);
  const [jdScore, setJdScore] = useState<JDScore | null>(null);

  // Refraction State
  const [selectedLens, setSelectedLens] = useState("platform");
  const [refractingNodeId, setRefractingNodeId] = useState<string | null>(null);
  const [refractions, setRefractions] = useState<Record<string, RefractionResult>>({});

  // Resume State
  const [generatingResume, setGeneratingResume] = useState(false);
  const [currentResume, setCurrentResume] = useState<ResumeData | null>(null);
  const [selectedTemplate, setSelectedTemplate] = useState("modern");
  const [switchingTemplate, setSwitchingTemplate] = useState(false);

  // Vault Editor State
  const [isEditingSummary, setIsEditingSummary] = useState(false);
  const [summaryInput, setSummaryInput] = useState("");

  const [isNodeModalOpen, setIsNodeModalOpen] = useState(false);
  const [editingNodeId, setEditingNodeId] = useState<string | null>(null);
  const [nodeForm, setNodeForm] = useState({
    company: "",
    role: "",
    duration: "",
    raw_text: "",
    tags: "",
  });

  const [isAddingSkill, setIsAddingSkill] = useState(false);
  const [newSkillName, setNewSkillName] = useState("");
  const [newSkillCategory, setNewSkillCategory] = useState("Technical Skills");

  const [isProjectModalOpen, setIsProjectModalOpen] = useState(false);
  const [editingProjectId, setEditingProjectId] = useState<string | null>(null);
  const [projectForm, setProjectForm] = useState({
    name: "",
    description: "",
    tags: "",
  });

  // Gap Project & Interview State
  const [loadingGap, setLoadingGap] = useState(false);
  const [gapProject, setGapProject] = useState<GapProject | null>(null);
  const [loadingInterview, setLoadingInterview] = useState(false);
  const [mockInterview, setMockInterview] = useState<MockInterview | null>(null);

  // Chat State
  const [chatInput, setChatInput] = useState("");
  const [chatMessages, setChatMessages] = useState<Array<{ sender: "user" | "loom"; text: string }>>([
    {
      sender: "loom",
      text: "Hello! I am Loom, your career intelligence engine. Paste a job description, reframe your experience narratives, or architect gap-filler projects.",
    },
  ]);
  const [chatLoading, setChatLoading] = useState(false);

  // Initial data load
  useEffect(() => {
    loadVault();
    checkHealth();
  }, []);

  async function checkHealth() {
    try {
      const h = await api.getHealth();
      setApiOnline(h.status === "ok");
    } catch {
      setApiOnline(false);
    }
  }

  async function loadVault() {
    setLoadingVault(true);
    try {
      const data = await api.getVault();
      setVault(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoadingVault(false);
    }
  }

  async function handleTriggerIngest() {
    try {
      await api.triggerIngest();
      await loadVault();
      alert("Career vault successfully refreshed from master profile!");
    } catch (err: unknown) {
      alert("Ingestion error: " + (err instanceof Error ? err.message : String(err)));
    }
  }

  async function handleAnalyzeJD() {
    if (!jdText.trim() || !vault?.user) return;
    setAnalyzingJD(true);
    try {
      const analysis = await api.analyzeJD(jdText, vault.user.email);
      setJdAnalysis(analysis);

      // Score the match
      const score = await api.getJDScore(analysis.session_id, vault.user.id);
      setJdScore(score);
    } catch (err: unknown) {
      alert("JD analysis error: " + (err instanceof Error ? err.message : String(err)));
    } finally {
      setAnalyzingJD(false);
    }
  }

  async function handleRefract(nodeId: string) {
    if (!vault?.user) return;
    setRefractingNodeId(nodeId);
    try {
      const res = await api.refractNode(nodeId, selectedLens, vault.user.id);
      setRefractions((prev) => ({ ...prev, [nodeId]: res }));
    } catch (err: unknown) {
      alert("Refraction error: " + (err instanceof Error ? err.message : String(err)));
    } finally {
      setRefractingNodeId(null);
    }
  }

  async function handleGenerateResume() {
    if (!vault?.user || !jdAnalysis) {
      alert("Please analyze a job description first.");
      return;
    }
    setGeneratingResume(true);
    try {
      const res = await api.generateResume(
        jdAnalysis.session_id,
        vault.user.id,
        selectedLens,
        selectedTemplate
      );
      setCurrentResume(res);
      setActiveTab("resume");
    } catch (err: unknown) {
      alert("Resume generation error: " + (err instanceof Error ? err.message : String(err)));
    } finally {
      setGeneratingResume(false);
    }
  }

  async function handleSwitchTemplate(templateId: string) {
    setSelectedTemplate(templateId);
    if (!currentResume) return;
    setSwitchingTemplate(true);
    try {
      const res = await api.switchResumeTemplate(currentResume.resume_id, templateId);
      setCurrentResume((prev) => (prev ? { ...prev, final_content: res.final_content } : null));
    } catch (err: unknown) {
      alert("Failed to switch template: " + (err instanceof Error ? err.message : String(err)));
    } finally {
      setSwitchingTemplate(false);
    }
  }

  // Summary Edit
  function handleStartEditSummary() {
    setSummaryInput(vault?.user?.summary || "");
    setIsEditingSummary(true);
  }

  async function handleSaveSummary() {
    try {
      await api.updateProfile({ summary: summaryInput });
      await loadVault();
      setIsEditingSummary(false);
    } catch (err: unknown) {
      alert("Failed to update summary: " + (err instanceof Error ? err.message : String(err)));
    }
  }

  // Experience Node CRUD
  function handleOpenAddNode() {
    setEditingNodeId(null);
    setNodeForm({ company: "", role: "", duration: "", raw_text: "", tags: "" });
    setIsNodeModalOpen(true);
  }

  function handleOpenEditNode(node: any) {
    setEditingNodeId(node.id);
    setNodeForm({
      company: node.company,
      role: node.role,
      duration: node.duration || "",
      raw_text: node.raw_text,
      tags: (node.tags || []).join(", "),
    });
    setIsNodeModalOpen(true);
  }

  async function handleSaveNode() {
    if (!nodeForm.company.trim() || !nodeForm.role.trim() || !nodeForm.raw_text.trim()) {
      alert("Company, Role, and Achievement Bullet Text are required.");
      return;
    }
    const tagsArray = nodeForm.tags.split(",").map((t) => t.trim()).filter(Boolean);
    try {
      if (editingNodeId) {
        await api.updateNode(editingNodeId, {
          company: nodeForm.company,
          role: nodeForm.role,
          duration: nodeForm.duration,
          raw_text: nodeForm.raw_text,
          tags: tagsArray,
        });
      } else {
        await api.createNode({
          company: nodeForm.company,
          role: nodeForm.role,
          duration: nodeForm.duration,
          raw_text: nodeForm.raw_text,
          tags: tagsArray,
        });
      }
      setIsNodeModalOpen(false);
      await loadVault();
    } catch (err: unknown) {
      alert("Failed to save experience node: " + (err instanceof Error ? err.message : String(err)));
    }
  }

  async function handleDeleteNode(nodeId: string) {
    if (!confirm("Are you sure you want to delete this achievement node from the vault?")) return;
    try {
      await api.deleteNode(nodeId);
      await loadVault();
    } catch (err: unknown) {
      alert("Failed to delete experience node: " + (err instanceof Error ? err.message : String(err)));
    }
  }

  // Skills CRUD
  async function handleAddSkill() {
    if (!newSkillName.trim()) return;
    try {
      await api.createSkill({
        skill_name: newSkillName.trim(),
        category: newSkillCategory.trim() || "Technical Skills",
      });
      setNewSkillName("");
      setIsAddingSkill(false);
      await loadVault();
    } catch (err: unknown) {
      alert("Failed to add skill: " + (err instanceof Error ? err.message : String(err)));
    }
  }

  async function handleDeleteSkill(skillId: string) {
    try {
      await api.deleteSkill(skillId);
      await loadVault();
    } catch (err: unknown) {
      alert("Failed to delete skill: " + (err instanceof Error ? err.message : String(err)));
    }
  }

  // Projects CRUD
  function handleOpenAddProject() {
    setEditingProjectId(null);
    setProjectForm({ name: "", description: "", tags: "" });
    setIsProjectModalOpen(true);
  }

  function handleOpenEditProject(project: any) {
    setEditingProjectId(project.id);
    setProjectForm({
      name: project.name,
      description: project.description || "",
      tags: (project.tags || []).join(", "),
    });
    setIsProjectModalOpen(true);
  }

  async function handleSaveProject() {
    if (!projectForm.name.trim() || !projectForm.description.trim()) {
      alert("Project Name and Description are required.");
      return;
    }
    const tagsArray = projectForm.tags.split(",").map((t) => t.trim()).filter(Boolean);
    try {
      if (editingProjectId) {
        await api.updateProject(editingProjectId, {
          name: projectForm.name,
          description: projectForm.description,
          tags: tagsArray,
        });
      } else {
        await api.createProject({
          name: projectForm.name,
          description: projectForm.description,
          tags: tagsArray,
        });
      }
      setIsProjectModalOpen(false);
      await loadVault();
    } catch (err: unknown) {
      alert("Failed to save project: " + (err instanceof Error ? err.message : String(err)));
    }
  }

  async function handleDeleteProject(projectId: string) {
    if (!confirm("Are you sure you want to delete this project?")) return;
    try {
      await api.deleteProject(projectId);
      await loadVault();
    } catch (err: unknown) {
      alert("Failed to delete project: " + (err instanceof Error ? err.message : String(err)));
    }
  }

  async function handleArchitectGap() {
    if (!vault?.user || !jdAnalysis) {
      alert("Please analyze a job description first.");
      return;
    }
    setLoadingGap(true);
    try {
      const res = await api.architectGapProject(jdAnalysis.session_id, vault.user.id);
      setGapProject(res);
    } catch (err: unknown) {
      alert("Project architecting error: " + (err instanceof Error ? err.message : String(err)));
    } finally {
      setLoadingGap(false);
    }
  }

  async function handleGenerateInterview() {
    if (!vault?.user || !jdAnalysis) {
      alert("Please analyze a job description first.");
      return;
    }
    setLoadingInterview(true);
    try {
      const res = await api.generateMockInterview(jdAnalysis.session_id, vault.user.id);
      setMockInterview(res);
    } catch (err: unknown) {
      alert("Mock interview error: " + (err instanceof Error ? err.message : String(err)));
    } finally {
      setLoadingInterview(false);
    }
  }

  async function handleSendMessage() {
    if (!chatInput.trim() || chatLoading) return;
    const msg = chatInput.trim();
    setChatInput("");
    setChatMessages((prev) => [...prev, { sender: "user", text: msg }]);
    setChatLoading(true);
    try {
      const res = await api.chat(msg);
      setChatMessages((prev) => [...prev, { sender: "loom", text: res.response }]);
    } catch (err: unknown) {
      setChatMessages((prev) => [
        ...prev,
        { sender: "loom", text: "Error connecting to Loom AI: " + (err instanceof Error ? err.message : String(err)) },
      ]);
    } finally {
      setChatLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-neutral-950 text-neutral-100 flex flex-col font-sans">
      {/* Top Navbar */}
      <header className="border-b border-neutral-800 bg-neutral-900/60 backdrop-blur px-6 py-4 flex items-center justify-between sticky top-0 z-50">
        <div className="flex items-center gap-3">
          <div className="h-9 w-9 rounded-lg bg-gradient-to-tr from-indigo-500 to-sky-400 flex items-center justify-center font-bold text-black shadow-lg shadow-indigo-500/20">
            LR
          </div>
          <div>
            <h1 className="text-base font-semibold tracking-tight text-white flex items-center gap-2">
              LoomResume
              <span className="text-xs px-2 py-0.5 rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                v0.1.0 Engine
              </span>
            </h1>
            <p className="text-xs text-neutral-400">The Cross-Functional Impact Engine</p>
          </div>
        </div>

        {/* Server & DB Status */}
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 text-xs px-3 py-1.5 rounded-md bg-neutral-900 border border-neutral-800">
            <span
              className={`h-2 w-2 rounded-full ${
                apiOnline ? "bg-emerald-500 animate-pulse" : "bg-rose-500"
              }`}
            />
            <span className="text-neutral-400">
              API & DB: {apiOnline ? "Connected" : "Offline"}
            </span>
          </div>

          <button
            onClick={handleTriggerIngest}
            className="flex items-center gap-2 text-xs font-medium px-3 py-1.5 rounded-md bg-neutral-800 hover:bg-neutral-700 text-neutral-200 transition"
          >
            <RefreshCw className="h-3.5 w-3.5" />
            Re-sync Vault
          </button>
        </div>
      </header>

      {/* Main Layout */}
      <div className="flex flex-1 overflow-hidden">
        {/* Left Sidebar Navigation */}
        <aside className="w-64 border-r border-neutral-800 bg-neutral-900/30 p-4 flex flex-col gap-1 shrink-0">
          <div className="text-xs font-semibold text-neutral-500 px-3 py-2 uppercase tracking-wider">
            Workspace
          </div>

          <button
            onClick={() => setActiveTab("vault")}
            className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition ${
              activeTab === "vault"
                ? "bg-indigo-600/20 text-indigo-300 border border-indigo-500/30"
                : "text-neutral-400 hover:bg-neutral-800/60 hover:text-neutral-200"
            }`}
          >
            <Layers className="h-4 w-4" />
            Experience Vault
          </button>

          <button
            onClick={() => setActiveTab("jd")}
            className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition ${
              activeTab === "jd"
                ? "bg-indigo-600/20 text-indigo-300 border border-indigo-500/30"
                : "text-neutral-400 hover:bg-neutral-800/60 hover:text-neutral-200"
            }`}
          >
            <Target className="h-4 w-4" />
            JD Match & Refract
          </button>

          <button
            onClick={() => setActiveTab("resume")}
            className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition ${
              activeTab === "resume"
                ? "bg-indigo-600/20 text-indigo-300 border border-indigo-500/30"
                : "text-neutral-400 hover:bg-neutral-800/60 hover:text-neutral-200"
            }`}
          >
            <FileText className="h-4 w-4" />
            Resume Studio
          </button>

          <button
            onClick={() => setActiveTab("gap")}
            className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition ${
              activeTab === "gap"
                ? "bg-indigo-600/20 text-indigo-300 border border-indigo-500/30"
                : "text-neutral-400 hover:bg-neutral-800/60 hover:text-neutral-200"
            }`}
          >
            <Sparkles className="h-4 w-4" />
            Gap Projects & Mock
          </button>

          <button
            onClick={() => setActiveTab("chat")}
            className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition ${
              activeTab === "chat"
                ? "bg-indigo-600/20 text-indigo-300 border border-indigo-500/30"
                : "text-neutral-400 hover:bg-neutral-800/60 hover:text-neutral-200"
            }`}
          >
            <MessageSquare className="h-4 w-4" />
            Loom AI Assistant
          </button>

          {/* User Profile Mini Card */}
          {vault?.user && (
            <div className="mt-auto pt-4 border-t border-neutral-800/80">
              <div className="p-3 rounded-lg bg-neutral-900 border border-neutral-800 text-xs">
                <div className="font-semibold text-neutral-200">
                  {vault.user.personal_info.name || "Candidate"}
                </div>
                <div className="text-neutral-400 truncate">{vault.user.email}</div>
                <div className="mt-2 text-indigo-400 font-medium">
                  {vault.nodes.length} Nodes &bull; {vault.skills.length} Skills
                </div>
              </div>
            </div>
          )}
        </aside>

        {/* Center Content Area */}
        <main className="flex-1 overflow-y-auto p-8">
          {/* TAB 1: VAULT */}
          {activeTab === "vault" && (
            <div className="max-w-5xl mx-auto space-y-6">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-xl font-bold text-white">The Experience Vault</h2>
                  <p className="text-sm text-neutral-400">
                    Living database of your raw achievements, project metrics, and technical skills.
                  </p>
                </div>
                <div className="flex items-center gap-3">
                  <div className="text-xs bg-neutral-900 border border-neutral-800 px-3 py-1.5 rounded-lg text-neutral-300">
                    Total Nodes: <span className="text-indigo-400 font-semibold">{vault?.nodes.length || 0}</span>
                  </div>
                  <button
                    onClick={handleOpenAddNode}
                    className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow transition"
                  >
                    <Plus className="h-3.5 w-3.5" />
                    Add Bullet
                  </button>
                </div>
              </div>

              {loadingVault ? (
                <div className="py-20 text-center text-neutral-500">Loading vault records...</div>
              ) : (
                <>
                  {/* Personal Summary Card */}
                  <div className="p-5 rounded-xl bg-neutral-900 border border-neutral-800 space-y-2">
                    <div className="flex items-center justify-between">
                      <div className="text-xs font-semibold text-neutral-400 uppercase tracking-wider">
                        Master Profile Summary
                      </div>
                      {!isEditingSummary && (
                        <button
                          onClick={handleStartEditSummary}
                          className="flex items-center gap-1 text-xs text-neutral-400 hover:text-white transition"
                        >
                          <Pencil className="h-3 w-3" />
                          Edit
                        </button>
                      )}
                    </div>
                    {isEditingSummary ? (
                      <div className="space-y-3 pt-1">
                        <textarea
                          value={summaryInput}
                          onChange={(e) => setSummaryInput(e.target.value)}
                          rows={3}
                          className="w-full rounded-lg bg-neutral-950 border border-neutral-700 p-3 text-xs text-neutral-200 focus:outline-none focus:border-indigo-500"
                        />
                        <div className="flex justify-end gap-2">
                          <button
                            onClick={() => setIsEditingSummary(false)}
                            className="px-3 py-1 rounded text-xs text-neutral-400 hover:text-white"
                          >
                            Cancel
                          </button>
                          <button
                            onClick={handleSaveSummary}
                            className="px-3 py-1 rounded bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium"
                          >
                            Save Summary
                          </button>
                        </div>
                      </div>
                    ) : (
                      <p className="text-sm text-neutral-200 leading-relaxed">
                        {vault?.user?.summary || "No master summary provided yet."}
                      </p>
                    )}
                  </div>

                  {/* Bullet Point Nodes List */}
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <h3 className="text-sm font-semibold text-neutral-300 uppercase tracking-wider">
                        Experience Nodes ({vault?.nodes.length})
                      </h3>
                      <button
                        onClick={handleOpenAddNode}
                        className="flex items-center gap-1 text-xs text-indigo-400 hover:text-indigo-300 font-medium"
                      >
                        <Plus className="h-3.5 w-3.5" /> Add Achievement Bullet
                      </button>
                    </div>
                    <div className="grid gap-3">
                      {vault?.nodes.map((node) => (
                        <div
                          key={node.id}
                          className="p-4 rounded-xl bg-neutral-900/60 border border-neutral-800 hover:border-neutral-700 transition space-y-2"
                        >
                          <div className="flex items-baseline justify-between mb-1">
                            <div className="text-sm font-bold text-white">
                              {node.company}{" "}
                              <span className="font-normal text-neutral-400">&mdash; {node.role}</span>
                            </div>
                            <div className="flex items-center gap-3">
                              <div className="text-xs text-neutral-500 font-mono">{node.duration}</div>
                              <button
                                onClick={() => handleOpenEditNode(node)}
                                title="Edit Bullet"
                                className="text-neutral-500 hover:text-neutral-300 transition"
                              >
                                <Pencil className="h-3.5 w-3.5" />
                              </button>
                              <button
                                onClick={() => handleDeleteNode(node.id)}
                                title="Delete Bullet"
                                className="text-neutral-500 hover:text-rose-400 transition"
                              >
                                <Trash2 className="h-3.5 w-3.5" />
                              </button>
                            </div>
                          </div>
                          <p className="text-sm text-neutral-300 leading-relaxed">{node.raw_text}</p>
                          <div className="flex flex-wrap gap-1.5 pt-1">
                            {node.tags.map((tag, idx) => (
                              <span
                                key={idx}
                                className="text-xs px-2 py-0.5 rounded-md bg-neutral-800 text-neutral-300 border border-neutral-700/50"
                              >
                                {tag}
                              </span>
                            ))}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Key Projects Section */}
                  <div className="space-y-3 pt-4">
                    <div className="flex items-center justify-between">
                      <h3 className="text-sm font-semibold text-neutral-300 uppercase tracking-wider">
                        Key Projects ({vault?.projects.length || 0})
                      </h3>
                      <button
                        onClick={handleOpenAddProject}
                        className="flex items-center gap-1 text-xs text-indigo-400 hover:text-indigo-300 font-medium"
                      >
                        <Plus className="h-3.5 w-3.5" /> Add Project
                      </button>
                    </div>
                    <div className="grid gap-3">
                      {(vault?.projects || []).map((p) => (
                        <div
                          key={p.id}
                          className="p-4 rounded-xl bg-neutral-900/60 border border-neutral-800 hover:border-neutral-700 transition space-y-2"
                        >
                          <div className="flex items-baseline justify-between">
                            <span className="text-sm font-bold text-white">{p.name}</span>
                            <div className="flex items-center gap-3">
                              <button
                                onClick={() => handleOpenEditProject(p)}
                                title="Edit Project"
                                className="text-neutral-500 hover:text-neutral-300 transition"
                              >
                                <Pencil className="h-3.5 w-3.5" />
                              </button>
                              <button
                                onClick={() => handleDeleteProject(p.id)}
                                title="Delete Project"
                                className="text-neutral-500 hover:text-rose-400 transition"
                              >
                                <Trash2 className="h-3.5 w-3.5" />
                              </button>
                            </div>
                          </div>
                          <p className="text-xs text-neutral-300 leading-relaxed">{p.description}</p>
                          <div className="flex flex-wrap gap-1.5">
                            {p.tags.map((tag, idx) => (
                              <span
                                key={idx}
                                className="text-xs px-2 py-0.5 rounded-md bg-neutral-800 text-neutral-400 border border-neutral-700/50"
                              >
                                {tag}
                              </span>
                            ))}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Skills Grid */}
                  <div className="space-y-3 pt-4">
                    <div className="flex items-center justify-between">
                      <h3 className="text-sm font-semibold text-neutral-300 uppercase tracking-wider">
                        Master Skills Profile ({vault?.skills.length})
                      </h3>
                      <button
                        onClick={() => setIsAddingSkill(!isAddingSkill)}
                        className="flex items-center gap-1 text-xs text-indigo-400 hover:text-indigo-300 font-medium"
                      >
                        <Plus className="h-3.5 w-3.5" /> Add Skill
                      </button>
                    </div>

                    {isAddingSkill && (
                      <div className="p-3 rounded-lg bg-neutral-900 border border-neutral-750 flex flex-wrap gap-2 items-center">
                        <input
                          type="text"
                          value={newSkillName}
                          onChange={(e) => setNewSkillName(e.target.value)}
                          placeholder="Skill name (e.g. Rust, Kafka, Kubernetes)..."
                          className="text-xs rounded bg-neutral-950 border border-neutral-700 px-2.5 py-1.5 text-white flex-1 min-w-[150px] focus:outline-none focus:border-indigo-500"
                        />
                        <input
                          type="text"
                          value={newSkillCategory}
                          onChange={(e) => setNewSkillCategory(e.target.value)}
                          placeholder="Category (e.g. Languages, Cloud)..."
                          className="text-xs rounded bg-neutral-950 border border-neutral-700 px-2.5 py-1.5 text-neutral-300 w-44 focus:outline-none focus:border-indigo-500"
                        />
                        <button
                          onClick={handleAddSkill}
                          className="px-3 py-1.5 rounded bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium"
                        >
                          Add
                        </button>
                        <button
                          onClick={() => setIsAddingSkill(false)}
                          className="px-2 py-1.5 text-xs text-neutral-400 hover:text-white"
                        >
                          Cancel
                        </button>
                      </div>
                    )}

                    <div className="flex flex-wrap gap-2">
                      {vault?.skills.map((s) => (
                        <span
                          key={s.id}
                          className="group inline-flex items-center gap-1.5 text-xs px-2.5 py-1 rounded-lg bg-neutral-900 border border-neutral-800 text-indigo-300 font-medium"
                        >
                          {s.skill_name}
                          <button
                            onClick={() => handleDeleteSkill(s.id)}
                            title="Remove Skill"
                            className="text-neutral-500 hover:text-rose-400 transition"
                          >
                            <X className="h-3 w-3" />
                          </button>
                        </span>
                      ))}
                    </div>
                  </div>
                </>
              )}
            </div>
          )}

          {/* TAB 2: JD MATCH & REFRACTION */}
          {activeTab === "jd" && (
            <div className="max-w-5xl mx-auto space-y-8">
              <div>
                <h2 className="text-xl font-bold text-white">JD Contextualization & Role Refraction</h2>
                <p className="text-sm text-neutral-400">
                  Analyze target job descriptions, evaluate hybrid alignment scores, and reframe achievements.
                </p>
              </div>

              {/* JD Input Card */}
              <div className="p-5 rounded-xl bg-neutral-900 border border-neutral-800 space-y-4">
                <label className="block text-xs font-semibold text-neutral-400 uppercase tracking-wider">
                  Target Job Description
                </label>
                <textarea
                  value={jdText}
                  onChange={(e) => setJdText(e.target.value)}
                  placeholder="Paste target Job Description here (responsibilities, technical requirements, keywords)..."
                  rows={6}
                  className="w-full rounded-lg bg-neutral-950 border border-neutral-800 p-3 text-sm text-neutral-200 placeholder-neutral-600 focus:outline-none focus:border-indigo-500 font-mono"
                />
                <div className="flex items-center justify-between">
                  <button
                    onClick={() =>
                      setJdText(
                        `We are looking for a Senior Staff Platform Engineer to scale our distributed cloud systems.
Requirements:
- Deep expertise in AWS, Kubernetes, ECS, and Terraform
- High-throughput messaging with Kafka or SQS
- Python or Go microservices architecture
- Zero-downtime CI/CD and observability (Prometheus, OpenTelemetry)
- Mentorship and cross-functional leadership`
                      )
                    }
                    className="text-xs text-neutral-500 hover:text-neutral-300 underline"
                  >
                    Load Sample Senior Platform JD
                  </button>
                  <button
                    onClick={handleAnalyzeJD}
                    disabled={analyzingJD || !jdText.trim()}
                    className="flex items-center gap-2 px-5 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-medium transition disabled:opacity-50"
                  >
                    {analyzingJD ? (
                      <>
                        <RefreshCw className="h-4 w-4 animate-spin" />
                        Analyzing via LLM & pgvector...
                      </>
                    ) : (
                      <>
                        <Target className="h-4 w-4" />
                        Analyze & Match JD
                      </>
                    )}
                  </button>
                </div>
              </div>

              {/* JD Scoring & Keyword Insights */}
              {jdScore && (
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="p-5 rounded-xl bg-neutral-900 border border-neutral-800 flex flex-col justify-between">
                    <span className="text-xs font-semibold text-neutral-400 uppercase tracking-wider">
                      Overall Match
                    </span>
                    <div className="text-4xl font-extrabold text-white mt-2">
                      {jdScore.overall_score}%
                    </div>
                    <span className="text-xs text-neutral-500 mt-1">
                      Weighted 60% semantic + 40% lexical
                    </span>
                  </div>

                  <div className="p-5 rounded-xl bg-neutral-900 border border-neutral-800 flex flex-col justify-between">
                    <span className="text-xs font-semibold text-neutral-400 uppercase tracking-wider">
                      Semantic Similarity
                    </span>
                    <div className="text-4xl font-extrabold text-sky-400 mt-2">
                      {jdScore.semantic_score}%
                    </div>
                    <span className="text-xs text-neutral-500 mt-1">pgvector HNSW Cosine Overlap</span>
                  </div>

                  <div className="p-5 rounded-xl bg-neutral-900 border border-neutral-800 flex flex-col justify-between">
                    <span className="text-xs font-semibold text-neutral-400 uppercase tracking-wider">
                      ATS Keyword Match
                    </span>
                    <div className="text-4xl font-extrabold text-indigo-400 mt-2">
                      {jdScore.keyword_score}%
                    </div>
                    <span className="text-xs text-neutral-500 mt-1">Exact Tech Token Coverage</span>
                  </div>
                </div>
              )}

              {/* Keyword Gap Breakdown */}
              {jdScore && (
                <div className="p-5 rounded-xl bg-neutral-900 border border-neutral-800 space-y-4">
                  <h3 className="text-sm font-semibold text-white">Keyword Gap Breakdown</h3>
                  <div>
                    <span className="text-xs font-medium text-emerald-400 block mb-2">
                      ✓ Present in Profile ({jdScore.present_keywords.length})
                    </span>
                    <div className="flex flex-wrap gap-1.5">
                      {jdScore.present_keywords.map((k, i) => (
                        <span
                          key={i}
                          className="text-xs px-2 py-0.5 rounded-md bg-emerald-950/60 text-emerald-300 border border-emerald-800/50"
                        >
                          {k}
                        </span>
                      ))}
                    </div>
                  </div>

                  {jdScore.missing_keywords.length > 0 && (
                    <div className="pt-2 border-t border-neutral-800">
                      <span className="text-xs font-medium text-amber-400 block mb-2">
                        ⚠ Missing Gaps ({jdScore.missing_keywords.length})
                      </span>
                      <div className="flex flex-wrap gap-1.5">
                        {jdScore.missing_keywords.map((k, i) => (
                          <span
                            key={i}
                            className="text-xs px-2 py-0.5 rounded-md bg-amber-950/60 text-amber-300 border border-amber-800/50"
                          >
                            {k}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* Lens Selector */}
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <h3 className="text-sm font-semibold text-white">Select Refraction Lens</h3>
                  <button
                    onClick={handleGenerateResume}
                    disabled={!jdAnalysis || generatingResume}
                    className="flex items-center gap-2 px-4 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-medium transition disabled:opacity-50"
                  >
                    <FileText className="h-3.5 w-3.5" />
                    Generate Tailored Resume & PDF
                  </button>
                </div>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                  {LENSES.map((l) => (
                    <button
                      key={l.id}
                      onClick={() => setSelectedLens(l.id)}
                      className={`p-3 rounded-xl border text-left transition ${
                        selectedLens === l.id
                          ? "bg-indigo-600/15 border-indigo-500 text-white"
                          : "bg-neutral-900 border-neutral-800 text-neutral-400 hover:border-neutral-700"
                      }`}
                    >
                      <div className="text-xs font-bold">{l.name}</div>
                      <div className="text-[11px] text-neutral-500 mt-1">{l.desc}</div>
                    </button>
                  ))}
                </div>
              </div>

              {/* Experience Nodes for Refraction */}
              <div className="space-y-4">
                <h3 className="text-sm font-semibold text-white">
                  Relevant Experience Nodes (Ranked by JD Match)
                </h3>
                <div className="space-y-3">
                  {((jdScore?.top_matches || vault?.nodes || []) as Array<{ id?: string; node_id?: string; company: string; role: string; raw_text: string; similarity?: number }>).slice(0, 6).map((item) => {
                    const nodeId = item.node_id || item.id;
                    if (!nodeId) return null;
                    const refraction = refractions[nodeId];
                    const isRefracting = refractingNodeId === nodeId;

                    return (
                      <div
                        key={nodeId}
                        className="p-5 rounded-xl bg-neutral-900/70 border border-neutral-800 space-y-3"
                      >
                        <div className="flex items-center justify-between">
                          <span className="text-xs font-bold text-neutral-300">
                            {item.company} &mdash; {item.role}
                          </span>
                          {item.similarity && (
                            <span className="text-xs px-2 py-0.5 rounded bg-sky-950/60 text-sky-400 border border-sky-800/40">
                              Similarity: {(item.similarity * 100).toFixed(1)}%
                            </span>
                          )}
                        </div>

                        {/* Original vs Refracted view */}
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          <div className="p-3 rounded-lg bg-neutral-950 border border-neutral-850">
                            <span className="text-[11px] font-semibold text-neutral-500 uppercase tracking-wider block mb-1">
                              Raw Vault Text
                            </span>
                            <p className="text-xs text-neutral-300 leading-relaxed">
                              {item.raw_text}
                            </p>
                          </div>

                          <div className="p-3 rounded-lg bg-neutral-950 border border-neutral-850">
                            <span className="text-[11px] font-semibold text-indigo-400 uppercase tracking-wider block mb-1">
                              Refracted ({selectedLens.toUpperCase()})
                            </span>
                            {refraction ? (
                              <div>
                                <p className="text-xs text-white leading-relaxed font-medium">
                                  {refraction.reframed_text}
                                </p>
                                <div className="mt-2 flex items-center gap-3 text-[11px]">
                                  <span className="text-emerald-400 flex items-center gap-1">
                                    <CheckCircle className="h-3 w-3" /> Factual Tokens Preserved
                                  </span>
                                  <span className="text-neutral-500">
                                    Similarity: {(refraction.verification.diff.similarity_ratio * 100).toFixed(0)}%
                                  </span>
                                </div>
                              </div>
                            ) : (
                              <div className="h-full flex items-center justify-center text-xs text-neutral-600">
                                Not refracted yet. Click Refract below.
                              </div>
                            )}
                          </div>
                        </div>

                        <div className="flex justify-end">
                          <button
                            onClick={() => handleRefract(nodeId)}
                            disabled={isRefracting}
                            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium transition disabled:opacity-50"
                          >
                            <Sparkles className="h-3.5 w-3.5" />
                            {isRefracting ? "Refracting with Diff Guardrails..." : "Refract through " + selectedLens}
                          </button>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          )}

          {/* TAB 3: RESUME STUDIO */}
          {activeTab === "resume" && (
            <div className="max-w-4xl mx-auto space-y-6">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-xl font-bold text-white">Resume Studio</h2>
                  <p className="text-sm text-neutral-400">
                    Live compiled resume customized for your target JD and lens.
                  </p>
                </div>
                {currentResume && (
                  <a
                    href={api.getResumePdfUrl(currentResume.resume_id)}
                    target="_blank"
                    rel="noreferrer"
                    className="flex items-center gap-2 px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-lg shadow-indigo-600/20 transition"
                  >
                    <Download className="h-4 w-4" />
                    Download PDF
                  </a>
                )}
              </div>

              {/* Template Selector Bar */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-3.5 rounded-xl bg-neutral-900 border border-neutral-800">
                <div className="flex items-center gap-2">
                  <Palette className="h-4 w-4 text-indigo-400" />
                  <span className="text-xs font-semibold text-neutral-300">Style Template:</span>
                  {switchingTemplate && (
                    <span className="text-[11px] text-indigo-400 animate-pulse">Switching styles...</span>
                  )}
                </div>
                <div className="grid grid-cols-2 sm:flex sm:flex-wrap gap-2">
                  {RESUME_TEMPLATES.map((t) => (
                    <button
                      key={t.id}
                      onClick={() => handleSwitchTemplate(t.id)}
                      disabled={switchingTemplate}
                      className={`px-3 py-1.5 rounded-lg text-xs font-medium transition text-left sm:text-center ${
                        selectedTemplate === t.id
                          ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/30"
                          : "bg-neutral-800 text-neutral-400 hover:text-neutral-200 hover:bg-neutral-700"
                      }`}
                    >
                      {t.name}
                    </button>
                  ))}
                </div>
              </div>

              {currentResume ? (
                <div className="bg-white rounded-xl shadow-2xl p-8 border border-neutral-200 overflow-hidden text-neutral-900">
                  <div
                    dangerouslySetInnerHTML={{ __html: currentResume.final_content }}
                    className="resume-preview"
                  />
                </div>
              ) : (
                <div className="p-16 text-center rounded-xl bg-neutral-900 border border-neutral-800 text-neutral-500 space-y-3">
                  <FileText className="h-10 w-10 mx-auto text-neutral-600" />
                  <p className="text-sm">No resume generated yet.</p>
                  <p className="text-xs text-neutral-600">
                    Go to the <strong>JD Match &amp; Refract</strong> tab, analyze a JD, and click &quot;Generate Tailored Resume&quot;.
                  </p>
                </div>
              )}
            </div>
          )}

          {/* TAB 4: GAP PROJECTS & MOCK INTERVIEW */}
          {activeTab === "gap" && (
            <div className="max-w-5xl mx-auto space-y-8">
              <div>
                <h2 className="text-xl font-bold text-white">Gap-Filler Projects & Mock Interviewing</h2>
                <p className="text-sm text-neutral-400">
                  Bridge identified skill gaps with evidence-based architecture blueprints and bar-raiser interview prep.
                </p>
              </div>

              {/* Action Buttons */}
              <div className="flex gap-3">
                <button
                  onClick={handleArchitectGap}
                  disabled={loadingGap || !jdAnalysis}
                  className="flex items-center gap-2 px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-medium transition disabled:opacity-50"
                >
                  <Code className="h-4 w-4" />
                  {loadingGap ? "Architecting Project..." : "Architect Gap-Filler Project"}
                </button>

                <button
                  onClick={handleGenerateInterview}
                  disabled={loadingInterview || !jdAnalysis}
                  className="flex items-center gap-2 px-4 py-2 rounded-lg bg-sky-600 hover:bg-sky-500 text-white text-sm font-medium transition disabled:opacity-50"
                >
                  <MessageSquare className="h-4 w-4" />
                  {loadingInterview ? "Generating Questions..." : "Generate Mock Interview Questions"}
                </button>
              </div>

              {!jdAnalysis && (
                <div className="p-4 rounded-lg bg-amber-950/40 border border-amber-800/40 text-amber-300 text-xs flex items-center gap-2">
                  <AlertCircle className="h-4 w-4 shrink-0" />
                  Please analyze a Job Description in the &quot;JD Match &amp; Refract&quot; tab first so the agents know which skills to target!
                </div>
              )}

              {/* Gap Project Blueprint Display */}
              {gapProject && (
                <div className="p-6 rounded-xl bg-neutral-900 border border-neutral-800 space-y-5">
                  <div className="flex items-center justify-between border-b border-neutral-800 pb-4">
                    <div>
                      <span className="text-xs font-semibold text-indigo-400 uppercase tracking-wider">
                        Tailored Architecture Blueprint
                      </span>
                      <h3 className="text-lg font-bold text-white mt-1">
                        {gapProject.project_blueprint.project_name}
                      </h3>
                      <p className="text-xs text-neutral-400 mt-0.5">
                        {gapProject.project_blueprint.tagline}
                      </p>
                    </div>
                    <div className="text-xs px-2.5 py-1 rounded bg-neutral-800 text-neutral-300 border border-neutral-700">
                      Targeting: {gapProject.targeted_gaps.join(", ")}
                    </div>
                  </div>

                  <div>
                    <h4 className="text-xs font-semibold text-neutral-300 uppercase tracking-wider mb-1">
                      System Design Summary
                    </h4>
                    <p className="text-xs text-neutral-300 leading-relaxed">
                      {gapProject.project_blueprint.architecture_summary}
                    </p>
                  </div>

                  <div>
                    <h4 className="text-xs font-semibold text-neutral-300 uppercase tracking-wider mb-2">
                      Phased Milestones
                    </h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      {gapProject.project_blueprint.milestones.map((m, i) => (
                        <div key={i} className="p-3 rounded-lg bg-neutral-950 border border-neutral-850">
                          <span className="text-xs font-bold text-neutral-200">{m.phase}</span>
                          <ul className="mt-2 space-y-1">
                            {m.deliverables.map((d, di) => (
                              <li key={di} className="text-xs text-neutral-400 flex items-start gap-1.5">
                                <span className="text-indigo-400">&bull;</span> {d}
                              </li>
                            ))}
                          </ul>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div>
                    <h4 className="text-xs font-semibold text-neutral-300 uppercase tracking-wider mb-2">
                      Resume Impact Bullets (Add Once Built)
                    </h4>
                    <ul className="space-y-1.5">
                      {gapProject.project_blueprint.resume_bullet_points.map((b, i) => (
                        <li
                          key={i}
                          className="text-xs text-white bg-neutral-950 p-2.5 rounded-lg border border-neutral-850"
                        >
                          &bull; {b}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              )}

              {/* Mock Interview Display */}
              {mockInterview && (
                <div className="p-6 rounded-xl bg-neutral-900 border border-neutral-800 space-y-4">
                  <h3 className="text-base font-bold text-white border-b border-neutral-800 pb-3">
                    Bar-Raiser Technical Mock Interview Questions
                  </h3>
                  <div className="space-y-3">
                    {mockInterview.interview_questions.map((q, idx) => (
                      <div
                        key={idx}
                        className="p-4 rounded-xl bg-neutral-950 border border-neutral-800 space-y-2"
                      >
                        <div className="flex items-center gap-2">
                          <span className="text-xs font-bold text-sky-400 px-2 py-0.5 rounded bg-sky-950/60 border border-sky-800/40">
                            {q.topic}
                          </span>
                        </div>
                        <p className="text-sm font-medium text-white">{q.question}</p>
                        <div className="text-xs text-neutral-400 bg-neutral-900 p-2.5 rounded border border-neutral-850">
                          <span className="font-semibold text-neutral-300">What to look for:</span>{" "}
                          {q.what_to_look_for}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* TAB 5: LOOM AI CHAT */}
          {activeTab === "chat" && (
            <div className="max-w-3xl mx-auto h-[calc(100vh-12rem)] flex flex-col justify-between rounded-xl bg-neutral-900 border border-neutral-800 overflow-hidden">
              <div className="p-4 border-b border-neutral-800 bg-neutral-900/80 flex items-center gap-2">
                <Sparkles className="h-4 w-4 text-indigo-400" />
                <span className="text-xs font-semibold text-white">Loom Career Identity Assistant</span>
              </div>

              {/* Messages feed */}
              <div className="flex-1 overflow-y-auto p-4 space-y-3">
                {chatMessages.map((m, i) => (
                  <div
                    key={i}
                    className={`flex ${m.sender === "user" ? "justify-end" : "justify-start"}`}
                  >
                    <div
                      className={`max-w-[80%] rounded-xl px-4 py-2.5 text-xs leading-relaxed ${
                        m.sender === "user"
                          ? "bg-indigo-600 text-white"
                          : "bg-neutral-950 text-neutral-200 border border-neutral-800"
                      }`}
                    >
                      {m.text}
                    </div>
                  </div>
                ))}
                {chatLoading && (
                  <div className="text-xs text-neutral-500 italic">Loom is thinking...</div>
                )}
              </div>

              {/* Chat Input */}
              <div className="p-3 border-t border-neutral-800 bg-neutral-950 flex gap-2">
                <input
                  type="text"
                  value={chatInput}
                  onChange={(e) => setChatInput(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && handleSendMessage()}
                  placeholder="Ask Loom to refine a bullet, prepare an interview answer, or suggest trade-offs..."
                  className="flex-1 rounded-lg bg-neutral-900 border border-neutral-800 px-3 py-2 text-xs text-neutral-200 placeholder-neutral-500 focus:outline-none focus:border-indigo-500"
                />
                <button
                  onClick={handleSendMessage}
                  disabled={chatLoading || !chatInput.trim()}
                  className="px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium transition disabled:opacity-50"
                >
                  Send
                </button>
              </div>
            </div>
          )}
        </main>
      </div>

      {/* Add / Edit Experience Node Modal */}
      {isNodeModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
          <div className="w-full max-w-lg rounded-2xl bg-neutral-900 border border-neutral-800 p-6 shadow-2xl space-y-4">
            <div className="flex items-center justify-between border-b border-neutral-800 pb-3">
              <h3 className="text-sm font-bold text-white">
                {editingNodeId ? "Edit Experience Bullet" : "Add New Experience Bullet"}
              </h3>
              <button
                onClick={() => setIsNodeModalOpen(false)}
                className="text-neutral-400 hover:text-white"
              >
                <X className="h-4 w-4" />
              </button>
            </div>

            <div className="space-y-3 text-xs">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-neutral-400 mb-1 font-semibold uppercase tracking-wider text-[10px]">
                    Company *
                  </label>
                  <input
                    type="text"
                    value={nodeForm.company}
                    onChange={(e) => setNodeForm({ ...nodeForm, company: e.target.value })}
                    placeholder="e.g. Stripe, Uber, Microsoft"
                    className="w-full rounded-lg bg-neutral-950 border border-neutral-800 p-2 text-white focus:outline-none focus:border-indigo-500"
                  />
                </div>
                <div>
                  <label className="block text-neutral-400 mb-1 font-semibold uppercase tracking-wider text-[10px]">
                    Role / Title *
                  </label>
                  <input
                    type="text"
                    value={nodeForm.role}
                    onChange={(e) => setNodeForm({ ...nodeForm, role: e.target.value })}
                    placeholder="e.g. Senior Backend Engineer"
                    className="w-full rounded-lg bg-neutral-950 border border-neutral-800 p-2 text-white focus:outline-none focus:border-indigo-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-neutral-400 mb-1 font-semibold uppercase tracking-wider text-[10px]">
                  Duration
                </label>
                <input
                  type="text"
                  value={nodeForm.duration}
                  onChange={(e) => setNodeForm({ ...nodeForm, duration: e.target.value })}
                  placeholder="e.g. 2023 - Present"
                  className="w-full rounded-lg bg-neutral-950 border border-neutral-800 p-2 text-white focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-neutral-400 mb-1 font-semibold uppercase tracking-wider text-[10px]">
                  Achievement Bullet Text * (Stored in Vault &amp; Embedded in Vector DB)
                </label>
                <textarea
                  value={nodeForm.raw_text}
                  onChange={(e) => setNodeForm({ ...nodeForm, raw_text: e.target.value })}
                  placeholder="e.g. Architected event streaming pipeline using Kafka and Go, reducing data processing latency by 60%..."
                  rows={4}
                  className="w-full rounded-lg bg-neutral-950 border border-neutral-800 p-2 text-white focus:outline-none focus:border-indigo-500 leading-relaxed font-sans"
                />
              </div>

              <div>
                <label className="block text-neutral-400 mb-1 font-semibold uppercase tracking-wider text-[10px]">
                  Technical Tags (comma-separated)
                </label>
                <input
                  type="text"
                  value={nodeForm.tags}
                  onChange={(e) => setNodeForm({ ...nodeForm, tags: e.target.value })}
                  placeholder="e.g. Go, Kafka, AWS, Kubernetes"
                  className="w-full rounded-lg bg-neutral-950 border border-neutral-800 p-2 text-white focus:outline-none focus:border-indigo-500"
                />
              </div>
            </div>

            <div className="flex justify-end gap-2 pt-2 border-t border-neutral-800">
              <button
                onClick={() => setIsNodeModalOpen(false)}
                className="px-4 py-2 rounded-lg text-xs text-neutral-400 hover:text-white"
              >
                Cancel
              </button>
              <button
                onClick={handleSaveNode}
                className="px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow transition"
              >
                {editingNodeId ? "Save Changes" : "Create Bullet"}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Add / Edit Project Modal */}
      {isProjectModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
          <div className="w-full max-w-lg rounded-2xl bg-neutral-900 border border-neutral-800 p-6 shadow-2xl space-y-4">
            <div className="flex items-center justify-between border-b border-neutral-800 pb-3">
              <h3 className="text-sm font-bold text-white">
                {editingProjectId ? "Edit Project" : "Add New Project"}
              </h3>
              <button
                onClick={() => setIsProjectModalOpen(false)}
                className="text-neutral-400 hover:text-white"
              >
                <X className="h-4 w-4" />
              </button>
            </div>

            <div className="space-y-3 text-xs">
              <div>
                <label className="block text-neutral-400 mb-1 font-semibold uppercase tracking-wider text-[10px]">
                  Project Name *
                </label>
                <input
                  type="text"
                  value={projectForm.name}
                  onChange={(e) => setProjectForm({ ...projectForm, name: e.target.value })}
                  placeholder="e.g. Distributed In-Memory Cache"
                  className="w-full rounded-lg bg-neutral-950 border border-neutral-800 p-2 text-white focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-neutral-400 mb-1 font-semibold uppercase tracking-wider text-[10px]">
                  Project Description *
                </label>
                <textarea
                  value={projectForm.description}
                  onChange={(e) => setProjectForm({ ...projectForm, description: e.target.value })}
                  placeholder="e.g. High-throughput tiered storage engine implemented in Rust with Raft consensus..."
                  rows={4}
                  className="w-full rounded-lg bg-neutral-950 border border-neutral-800 p-2 text-white focus:outline-none focus:border-indigo-500 leading-relaxed font-sans"
                />
              </div>

              <div>
                <label className="block text-neutral-400 mb-1 font-semibold uppercase tracking-wider text-[10px]">
                  Technologies / Tags (comma-separated)
                </label>
                <input
                  type="text"
                  value={projectForm.tags}
                  onChange={(e) => setProjectForm({ ...projectForm, tags: e.target.value })}
                  placeholder="e.g. Rust, Raft, RocksDB, gRPC"
                  className="w-full rounded-lg bg-neutral-950 border border-neutral-800 p-2 text-white focus:outline-none focus:border-indigo-500"
                />
              </div>
            </div>

            <div className="flex justify-end gap-2 pt-2 border-t border-neutral-800">
              <button
                onClick={() => setIsProjectModalOpen(false)}
                className="px-4 py-2 rounded-lg text-xs text-neutral-400 hover:text-white"
              >
                Cancel
              </button>
              <button
                onClick={handleSaveProject}
                className="px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow transition"
              >
                {editingProjectId ? "Save Changes" : "Create Project"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
