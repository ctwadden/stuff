export function SourceInputBlock() {
  return (
    <div className="space-y-2 rounded border border-slate-800 p-4">
      <h3 className="font-medium">Sources</h3>
      <input className="w-full rounded bg-slate-900 p-2 text-sm" placeholder="YouTube / URL / notes" />
      <p className="text-xs text-slate-500">PDF upload will be added in a later phase.</p>
    </div>
  );
}
