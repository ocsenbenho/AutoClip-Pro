"use client";

import { useState, useEffect } from "react";

const API_BASE = "http://localhost:8000/api";

export default function JobsPage() {
    const [jobs, setJobs] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchJobs();
        const interval = setInterval(fetchJobs, 3000);
        return () => clearInterval(interval);
    }, []);

    async function fetchJobs() {
        try {
            const res = await fetch(`${API_BASE}/jobs`);
            if (res.ok) {
                const data = await res.json();
                setJobs(data);
            }
        } catch {
            // API not available
        } finally {
            setLoading(false);
        }
    }

    async function deleteJob(jobId, e) {
        e.preventDefault();
        e.stopPropagation();
        if (!confirm("Delete this job?")) return;

        try {
            const res = await fetch(`${API_BASE}/jobs/${jobId}`, {
                method: "DELETE",
            });
            if (res.ok) {
                setJobs(jobs.filter((j) => j.id !== jobId));
            }
        } catch {
            // ignore
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

    function formatTime(dt) {
        return new Date(dt).toLocaleString();
    }

    function formatDuration(seconds) {
        if (!seconds) return "";
        const m = Math.floor(seconds / 60);
        const s = Math.floor(seconds % 60);
        return `${m}m ${s}s`;
    }

    if (loading) {
        return (
            <div className="fade-in" style={{ textAlign: "center", paddingTop: 80 }}>
                <div
                    className="shimmer"
                    style={{
                        width: 200,
                        height: 24,
                        borderRadius: 8,
                        margin: "0 auto 12px",
                    }}
                />
                <div
                    className="shimmer"
                    style={{ width: 300, height: 16, borderRadius: 8, margin: "0 auto" }}
                />
            </div>
        );
    }

    return (
        <div className="fade-in">
            <div
                style={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                    marginBottom: 32,
                }}
            >
                <div>
                    <h1 style={{ fontSize: 30, fontWeight: 800, marginBottom: 6 }}>
                        Processing Jobs
                    </h1>
                    <p style={{ fontSize: 14, color: "var(--text-secondary)" }}>
                        {jobs.length} total job{jobs.length !== 1 ? "s" : ""}
                    </p>
                </div>
                <a href="/" className="btn-glow" style={{ textDecoration: "none" }}>
                    + New Job
                </a>
            </div>

            {jobs.length === 0 ? (
                <div
                    className="glass-card"
                    style={{ padding: 48, textAlign: "center" }}
                >
                    <div style={{ fontSize: 48, marginBottom: 16 }}>📭</div>
                    <h3 style={{ fontSize: 18, fontWeight: 600, marginBottom: 8 }}>
                        No jobs yet
                    </h3>
                    <p style={{ fontSize: 14, color: "var(--text-secondary)" }}>
                        Submit a YouTube URL from the{" "}
                        <a href="/" style={{ color: "var(--accent-light)" }}>
                            dashboard
                        </a>{" "}
                        to get started.
                    </p>
                </div>
            ) : (
                <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
                    {jobs.map((job) => (
                        <a
                            key={job.id}
                            href={`/jobs/${job.id}`}
                            className="glass-card"
                            style={{
                                padding: 20,
                                textDecoration: "none",
                                color: "inherit",
                                cursor: "pointer",
                            }}
                        >
                            <div
                                style={{
                                    display: "flex",
                                    justifyContent: "space-between",
                                    alignItems: "flex-start",
                                    gap: 16,
                                }}
                            >
                                <div style={{ flex: 1, minWidth: 0 }}>
                                    <div
                                        style={{
                                            display: "flex",
                                            alignItems: "center",
                                            gap: 10,
                                            marginBottom: 8,
                                        }}
                                    >
                                        <span
                                            style={{
                                                fontSize: 13,
                                                color: "var(--text-secondary)",
                                                fontFamily: "monospace",
                                            }}
                                        >
                                            #{job.id}
                                        </span>
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

                                    <div
                                        style={{
                                            fontSize: 15,
                                            fontWeight: 600,
                                            marginBottom: 6,
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
                                            display: "flex",
                                            gap: 16,
                                            flexWrap: "wrap",
                                        }}
                                    >
                                        <span>📅 {formatTime(job.created_at)}</span>
                                        {job.video_duration && (
                                            <span>⏱️ {formatDuration(job.video_duration)}</span>
                                        )}
                                        {job.clips_count > 0 && (
                                            <span>🎬 {job.clips_count} clips</span>
                                        )}
                                        {job.progress_message && (
                                            <span
                                                style={{
                                                    color: isActive(job.status)
                                                        ? "var(--accent-light)"
                                                        : "var(--text-secondary)",
                                                }}
                                            >
                                                {job.progress_message}
                                            </span>
                                        )}
                                    </div>
                                </div>

                                <div
                                    style={{
                                        display: "flex",
                                        alignItems: "center",
                                        gap: 8,
                                        flexShrink: 0,
                                    }}
                                >
                                    {(job.status === "completed" || job.status === "failed") && (
                                        <button
                                            onClick={(e) => deleteJob(job.id, e)}
                                            style={{
                                                background: "rgba(239,68,68,0.1)",
                                                border: "1px solid rgba(239,68,68,0.2)",
                                                borderRadius: 8,
                                                padding: "6px 12px",
                                                color: "#f87171",
                                                fontSize: 12,
                                                cursor: "pointer",
                                                transition: "all 0.2s",
                                            }}
                                        >
                                            Delete
                                        </button>
                                    )}
                                    <span
                                        style={{
                                            color: "var(--text-secondary)",
                                            fontSize: 18,
                                        }}
                                    >
                                        →
                                    </span>
                                </div>
                            </div>
                        </a>
                    ))}
                </div>
            )}
        </div>
    );
}
