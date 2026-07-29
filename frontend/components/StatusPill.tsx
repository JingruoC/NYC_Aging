export function StatusPill({ status, label }: { status: "pass" | "warning" | "fail" | "brand"; label: string }) {
  return <span className={`pill ${status}`}>{label}</span>;
}

