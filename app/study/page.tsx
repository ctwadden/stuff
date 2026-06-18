import { SessionTimer } from '@/components/session/session-timer';

const blocks = [
  ['Mission', 5],
  ['80/20 preview', 10],
  ['Focused input', 15],
  ['Socratic phase', 15],
  ['Direct practice', 20],
  ['Weak-link drill', 10],
  ['Retrieval', 10],
  ['Close + schedule', 5],
] as const;

export default function StudyPage() {
  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold">Study Session</h2>
      <div className="grid gap-3 md:grid-cols-4">
        {blocks.map(([label, minutes]) => (
          <SessionTimer key={label} label={label} minutes={minutes} />
        ))}
      </div>
      <section className="rounded border border-slate-800 p-4">
        <h3 className="font-medium">Retrieval Scratchpad</h3>
        <textarea className="mt-2 w-full rounded bg-slate-900 p-2" rows={8} placeholder="Close notes and answer from memory..." />
      </section>
    </div>
  );
}
