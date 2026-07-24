import Link from "next/link";

const pillars = [
  "Strategy & Audit",
  "AI SEO",
  "On-Page SEO",
  "CRO",
  "Off-Page SEO",
  "Local SEO",
  "Paid Media",
  "SMM",
  "Email",
  "Content",
  "Reporting",
];

const hierarchy = [
  "Audit what is broken",
  "Fix discoverability (AI SEO + On-Page)",
  "Create assets (Content)",
  "Improve conversion (CRO)",
  "Earn authority & local",
  "Amplify with Paid, Social & Email",
  "Report & iterate",
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
          <a href="#pillars" className="hover:text-ink">
            Services
          </a>
          <a href="#playbook" className="hover:text-ink">
            Playbook
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
          Digicane Systems · AI Growth OS
        </p>
        <h1 className="animate-rise font-display max-w-4xl text-5xl leading-[1.05] tracking-tight text-ink md:text-7xl">
          DigiSEO AI
        </h1>
        <p
          className="animate-rise mt-6 max-w-xl text-lg text-muted md:text-xl"
          style={{ animationDelay: "120ms" }}
        >
          Run the full SEO & growth playbook — Strategy, AI SEO, On-Page, CRO, Off-Page, Local,
          Paid, Social, and Email — with human approval before live changes.
        </p>
        <div className="animate-rise mt-10 flex flex-wrap gap-4" style={{ animationDelay: "220ms" }}>
          <Link
            href="/signup"
            className="rounded-full bg-accent px-7 py-3 text-base font-semibold text-[#04140e] hover:brightness-110"
          >
            Start Strategy & Audit
          </Link>
          <a
            href="#playbook"
            className="rounded-full border border-[var(--line)] px-7 py-3 text-ink hover:border-accent/40"
          >
            See the hierarchy
          </a>
        </div>
      </section>

      <section id="pillars" className="relative z-10 border-t border-[var(--line)] py-20">
        <div className="mx-auto max-w-6xl px-6">
          <h2 className="font-display text-3xl md:text-4xl">Service pillars, not scattered tools</h2>
          <p className="mt-3 max-w-2xl text-muted">
            Keywords, competitors, backlinks, and analytics live inside these pillars — the way SEO
            executives plan delivery.
          </p>
          <ul className="mt-10 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
            {pillars.map((name, i) => (
              <li
                key={name}
                className="animate-rise border border-[var(--line)] bg-elevated/60 px-4 py-5"
                style={{ animationDelay: `${i * 30}ms` }}
              >
                <span className="text-xs text-accent">{String(i + 1).padStart(2, "0")}</span>
                <div className="mt-2 font-medium">{name}</div>
              </li>
            ))}
          </ul>
          <p className="mt-8 text-sm text-muted">
            Web design & hosting stay with partners — DigiSEO exports CWV/design briefs from
            Settings.
          </p>
        </div>
      </section>

      <section id="playbook" className="relative z-10 border-t border-[var(--line)] py-20">
        <div className="mx-auto max-w-6xl px-6">
          <h2 className="font-display text-3xl md:text-4xl">What we do, in order</h2>
          <ol className="mt-10 max-w-2xl space-y-4">
            {hierarchy.map((step, i) => (
              <li key={step} className="flex gap-4 border-b border-[var(--line)] pb-4 text-muted">
                <span className="font-display text-accent">{i + 1}</span>
                <span className="text-ink">{step}</span>
              </li>
            ))}
          </ol>
        </div>
      </section>

      <section id="pricing" className="relative z-10 border-t border-[var(--line)] py-20">
        <div className="mx-auto max-w-6xl px-6">
          <h2 className="font-display text-3xl md:text-4xl">Simple SaaS pricing</h2>
          <div className="mt-10 grid gap-6 md:grid-cols-3">
            {[
              {
                name: "Starter",
                price: 49,
                blurb: "Strategy & Audit, AI SEO, On-Page, blog content",
              },
              {
                name: "Professional",
                price: 149,
                blurb: "CRO, SMM, reporting, competitors-as-capability",
              },
              {
                name: "Business",
                price: 399,
                blurb: "Off-Page, Local, Paid (Google+Meta), Email, Growth Playbook",
              },
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
        DigiSEO AI · Digicane Systems · AI Growth OS for SMBs & agencies
      </footer>
    </main>
  );
}
