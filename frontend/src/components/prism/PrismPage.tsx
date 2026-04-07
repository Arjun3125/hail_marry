import { cn } from "@/lib/utils";

export function PrismPage({
  className,
  children,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) {
  return <div className={cn("prism-page", className)} {...props}>{children}</div>;
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
      <div className="space-y-4">
        {kicker ? <div>{kicker}</div> : null}
        <div className="space-y-3">
          <h1 className="prism-title text-4xl font-black leading-[0.98] text-[var(--text-primary)] md:text-5xl">
            {title}
          </h1>
          {description ? (
            <p className="max-w-3xl text-base leading-7 text-[var(--text-secondary)] md:text-lg">
              {description}
            </p>
          ) : null}
        </div>
      </div>
      {aside ? <div>{aside}</div> : null}
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
      {actions ? <div>{actions}</div> : null}
    </div>
  );
}
