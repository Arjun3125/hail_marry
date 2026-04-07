export function PrismBackdrop() {
  return (
    <div aria-hidden="true" className="pointer-events-none fixed inset-0 z-0 overflow-hidden">
      <div className="prism-grid absolute inset-0 opacity-50" />
      <div className="prism-noise absolute inset-0 opacity-40" />
      <div className="prism-orb prism-orb-a" />
      <div className="prism-orb prism-orb-b" />
      <div className="prism-orb prism-orb-c" />
      <div className="prism-radial absolute inset-x-0 top-0 h-[48rem]" />
      <div className="prism-horizon absolute inset-x-0 bottom-0 h-[18rem]" />
    </div>
  );
}

