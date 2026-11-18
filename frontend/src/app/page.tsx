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
  Terminal,
  Download,
  CheckCircle,
  AlertCircle,
  RefreshCw,
  Search,
  MessageSquare,
  Briefcase,
  ExternalLink,
  ChevronRight,
  Code,
  Shield,
  Zap,
} from "lucide-react";

const LENSES = [
  { id: "platform", name: "Platform Engineering", desc: "Scalability, API architecture, developer experience" },
  { id: "infrastructure", name: "Infrastructure / DevOps", desc: "Cloud architecture, CI/CD, reliability, SRE" },
  { id: "leadership", name: "Team Leadership", desc: "Mentorship, cross-functional collaboration, ownership" },
  { id: "business_impact", name: "Business Impact", desc: "Revenue, cost reduction, efficiency, measurable ROI" },
  { id: "data_engineering", name: "Data Engineering", desc: "Pipelines, data modeling, ETL, streaming" },
  { id: "security", name: "Security & Compliance", desc: "Access control, hardening, compliance, threat mitigation" },
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
    } catch (err: any) {
      alert("Ingestion error: " + err.message);
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
    } catch (err: any) {
      alert("JD analysis error: " + err.message);
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
    } catch (err: any) {
      alert("Refraction error: " + err.message);
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
      const res = await api.generateResume(jdAnalysis.session_id, vault.user.id, selectedLens);
      setCurrentResume(res);
      setActiveTab("resume");
    } catch (err: any) {
      alert("Resume generation error: " + err.message);
    } finally {
      setGeneratingResume(false);
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
    } catch (err: any) {
      alert("Project architecting error: " + err.message);
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
    } catch (err: any) {
      alert("Mock interview error: " + err.message);
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
    } catch (err: any) {
      setChatMessages((prev) => [
        ...prev,
        { sender: "loom", text: "Error connecting to Loom AI: " + err.message },
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
                <div className="text-xs bg-neutral-900 border border-neutral-800 px-3 py-1.5 rounded-lg text-neutral-300">
                  Total Nodes: <span className="text-indigo-400 font-semibold">{vault?.nodes.length || 0}</span>
                </div>
              </div>

              {loadingVault ? (
                <div className="py-20 text-center text-neutral-500">Loading vault records...</div>
              ) : (
                <>
                  {/* Personal Summary Card */}
                  {vault?.user?.summary && (
                    <div className="p-5 rounded-xl bg-neutral-900 border border-neutral-800">
                      <div className="text-xs font-semibold text-neutral-400 uppercase tracking-wider mb-2">
                        Master Profile Summary
                      </div>
                      <p className="text-sm text-neutral-200 leading-relaxed">{vault.user.summary}</p>
                    </div>
                  )}

                  {/* Bullet Point Nodes List */}
                  <div className="space-y-3">
                    <h3 className="text-sm font-semibold text-neutral-300 uppercase tracking-wider">
                      Experience Nodes ({vault?.nodes.length})
                    </h3>
                    <div className="grid gap-3">
                      {vault?.nodes.map((node) => (
                        <div
                          key={node.id}
                          className="p-4 rounded-xl bg-neutral-900/60 border border-neutral-800 hover:border-neutral-700 transition"
                        >
                          <div className="flex items-baseline justify-between mb-2">
                            <div className="text-sm font-bold text-white">
                              {node.company}{" "}
                              <span className="font-normal text-neutral-400">&mdash; {node.role}</span>
                            </div>
                            <div className="text-xs text-neutral-500 font-mono">{node.duration}</div>
                          </div>
                          <p className="text-sm text-neutral-300 leading-relaxed mb-3">{node.raw_text}</p>
                          <div className="flex flex-wrap gap-1.5">
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

                  {/* Skills Grid */}
                  <div className="space-y-3 pt-4">
                    <h3 className="text-sm font-semibold text-neutral-300 uppercase tracking-wider">
                      Master Skills Profile ({vault?.skills.length})
                    </h3>
                    <div className="flex flex-wrap gap-2">
                      {vault?.skills.map((s) => (
                        <span
                          key={s.id}
                          className="text-xs px-2.5 py-1 rounded-lg bg-neutral-900 border border-neutral-800 text-indigo-300 font-medium"
                        >
                          {s.skill_name}
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
                  {(jdScore?.top_matches || vault?.nodes || []).slice(0, 6).map((item: any) => {
                    const nodeId = item.node_id || item.id;
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
                    Go to the <strong>JD Match & Refract</strong> tab, analyze a JD, and click "Generate Tailored Resume".
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
                  Please analyze a Job Description in the "JD Match & Refract" tab first so the agents know which skills to target!
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
    </div>
  );
}
