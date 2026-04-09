import { cn } from "@/lib/utils";

export function PrismPage({
  variant = "default",
  className,
  children,
  ...props
}: React.HTMLAttributes<HTMLDivElement> & {
  variant?: "default" | "dashboard" | "workspace" | "report" | "form";
}) {
  return (
    <div className={cn("prism-page", `prism-page-${variant}`, className)} {...props}>
      {children}
    </div>
  );
}

export function PrismSection({
  className,
  children,
  ...props
}: React.HTMLAttributes<HTMLElement>) {
  return <section className={cn("prism-section", className)} {...props}>{children}</section>;
}

export function PrismPanel({
  className,
  children,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) {
  return <div className={cn("prism-panel", className)} {...props}>{children}</div>;
}

export function PrismHeroKicker({
  className,
  children,
}: {
  className?: string;
  children: React.ReactNode;
}) {
  return <div className={cn("prism-kicker", className)}>{children}</div>;
}

export function PrismPageIntro({
  className,
  kicker,
  title,
  description,
  aside,
}: {
  className?: string;
  kicker?: React.ReactNode;
  title: React.ReactNode;
  description?: React.ReactNode;
  aside?: React.ReactNode;
}) {
  return (
    <div className={cn("prism-page-intro", className)}>
      <div className="prism-intro-main prism-hero-copy space-y-4">
        {kicker ? <div className="prism-intro-kicker">{kicker}</div> : null}
        <div className="space-y-3">
          <h1 className="prism-intro-title prism-title text-3xl font-black leading-[1.02] text-[var(--text-primary)] md:text-4xl xl:text-[2.95rem]">
            {title}
          </h1>
          {description ? (
            <p className="prism-intro-description max-w-3xl text-sm leading-7 text-[var(--text-secondary)] md:text-base">
              {description}
            </p>
          ) : null}
        </div>
      </div>
      {aside ? <div className="prism-hero-support prism-intro-aside">{aside}</div> : null}
    </div>
  );
}

export function PrismSectionHeader({
  className,
  kicker,
  title,
  description,
  actions,
}: {
  className?: string;
  kicker?: React.ReactNode;
  title: React.ReactNode;
  description?: React.ReactNode;
  actions?: React.ReactNode;
}) {
  return (
    <div className={cn("prism-section-header", className)}>
      <div className="space-y-1">
        {kicker ? (
          <p className="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--text-muted)]">
            {kicker}
          </p>
        ) : null}
        <h2 className="text-base font-semibold text-[var(--text-primary)]">{title}</h2>
        {description ? (
          <p className="text-sm leading-6 text-[var(--text-secondary)]">{description}</p>
        ) : null}
      </div>
      {actions ? <div className="prism-section-actions">{actions}</div> : null}
    </div>
  );
}
