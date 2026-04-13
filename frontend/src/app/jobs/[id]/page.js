"use client";

import { useState, useEffect, use } from "react";

const API_BASE = "http://localhost:8000/api";

export default function JobDetailPage({ params }) {
    const { id } = use(params);
    const [job, setJob] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        fetchJob();
        const interval = setInterval(fetchJob, 2000);
        return () => clearInterval(interval);
    }, [id]);

    async function fetchJob() {
        try {
            const res = await fetch(`${API_BASE}/jobs/${id}`);
            if (res.ok) {
                const data = await res.json();
                setJob(data);
            } else if (res.status === 404) {
                setError("Job not found");
            }
        } catch {
            setError("Cannot connect to API");
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

    function formatDuration(seconds) {
        if (!seconds) return "0s";
        const m = Math.floor(seconds / 60);
        const s = Math.floor(seconds % 60);
        if (m === 0) return `${s}s`;
        return `${m}m ${s}s`;
    }

    function formatTimestamp(seconds) {
        const m = Math.floor(seconds / 60);
        const s = Math.floor(seconds % 60);
        return `${m}:${s.toString().padStart(2, "0")}`;
    }

    // Pipeline steps for progress visualization
    const pipelineSteps = [
        { key: "downloading", label: "Download", icon: "📥" },
        { key: "transcribing", label: "Transcribe", icon: "🎙️" },
        { key: "detecting_highlights", label: "Highlights", icon: "✨" },
        { key: "clipping", label: "Clipping", icon: "✂️" },
        { key: "generating_subtitles", label: "Subtitles", icon: "📝" },
        { key: "completed", label: "Done", icon: "✅" },
    ];

    function getStepStatus(stepKey) {
        if (!job) return "pending";
        const statusOrder = pipelineSteps.map((s) => s.key);
        const currentIdx = statusOrder.indexOf(job.status);
        const stepIdx = statusOrder.indexOf(stepKey);
        if (job.status === "failed") return currentIdx >= stepIdx ? "failed" : "pending";
        if (stepIdx < currentIdx) return "done";
        if (stepIdx === currentIdx) return "active";
        return "pending";
    }

    if (loading) {
        return (
            <div className="fade-in" style={{ textAlign: "center", paddingTop: 80 }}>
                <div
                    className="shimmer"
                    style={{
                        width: 300,
                        height: 32,
                        borderRadius: 8,
                        margin: "0 auto 16px",
                    }}
                />
                <div
                    className="shimmer"
                    style={{ width: 200, height: 20, borderRadius: 8, margin: "0 auto" }}
                />
            </div>
        );
    }

    if (error) {
        return (
            <div className="fade-in" style={{ textAlign: "center", paddingTop: 80 }}>
                <div style={{ fontSize: 48, marginBottom: 16 }}>😕</div>
                <h2 style={{ fontSize: 22, fontWeight: 700, marginBottom: 8 }}>
                    {error}
                </h2>
                <a
                    href="/jobs"
                    style={{ color: "var(--accent-light)", textDecoration: "none" }}
                >
                    ← Back to jobs
                </a>
            </div>
        );
    }

    return (
        <div className="fade-in">
            {/* ── Header ───────────────────────────────────── */}
            <div style={{ marginBottom: 32 }}>
                <a
                    href="/jobs"
                    style={{
                        color: "var(--text-secondary)",
                        textDecoration: "none",
                        fontSize: 13,
                        display: "inline-flex",
                        alignItems: "center",
                        gap: 4,
                        marginBottom: 16,
                    }}
                >
                    ← Back to jobs
                </a>

                <div
                    style={{
                        display: "flex",
                        justifyContent: "space-between",
                        alignItems: "flex-start",
                        gap: 16,
                        flexWrap: "wrap",
                    }}
                >
                    <div>
                        <h1 style={{ fontSize: 28, fontWeight: 800, marginBottom: 8 }}>
                            {job.video_title || "Processing..."}
                        </h1>
                        <div
                            style={{
                                display: "flex",
                                alignItems: "center",
                                gap: 12,
                                color: "var(--text-secondary)",
                                fontSize: 13,
                            }}
                        >
                            <span style={{ fontFamily: "monospace" }}>#{job.id}</span>
                            {job.video_duration && (
                                <span>⏱️ {formatDuration(job.video_duration)}</span>
                            )}
                            {job.detector && (
                                <span style={{
                                    background: "rgba(255,255,255,0.05)",
                                    padding: "2px 8px",
                                    borderRadius: 4,
                                    fontSize: 12
                                }}>
                                    {job.detector === "local" ? "🤖 Local Analysis" : job.detector === "gemini" ? "💎 Gemini" : "✨ OpenAI Detector"}
                                </span>
                            )}
                            {job.vertical_format && (
                                <span style={{
                                    background: "rgba(255,255,255,0.05)",
                                    padding: "2px 8px",
                                    borderRadius: 4,
                                    fontSize: 12
                                }}>
                                    📱 Vertical 9:16
                                </span>
                            )}
                        </div>
                    </div>

                    <span className={`badge badge-${job.status}`}>
                        {isActive(job.status) && (
                            <span
                                className="pulse-dot"
                                style={{ backgroundColor: getStatusColor(job.status) }}
                            />
                        )}
                        {job.status.replace(/_/g, " ")}
                    </span>
                </div>
            </div>

            {/* ── Pipeline Progress ────────────────────────── */}
            <div
                className="glass-card"
                style={{ padding: 24, marginBottom: 32 }}
            >
                <h3
                    style={{
                        fontSize: 14,
                        fontWeight: 600,
                        marginBottom: 20,
                        color: "var(--text-secondary)",
                        textTransform: "uppercase",
                        letterSpacing: 1,
                    }}
                >
                    Pipeline Progress
                </h3>

                <div
                    style={{
                        display: "flex",
                        justifyContent: "space-between",
                        alignItems: "center",
                        gap: 4,
                    }}
                >
                    {pipelineSteps.map((step, i) => {
                        const status = getStepStatus(step.key);
                        return (
                            <div
                                key={step.key}
                                style={{
                                    display: "flex",
                                    alignItems: "center",
                                    gap: 4,
                                    flex: 1,
                                }}
                            >
                                <div
                                    style={{
                                        display: "flex",
                                        flexDirection: "column",
                                        alignItems: "center",
                                        gap: 6,
                                        flex: 1,
                                    }}
                                >
                                    <div
                                        style={{
                                            width: 36,
                                            height: 36,
                                            borderRadius: 10,
                                            display: "flex",
                                            alignItems: "center",
                                            justifyContent: "center",
                                            fontSize: 18,
                                            background:
                                                status === "done"
                                                    ? "rgba(16,185,129,0.15)"
                                                    : status === "active"
                                                        ? "rgba(124,58,237,0.2)"
                                                        : status === "failed"
                                                            ? "rgba(239,68,68,0.15)"
                                                            : "rgba(255,255,255,0.04)",
                                            border: `1px solid ${status === "active"
                                                ? "var(--accent)"
                                                : "transparent"
                                                }`,
                                            transition: "all 0.3s",
                                        }}
                                        className={status === "active" ? "shimmer" : ""}
                                    >
                                        {step.icon}
                                    </div>
                                    <span
                                        style={{
                                            fontSize: 10,
                                            fontWeight: 600,
                                            color:
                                                status === "done"
                                                    ? "#34d399"
                                                    : status === "active"
                                                        ? "var(--accent-light)"
                                                        : "var(--text-secondary)",
                                            textTransform: "uppercase",
                                            letterSpacing: 0.5,
                                        }}
                                    >
                                        {step.label}
                                    </span>
                                </div>

                                {i < pipelineSteps.length - 1 && (
                                    <div
                                        style={{
                                            width: "100%",
                                            height: 2,
                                            background:
                                                status === "done"
                                                    ? "rgba(16,185,129,0.3)"
                                                    : "rgba(255,255,255,0.06)",
                                            borderRadius: 1,
                                            marginBottom: 20,
                                        }}
                                    />
                                )}
                            </div>
                        );
                    })}
                </div>

                {job.progress_message && (
                    <div
                        style={{
                            marginTop: 16,
                            padding: "10px 16px",
                            borderRadius: 8,
                            background: "rgba(255,255,255,0.03)",
                            fontSize: 13,
                            color: isActive(job.status)
                                ? "var(--accent-light)"
                                : "var(--text-secondary)",
                        }}
                    >
                        {job.progress_message}
                    </div>
                )}

                {job.error && (
                    <div
                        style={{
                            marginTop: 16,
                            padding: "10px 16px",
                            borderRadius: 8,
                            background: "rgba(239,68,68,0.08)",
                            border: "1px solid rgba(239,68,68,0.2)",
                            fontSize: 13,
                            color: "#f87171",
                        }}
                    >
                        ⚠️ {job.error}
                    </div>
                )}
            </div>

            {/* ── Full Transcript ────────────────────────────── */}
            {job.transcript_url && (
                <div style={{ marginBottom: 32 }}>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
                        <h2 style={{ fontSize: 22, fontWeight: 700 }}>Full Text Transcript</h2>
                        <a
                            href={`http://localhost:8000${job.transcript_url}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="btn-glow"
                            download
                            style={{ textDecoration: "none", fontSize: 13, padding: "8px 16px" }}
                        >
                            📄 Download File
                        </a>
                    </div>
                </div>
            )}

            {/* ── Clips Grid ───────────────────────────────── */}
            {job.clips && job.clips.length > 0 && (
                <div>
                    <h2 style={{ fontSize: 22, fontWeight: 700, marginBottom: 20 }}>
                        Generated Clips ({job.clips.length})
                    </h2>

                    <div
                        style={{
                            display: "grid",
                            gridTemplateColumns: "repeat(auto-fill, minmax(340, 1fr))",
                            gap: 16,
                        }}
                    >
                        {job.clips.map((clip, i) => (
                            <div
                                key={clip.id}
                                className="glass-card"
                                style={{ overflow: "hidden" }}
                            >
                                {/* Video Player */}
                                <div
                                    style={{
                                        position: "relative",
                                        background: "#000",
                                        aspectRatio: "16/9",
                                    }}
                                >
                                    <video
                                        controls
                                        preload="metadata"
                                        style={{
                                            width: "100%",
                                            height: "100%",
                                            objectFit: "contain",
                                        }}
                                    >
                                        <source
                                            src={`http://localhost:8000${clip.video_url}`}
                                            type="video/mp4"
                                        />
                                        {clip.subtitle_url && (
                                            <track
                                                kind="subtitles"
                                                src={`http://localhost:8000${clip.subtitle_url}`}
                                                srcLang="en"
                                                label="English"
                                                default
                                            />
                                        )}
                                    </video>

                                    {/* Clip number badge */}
                                    <div
                                        style={{
                                            position: "absolute",
                                            top: 8,
                                            left: 8,
                                            background: "rgba(0,0,0,0.7)",
                                            padding: "2px 8px",
                                            borderRadius: 6,
                                            fontSize: 11,
                                            fontWeight: 600,
                                        }}
                                    >
                                        Clip {i + 1}
                                    </div>

                                    {/* Duration badge */}
                                    <div
                                        style={{
                                            position: "absolute",
                                            bottom: 8,
                                            right: 8,
                                            background: "rgba(0,0,0,0.7)",
                                            padding: "2px 8px",
                                            borderRadius: 6,
                                            fontSize: 11,
                                            fontWeight: 600,
                                        }}
                                    >
                                        {formatDuration(clip.duration)}
                                    </div>
                                </div>

                                {/* Clip Info */}
                                <div style={{ padding: 16 }}>
                                    <h4
                                        style={{
                                            fontSize: 14,
                                            fontWeight: 600,
                                            marginBottom: 8,
                                            lineHeight: 1.4,
                                        }}
                                    >
                                        {clip.title}
                                    </h4>

                                    {/* Score Bar */}
                                    {clip.score != null && (
                                        <div style={{ marginBottom: 10 }}>
                                            <div
                                                style={{
                                                    display: "flex",
                                                    justifyContent: "space-between",
                                                    alignItems: "center",
                                                    marginBottom: 4,
                                                }}
                                            >
                                                <span
                                                    style={{
                                                        fontSize: 11,
                                                        fontWeight: 600,
                                                        color: "var(--text-secondary)",
                                                        textTransform: "uppercase",
                                                        letterSpacing: 0.5,
                                                    }}
                                                >
                                                    ⭐ Viral Score
                                                </span>
                                                <span
                                                    style={{
                                                        fontSize: 13,
                                                        fontWeight: 700,
                                                        color:
                                                            clip.score >= 0.8
                                                                ? "#34d399"
                                                                : clip.score >= 0.5
                                                                    ? "#fbbf24"
                                                                    : "#f87171",
                                                    }}
                                                >
                                                    {Math.round(clip.score * 100)}%
                                                </span>
                                            </div>
                                            <div
                                                style={{
                                                    width: "100%",
                                                    height: 6,
                                                    borderRadius: 3,
                                                    background: "rgba(255,255,255,0.06)",
                                                    overflow: "hidden",
                                                }}
                                            >
                                                <div
                                                    style={{
                                                        width: `${Math.round(clip.score * 100)}%`,
                                                        height: "100%",
                                                        borderRadius: 3,
                                                        background:
                                                            clip.score >= 0.8
                                                                ? "linear-gradient(90deg, #34d399, #10b981)"
                                                                : clip.score >= 0.5
                                                                    ? "linear-gradient(90deg, #fbbf24, #f59e0b)"
                                                                    : "linear-gradient(90deg, #f87171, #ef4444)",
                                                        transition: "width 0.5s ease",
                                                    }}
                                                />
                                            </div>
                                        </div>
                                    )}

                                    {/* Reason */}
                                    {clip.reason && (
                                        <p
                                            style={{
                                                fontSize: 12,
                                                color: "var(--text-secondary)",
                                                lineHeight: 1.5,
                                                marginBottom: 10,
                                                fontStyle: "italic",
                                            }}
                                        >
                                            💡 {clip.reason}
                                        </p>
                                    )}

                                    <div
                                        style={{
                                            display: "flex",
                                            gap: 12,
                                            fontSize: 12,
                                            color: "var(--text-secondary)",
                                            marginBottom: 12,
                                        }}
                                    >
                                        <span>
                                            🕐 {formatTimestamp(clip.start)} –{" "}
                                            {formatTimestamp(clip.end)}
                                        </span>
                                    </div>

                                    <div style={{ display: "flex", gap: 8 }}>
                                        <a
                                            href={`http://localhost:8000${clip.video_url}`}
                                            download
                                            style={{
                                                flex: 1,
                                                padding: "8px 12px",
                                                borderRadius: 8,
                                                background: "rgba(124,58,237,0.15)",
                                                border: "1px solid rgba(124,58,237,0.2)",
                                                color: "var(--accent-light)",
                                                textDecoration: "none",
                                                fontSize: 12,
                                                fontWeight: 600,
                                                textAlign: "center",
                                                transition: "all 0.2s",
                                            }}
                                        >
                                            📥 Download MP4
                                        </a>
                                        {clip.subtitle_url && (
                                            <a
                                                href={`http://localhost:8000${clip.subtitle_url}`}
                                                download
                                                style={{
                                                    flex: 1,
                                                    padding: "8px 12px",
                                                    borderRadius: 8,
                                                    background: "rgba(16,185,129,0.1)",
                                                    border: "1px solid rgba(16,185,129,0.2)",
                                                    color: "#34d399",
                                                    textDecoration: "none",
                                                    fontSize: 12,
                                                    fontWeight: 600,
                                                    textAlign: "center",
                                                    transition: "all 0.2s",
                                                }}
                                            >
                                                📝 Download SRT
                                            </a>
                                        )}
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* ── Empty state for no clips yet ─────────────── */}
            {job.status === "completed" &&
                (!job.clips || job.clips.length === 0) && (
                    <div
                        className="glass-card"
                        style={{ padding: 48, textAlign: "center" }}
                    >
                        <div style={{ fontSize: 48, marginBottom: 16 }}>🤔</div>
                        <h3 style={{ fontSize: 18, fontWeight: 600, marginBottom: 8 }}>
                            No highlights detected
                        </h3>
                        <p style={{ fontSize: 14, color: "var(--text-secondary)" }}>
                            The AI couldn't find strong highlight moments in this video. Try a
                            longer or more dynamic video.
                        </p>
                    </div>
                )}
        </div>
    );
}
