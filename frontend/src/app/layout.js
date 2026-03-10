import "./globals.css";

export const metadata = {
  title: "AutoClip Pro – AI Video Highlight Generator",
  description:
    "Transform long videos into engaging short clips with AI-powered highlight detection, automatic transcription, and subtitle generation.",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <head>
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap"
          rel="stylesheet"
        />
      </head>
      <body>
        {/* ── Navigation Bar ─────────────────────────────── */}
        <nav
          style={{
            position: "sticky",
            top: 0,
            zIndex: 50,
            backdropFilter: "blur(16px)",
            background: "rgba(10, 10, 15, 0.8)",
            borderBottom: "1px solid rgba(255,255,255,0.06)",
          }}
        >
          <div
            style={{
              maxWidth: 1200,
              margin: "0 auto",
              padding: "16px 24px",
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
            }}
          >
            <a
              href="/"
              style={{
                display: "flex",
                alignItems: "center",
                gap: 10,
                textDecoration: "none",
                color: "var(--text-primary)",
              }}
            >
              <span style={{ fontSize: 28 }}>⚡</span>
              <span
                style={{
                  fontWeight: 800,
                  fontSize: 20,
                  background: "linear-gradient(135deg, #a78bfa, #7c3aed)",
                  WebkitBackgroundClip: "text",
                  WebkitTextFillColor: "transparent",
                }}
              >
                AutoClip Pro
              </span>
            </a>
            <div style={{ display: "flex", gap: 24, alignItems: "center" }}>
              <a
                href="/"
                style={{
                  color: "var(--text-secondary)",
                  textDecoration: "none",
                  fontSize: 14,
                  fontWeight: 500,
                  transition: "color 0.2s",
                }}
              >
                Dashboard
              </a>
              <a
                href="/jobs"
                style={{
                  color: "var(--text-secondary)",
                  textDecoration: "none",
                  fontSize: 14,
                  fontWeight: 500,
                  transition: "color 0.2s",
                }}
              >
                Jobs
              </a>
            </div>
          </div>
        </nav>

        {/* ── Main Content ───────────────────────────────── */}
        <main
          style={{
            maxWidth: 1200,
            margin: "0 auto",
            padding: "32px 24px 64px",
          }}
        >
          {children}
        </main>
      </body>
    </html>
  );
}
