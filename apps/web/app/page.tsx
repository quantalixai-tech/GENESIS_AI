import styles from "./page.module.css";

export default function Home() {
  return (
    <main className={styles.main}>
      {/* Background gradient orbs */}
      <div className={styles.orb} aria-hidden="true" />
      <div className={styles.orbSecondary} aria-hidden="true" />

      {/* Navigation */}
      <nav className={styles.nav}>
        <div className={styles.navBrand}>
          <span className={styles.navLogo}>⬡</span>
          <span className={styles.navName}>GENESIS AI</span>
        </div>
        <div className={styles.navLinks}>
          <a
            href="http://localhost:8080/docs"
            className={styles.navLink}
            target="_blank"
            rel="noopener noreferrer"
            id="api-docs-link"
          >
            API Docs
          </a>
          <a
            href="/dashboard"
            className={styles.navLinkPrimary}
            id="get-started-nav-link"
          >
            Get Started
          </a>
        </div>
      </nav>

      {/* Hero */}
      <section className={styles.hero}>
        <div className={styles.heroBadge}>
          <span className={styles.heroBadgeDot} />
          Platform v0.3 — Foundation
        </div>

        <h1 className={styles.heroTitle}>
          Build Software with
          <br />
          <span className={styles.heroAccent}>Natural Language</span>
        </h1>

        <p className={styles.heroSubtitle}>
          Describe what you want to build. GENESIS AI understands your idea,
          designs the application, generates production-ready code, validates it
          automatically, and repairs failures — without you writing a single line.
        </p>

        <div className={styles.heroCta}>
          <a
            href="/dashboard"
            className={styles.ctaPrimary}
            id="start-project-btn"
          >
            Start a Project
            <span className={styles.ctaArrow}>→</span>
          </a>
          <a
            href="https://github.com/quantalixai-tech/GENESIS_AI"
            className={styles.ctaSecondary}
            target="_blank"
            rel="noopener noreferrer"
            id="view-source-btn"
          >
            View Source
          </a>
        </div>
      </section>

      {/* Pipeline visualization */}
      <section className={styles.pipeline} aria-label="Platform pipeline">
        <div className={styles.pipelineSteps}>
          {PIPELINE_STEPS.map((step, i) => (
            <div key={step.label} className={styles.pipelineStep}>
              <div className={styles.pipelineIcon} aria-hidden="true">
                {step.icon}
              </div>
              <div className={styles.pipelineLabel}>{step.label}</div>
              {i < PIPELINE_STEPS.length - 1 && (
                <div className={styles.pipelineArrow} aria-hidden="true">
                  →
                </div>
              )}
            </div>
          ))}
        </div>
      </section>

      {/* Feature grid */}
      <section className={styles.features} aria-label="Platform features">
        <h2 className={styles.sectionTitle}>Built for the AI-Native Era</h2>
        <div className={styles.featureGrid}>
          {FEATURES.map((feature) => (
            <article key={feature.title} className={styles.featureCard}>
              <div className={styles.featureIcon} aria-hidden="true">
                {feature.icon}
              </div>
              <h3 className={styles.featureTitle}>{feature.title}</h3>
              <p className={styles.featureDescription}>{feature.description}</p>
            </article>
          ))}
        </div>
      </section>

      {/* Infrastructure status */}
      <section className={styles.status} aria-label="Platform status">
        <h2 className={styles.sectionTitle}>Infrastructure</h2>
        <div className={styles.statusGrid}>
          {STATUS_ITEMS.map((item) => (
            <div key={item.name} className={styles.statusCard}>
              <div
                className={`${styles.statusDot} ${
                  item.active ? styles.statusDotActive : styles.statusDotPlanned
                }`}
                aria-label={item.active ? "Active" : "Planned"}
              />
              <div className={styles.statusInfo}>
                <div className={styles.statusName}>{item.name}</div>
                <div className={styles.statusDetail}>{item.detail}</div>
              </div>
              <div
                className={`${styles.statusBadge} ${
                  item.active
                    ? styles.statusBadgeActive
                    : styles.statusBadgePlanned
                }`}
              >
                {item.active ? "Active" : "Planned"}
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Footer */}
      <footer className={styles.footer}>
        <p className={styles.footerText}>
          GENESIS AI Platform — Phase 0.3 Foundation
        </p>
        <p className={styles.footerMuted}>
          API running at{" "}
          <a
            href="http://localhost:8080/docs"
            className={styles.footerLink}
            target="_blank"
            rel="noopener noreferrer"
          >
            localhost:8080
          </a>
        </p>
      </footer>
    </main>
  );
}

// ---------------------------------------------------------------------------
// Data
// ---------------------------------------------------------------------------

const PIPELINE_STEPS = [
  { icon: "💬", label: "Describe" },
  { icon: "🧠", label: "Understand" },
  { icon: "📐", label: "Design" },
  { icon: "⚙️", label: "Generate" },
  { icon: "✅", label: "Validate" },
  { icon: "🔧", label: "Repair" },
  { icon: "🚀", label: "Ready" },
];

const FEATURES = [
  {
    icon: "💬",
    title: "Conversational Requirements",
    description:
      "Describe your application in plain language. The AI asks targeted questions, extracts structured requirements, and confirms understanding before building.",
  },
  {
    icon: "🤖",
    title: "Specialized AI Agents",
    description:
      "A team of purpose-built agents handles requirements, architecture, database design, frontend, backend, testing, and repair — each with defined boundaries and governance.",
  },
  {
    icon: "⚡",
    title: "Live Preview",
    description:
      "Generated code is reflected in a live UI preview immediately. See your application take shape in real time without touching source code.",
  },
  {
    icon: "🔍",
    title: "Automatic Validation",
    description:
      "Every generated change is compiled, type-checked, linted, and tested automatically. Validation failures trigger the repair agent before you ever see them.",
  },
  {
    icon: "🛡️",
    title: "AI Governance",
    description:
      "Every AI action is traceable. Models, prompts, and agents are registered and versioned. High-risk operations require human approval before execution.",
  },
  {
    icon: "📦",
    title: "Git Project History",
    description:
      "Every meaningful change is committed with full traceability back to the user request, requirement, and AI agent. Restore any previous working state.",
  },
];

const STATUS_ITEMS = [
  { name: "PostgreSQL", detail: "Primary database — genesis:5432", active: true },
  { name: "NATS", detail: "Event bus — genesis:4222", active: true },
  { name: "MinIO", detail: "Object storage — genesis:9000", active: true },
  { name: "FastAPI", detail: "Core API — localhost:8080", active: true },
  { name: "Worker", detail: "NATS consumer", active: true },
  { name: "AI Engine", detail: "Model routing — Phase 1.0", active: false },
  { name: "Ollama", detail: "Local LLM runtime — Phase 1.0", active: false },
  { name: "Observability", detail: "Prometheus / Grafana — Phase 1.0", active: false },
];
