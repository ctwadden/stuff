export function SessionTimer({ label, minutes }: { label: string; minutes: number }) {
  return (
    <div className="rounded border border-slate-800 p-3">
      <p className="text-sm text-slate-400">{label}</p>
      <p className="text-lg font-semibold">{minutes} min</p>
    </div>
  );
}
