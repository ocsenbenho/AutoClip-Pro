"use client";

import { useState, useEffect } from "react";

const API_BASE = "http://localhost:8000/api";

export default function HomePage() {
    const [url, setUrl] = useState("");
    const [loading, setLoading] = useState(false);
    const [recentJobs, setRecentJobs] = useState([]);
    const [message, setMessage] = useState(null);
    const [detectors, setDetectors] = useState([]);
    const [selectedDetector, setSelectedDetector] = useState("local");
    const [verticalFormat, setVerticalFormat] = useState(false);
    const [uploadMode, setUploadMode] = useState(false);
    const [selectedFile, setSelectedFile] = useState(null);
    const [taskType, setTaskType] = useState("clip");
    const [videoLanguage, setVideoLanguage] = useState("auto");

    // Fetch recent jobs and detectors on mount
    useEffect(() => {
        fetchJobs();
        fetchDetectors();
        const interval = setInterval(fetchJobs, 3000);
        return () => clearInterval(interval);
    }, []);

    async function fetchJobs() {
        try {
            const res = await fetch(`${API_BASE}/jobs`);
            if (res.ok) {
                const data = await res.json();
                setRecentJobs(data.slice(0, 5));
            }
        } catch {
            // API not available
        }
    }

    async function fetchDetectors() {
        try {
            const res = await fetch(`${API_BASE}/detectors`);
            if (res.ok) {
                const data = await res.json();
                setDetectors(data);
            }
        } catch {
            // API not available
        }
    }

    async function handleSubmit(e) {
        e.preventDefault();
        
        if (uploadMode && !selectedFile) return;
        if (!uploadMode && !url.trim()) return;

        setLoading(true);
        setMessage(null);

        try {
            let res;
            if (uploadMode) {
                const formData = new FormData();
                formData.append("file", selectedFile);
                formData.append("detector", selectedDetector);
                // HTML forms will send the string "true" or "false" but python FastAPI Form(bool) handles that
                formData.append("vertical_format", verticalFormat);
                formData.append("task_type", taskType);
                formData.append("video_language", videoLanguage);
                
                res = await fetch(`${API_BASE}/jobs/upload`, {
                    method: "POST",
                    body: formData,
                });
            } else {
                res = await fetch(`${API_BASE}/jobs`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        video_url: url.trim(),
                        detector: selectedDetector,
                        vertical_format: verticalFormat,
                        task_type: taskType,
                        video_language: videoLanguage
                    }),
                });
            }

            if (res.ok) {
                const job = await res.json();
                setMessage({
                    type: "success",
                    text: `Job created! ID: ${job.id}`,
                });
                setUrl("");
                setSelectedFile(null);
                fetchJobs();
            } else {
                const err = await res.json();
                setMessage({
                    type: "error",
                    text: err.detail || "Failed to create job",
                });
            }
        } catch {
            setMessage({
                type: "error",
                text: "Cannot connect to API. Is the backend running?",
            });
        } finally {
            setLoading(false);
        }
    }

    function getStatusColor(status) {
        const colors = {
            pending: "#9ca3af",
            downloading: "#60a5fa",
            transcribing: "#a78bfa",
            detecting_highlights: "#fbbf24",
            clipping: "#f472b6",
            generating_subtitles: "#2dd4bf",
            completed: "#34d399",
            failed: "#f87171",
        };
        return colors[status] || "#9ca3af";
    }

    function isActive(status) {
        return !["completed", "failed", "pending"].includes(status);
    }

    return (
        <div className="fade-in">
            {/* ── Hero Section ─────────────────────────────── */}
            <section style={{ textAlign: "center", marginBottom: 56 }}>
                <h1
                    style={{
                        fontSize: 48,
                        fontWeight: 800,
                        lineHeight: 1.1,
                        marginBottom: 16,
                        background: "linear-gradient(135deg, #f1f1f7, #a78bfa)",
                        WebkitBackgroundClip: "text",
                        WebkitTextFillColor: "transparent",
                    }}
                >
                    AI-Powered Video Clips
                </h1>
                <p
                    style={{
                        fontSize: 18,
                        color: "var(--text-secondary)",
                        maxWidth: 600,
                        margin: "0 auto 40px",
                        lineHeight: 1.6,
                    }}
                >
                    Transform long videos into engaging short clips. Automatic
                    transcription, highlight detection, and subtitle generation.
                </p>

                <div style={{ display: "flex", justifyContent: "center", gap: 12, marginBottom: 20 }}>
                    <button 
                        type="button"
                        className="btn-glow"
                        style={{ 
                            background: taskType === 'clip' ? 'var(--accent)' : 'rgba(255,255,255,0.05)',
                            border: taskType === 'clip' ? '1px solid var(--accent-light)' : '1px solid rgba(255,255,255,0.1)',
                        }}
                        onClick={() => setTaskType("clip")}
                    >
                        ✂️ Create Clips
                    </button>
                    <button 
                        type="button"
                        className="btn-glow"
                        style={{ 
                            background: taskType === 'transcribe' ? 'var(--accent)' : 'rgba(255,255,255,0.05)',
                            border: taskType === 'transcribe' ? '1px solid var(--accent-light)' : '1px solid rgba(255,255,255,0.1)',
                        }}
                        onClick={() => setTaskType("transcribe")}
                    >
                        📄 Transcribe Only
                    </button>
                </div>

                <div style={{ display: "flex", justifyContent: "center", gap: 12, marginBottom: 20 }}>
                    <button 
                        type="button"
                        className="btn-glow"
                        style={{ 
                            background: !uploadMode ? 'var(--accent)' : 'rgba(255,255,255,0.05)',
                            border: !uploadMode ? '1px solid var(--accent-light)' : '1px solid rgba(255,255,255,0.1)',
                        }}
                        onClick={() => setUploadMode(false)}
                    >
                        🔗 Paste URL
                    </button>
                    <button 
                        type="button"
                        className="btn-glow"
                        style={{ 
                            background: uploadMode ? 'var(--accent)' : 'rgba(255,255,255,0.05)',
                            border: uploadMode ? '1px solid var(--accent-light)' : '1px solid rgba(255,255,255,0.1)',
                        }}
                        onClick={() => setUploadMode(true)}
                    >
                        📁 Upload Video
                    </button>
                </div>

                {/* ── URL Input Form ─────────────────────────── */}
                <form
                    onSubmit={handleSubmit}
                    className="glass-card"
                    style={{
                        maxWidth: 720,
                        margin: "0 auto",
                        padding: 24,
                        display: "flex",
                        flexDirection: "column",
                        gap: 16,
                    }}
                >
                    <div style={{ display: "flex", width: "100%", gap: 12 }}>
                        {uploadMode ? (
                            <input
                                key="upload-input"
                                type="file"
                                accept="video/*"
                                className="input-dark"
                                onChange={(e) => setSelectedFile(e.target.files[0])}
                                disabled={loading}
                                style={{ flex: 1, padding: "10px" }}
                            />
                        ) : (
                            <input
                                key="url-input"
                                type="text"
                                className="input-dark"
                                placeholder="Paste YouTube URL here..."
                                value={url}
                                onChange={(e) => setUrl(e.target.value)}
                                disabled={loading}
                                style={{ flex: 1 }}
                            />
                        )}
                        <select
                            className="input-dark"
                            value={videoLanguage}
                            onChange={(e) => setVideoLanguage(e.target.value)}
                            disabled={loading}
                            style={{ width: 140, cursor: "pointer", appearance: "auto" }}
                        >
                            <option value="auto">Auto-Detect</option>
                            <option value="vi">Vietnamese</option>
                            <option value="en">English</option>
                        </select>
                        {taskType === "clip" && (
                            <select
                                className="input-dark"
                                value={selectedDetector}
                                onChange={(e) => setSelectedDetector(e.target.value)}
                                disabled={loading || detectors.length === 0}
                                style={{ width: 220, cursor: "pointer", appearance: "auto" }}
                            >
                                {detectors.length === 0 ? (
                                    <option value="local">Local Analysis (Free)</option>
                                ) : (
                                    detectors.map((d) => (
                                        <option key={d.id} value={d.id}>
                                            {d.name.split(" ")[0]} {d.name.includes("Free") ? "(Free)" : "(API Key)"}
                                        </option>
                                    ))
                                )}
                            </select>
                        )}
                    </div>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                        <div style={{flex: 1}}>
                            {taskType === "clip" && (
                                <label
                                    style={{
                                        display: "flex",
                                        alignItems: "center",
                                        gap: 8,
                                        color: "var(--text-secondary)",
                                        fontSize: 14,
                                        cursor: "pointer",
                                        userSelect: "none",
                                    }}
                                >
                                    <input
                                        type="checkbox"
                                        checked={verticalFormat}
                                        onChange={(e) => setVerticalFormat(e.target.checked)}
                                        disabled={loading}
                                        style={{
                                            accentColor: "var(--accent)",
                                            width: 16,
                                            height: 16,
                                            cursor: "pointer",
                                        }}
                                    />
                                    📱 Vertical Format (9:16)
                                </label>
                            )}
                        </div>
                        <button
                            type="submit"
                            className="btn-glow"
                            disabled={loading || (uploadMode ? !selectedFile : !url.trim())}
                            style={{ whiteSpace: "nowrap", minWidth: 140 }}
                        >
                            {loading ? "Submitting..." : taskType === "clip" ? "⚡ Generate Clips" : "📄 Get Transcript"}
                        </button>
                    </div>
                </form>

                {/* ── Message ────────────────────────────────── */}
                {message && (
                    <div
                        className="fade-in"
                        style={{
                            maxWidth: 640,
                            margin: "16px auto 0",
                            padding: "12px 20px",
                            borderRadius: 12,
                            fontSize: 14,
                            background:
                                message.type === "success"
                                    ? "rgba(16,185,129,0.1)"
                                    : "rgba(239,68,68,0.1)",
                            color: message.type === "success" ? "#34d399" : "#f87171",
                            border: `1px solid ${message.type === "success"
                                ? "rgba(16,185,129,0.2)"
                                : "rgba(239,68,68,0.2)"
                                }`,
                        }}
                    >
                        {message.text}
                    </div>
                )}
            </section>

            {/* ── Feature Cards ────────────────────────────── */}
            <section style={{ marginBottom: 56 }}>
                <div
                    style={{
                        display: "grid",
                        gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))",
                        gap: 20,
                    }}
                >
                    {[
                        {
                            icon: "📥",
                            title: "Smart Download",
                            desc: "Downloads videos from YouTube with optimal quality settings",
                        },
                        {
                            icon: "🎙️",
                            title: "AI Transcription",
                            desc: "Whisper-powered speech-to-text with precise timestamps",
                        },
                        {
                            icon: "✨",
                            title: "Highlight Detection",
                            desc: "GPT analyzes transcripts to find viral-worthy moments",
                        },
                        {
                            icon: "✂️",
                            title: "Auto Clipping",
                            desc: "FFmpeg cuts and encodes clips automatically",
                        },
                    ].map((feature, i) => (
                        <div
                            key={i}
                            className="glass-card"
                            style={{
                                padding: 24,
                                textAlign: "left",
                            }}
                        >
                            <div style={{ fontSize: 32, marginBottom: 12 }}>
                                {feature.icon}
                            </div>
                            <h3
                                style={{
                                    fontSize: 16,
                                    fontWeight: 700,
                                    marginBottom: 8,
                                }}
                            >
                                {feature.title}
                            </h3>
                            <p
                                style={{
                                    fontSize: 13,
                                    color: "var(--text-secondary)",
                                    lineHeight: 1.5,
                                }}
                            >
                                {feature.desc}
                            </p>
                        </div>
                    ))}
                </div>
            </section>

            {/* ── Recent Jobs ──────────────────────────────── */}
            {recentJobs.length > 0 && (
                <section>
                    <div
                        style={{
                            display: "flex",
                            justifyContent: "space-between",
                            alignItems: "center",
                            marginBottom: 20,
                        }}
                    >
                        <h2 style={{ fontSize: 22, fontWeight: 700 }}>Recent Jobs</h2>
                        <a
                            href="/jobs"
                            style={{
                                color: "var(--accent-light)",
                                textDecoration: "none",
                                fontSize: 14,
                                fontWeight: 500,
                            }}
                        >
                            View All →
                        </a>
                    </div>

                    <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
                        {recentJobs.map((job) => (
                            <a
                                key={job.id}
                                href={`/jobs/${job.id}`}
                                className="glass-card"
                                style={{
                                    padding: "16px 20px",
                                    display: "flex",
                                    justifyContent: "space-between",
                                    alignItems: "center",
                                    textDecoration: "none",
                                    color: "inherit",
                                    cursor: "pointer",
                                }}
                            >
                                <div
                                    style={{
                                        display: "flex",
                                        alignItems: "center",
                                        gap: 14,
                                        flex: 1,
                                        minWidth: 0,
                                    }}
                                >
                                    <div
                                        style={{
                                            width: 40,
                                            height: 40,
                                            borderRadius: 10,
                                            background: "rgba(124,58,237,0.15)",
                                            display: "flex",
                                            alignItems: "center",
                                            justifyContent: "center",
                                            fontSize: 18,
                                            flexShrink: 0,
                                        }}
                                    >
                                        🎬
                                    </div>
                                    <div style={{ minWidth: 0 }}>
                                        <div
                                            style={{
                                                fontSize: 14,
                                                fontWeight: 600,
                                                whiteSpace: "nowrap",
                                                overflow: "hidden",
                                                textOverflow: "ellipsis",
                                            }}
                                        >
                                            {job.video_title || job.video_url}
                                        </div>
                                        <div
                                            style={{
                                                fontSize: 12,
                                                color: "var(--text-secondary)",
                                                marginTop: 2,
                                                display: "flex",
                                                alignItems: "center",
                                                gap: 8,
                                            }}
                                        >
                                            <span>{job.progress_message || job.status.replace(/_/g, " ")}</span>
                                            {job.detector && (
                                                <>
                                                    <span style={{ opacity: 0.5 }}>•</span>
                                                    <span style={{
                                                        background: "rgba(255,255,255,0.05)",
                                                        padding: "2px 6px",
                                                        borderRadius: 4,
                                                        fontSize: 11
                                                    }}>
                                                        {job.detector === "local" ? "🤖 Local" : "✨ OpenAI"}
                                                    </span>
                                                </>
                                            )}
                                            {job.vertical_format && (
                                                <>
                                                    <span style={{ opacity: 0.5 }}>•</span>
                                                    <span style={{
                                                        background: "rgba(255,255,255,0.05)",
                                                        padding: "2px 6px",
                                                        borderRadius: 4,
                                                        fontSize: 11
                                                    }}>
                                                        📱 9:16
                                                    </span>
                                                </>
                                            )}
                                        </div>
                                    </div>
                                </div>

                                <div
                                    style={{
                                        display: "flex",
                                        alignItems: "center",
                                        gap: 12,
                                        flexShrink: 0,
                                    }}
                                >
                                    {job.clips_count > 0 && (
                                        <span
                                            style={{
                                                fontSize: 12,
                                                color: "var(--text-secondary)",
                                            }}
                                        >
                                            {job.clips_count} clips
                                        </span>
                                    )}
                                    <span className={`badge badge-${job.status}`}>
                                        {isActive(job.status) && (
                                            <span
                                                className="pulse-dot"
                                                style={{
                                                    backgroundColor: getStatusColor(job.status),
                                                }}
                                            />
                                        )}
                                        {job.status.replace(/_/g, " ")}
                                    </span>
                                </div>
                            </a>
                        ))}
                    </div>
                </section>
            )}
        </div>
    );
}
