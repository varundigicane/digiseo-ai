import Link from "next/link";

const agents = [
  "Website SEO",
  "AEO",
  "Content",
  "Social",
  "Competitor",
  "Keywords",
  "Backlinks",
  "PPC",
  "Analytics",
  "Local SEO",
];

export default function HomePage() {
  return (
    <main className="relative overflow-hidden">
      <div
        aria-hidden
        className="pointer-events-none absolute inset-0 animate-pulse-glow"
        style={{
          backgroundImage:
            "linear-gradient(rgba(232,240,235,0.04) 1px, transparent 1px), linear-gradient(90deg, rgba(232,240,235,0.04) 1px, transparent 1px)",
          backgroundSize: "64px 64px",
          maskImage: "radial-gradient(ellipse at center, black 20%, transparent 70%)",
        }}
      />

      <header className="relative z-10 mx-auto flex max-w-6xl items-center justify-between px-6 py-6">
        <div className="font-display text-2xl tracking-tight text-accent">DigiSEO AI</div>
        <nav className="flex items-center gap-4 text-sm text-muted">
          <a href="#agents" className="hover:text-ink">
            Agents
          </a>
          <a href="#pricing" className="hover:text-ink">
            Pricing
          </a>
          <Link
            href="/login"
            className="rounded-full border border-[var(--line)] px-4 py-2 text-ink hover:border-accent/40"
          >
            Sign in
          </Link>
          <Link
            href="/signup"
            className="rounded-full bg-accent px-4 py-2 font-medium text-[#04140e] hover:brightness-110"
          >
            Start free
          </Link>
        </nav>
      </header>

      <section className="relative z-10 mx-auto flex min-h-[78vh] max-w-6xl flex-col justify-center px-6 pb-20 pt-8">
        <p className="animate-rise mb-4 text-sm uppercase tracking-[0.2em] text-accent/80">
          Digicane Systems
        </p>
        <h1 className="animate-rise font-display max-w-4xl text-5xl leading-[1.05] tracking-tight text-ink md:text-7xl">
          DigiSEO AI
        </h1>
        <p
          className="animate-rise mt-6 max-w-xl text-lg text-muted md:text-xl"
          style={{ animationDelay: "120ms" }}
        >
          A self-serve team of marketing agents for SEO, answer engines, content, and growth —
          built for startups and SMBs.
        </p>
        <div className="animate-rise mt-10 flex flex-wrap gap-4" style={{ animationDelay: "220ms" }}>
          <Link
            href="/signup"
            className="rounded-full bg-accent px-7 py-3 text-base font-semibold text-[#04140e] hover:brightness-110"
          >
            Run your first audit
          </Link>
          <a
            href="#agents"
            className="rounded-full border border-[var(--line)] px-7 py-3 text-ink hover:border-accent/40"
          >
            Meet the agents
          </a>
        </div>
        <div
          className="animate-drift pointer-events-none absolute right-0 top-24 hidden h-72 w-72 rounded-full md:block"
          style={{
            background:
              "radial-gradient(circle at 30% 30%, rgba(61,255,168,0.35), transparent 60%)",
            filter: "blur(8px)",
          }}
        />
      </section>

      <section id="agents" className="relative z-10 border-t border-[var(--line)] py-20">
        <div className="mx-auto max-w-6xl px-6">
          <h2 className="font-display text-3xl md:text-4xl">Ten specialists. One orchestrator.</h2>
          <p className="mt-3 max-w-2xl text-muted">
            LangGraph routes work across SEO, AEO, content, social, competitor intel, keywords,
            outreach, PPC, analytics, and local SEO — with human approval before live changes.
          </p>
          <ul className="mt-10 grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
            {agents.map((name, i) => (
              <li
                key={name}
                className="animate-rise border border-[var(--line)] bg-elevated/60 px-4 py-5"
                style={{ animationDelay: `${i * 40}ms` }}
              >
                <span className="text-xs text-accent">0{i + 1 > 9 ? "" : ""}{i + 1}</span>
                <div className="mt-2 font-medium">{name}</div>
              </li>
            ))}
          </ul>
        </div>
      </section>

      <section id="pricing" className="relative z-10 border-t border-[var(--line)] py-20">
        <div className="mx-auto max-w-6xl px-6">
          <h2 className="font-display text-3xl md:text-4xl">Simple SaaS pricing</h2>
          <div className="mt-10 grid gap-6 md:grid-cols-3">
            {[
              { name: "Starter", price: 49, blurb: "SEO + AEO audits, blogs, GSC" },
              { name: "Professional", price: 149, blurb: "Social, calendar, analytics, competitors" },
              { name: "Business", price: 399, blurb: "Multi-agent workflows, PPC, outreach, API" },
            ].map((plan) => (
              <div key={plan.name} className="border border-[var(--line)] bg-surface/80 p-6">
                <div className="text-sm uppercase tracking-wider text-muted">{plan.name}</div>
                <div className="mt-3 font-display text-4xl">
                  ${plan.price}
                  <span className="text-base text-muted">/mo</span>
                </div>
                <p className="mt-3 text-sm text-muted">{plan.blurb}</p>
                <Link
                  href="/signup"
                  className="mt-6 inline-block text-sm font-medium text-accent hover:underline"
                >
                  Get started →
                </Link>
              </div>
            ))}
          </div>
        </div>
      </section>

      <footer className="border-t border-[var(--line)] py-10 text-center text-sm text-muted">
        DigiSEO AI · Digicane Systems · Enterprise multi-agent marketing
      </footer>
    </main>
  );
}
