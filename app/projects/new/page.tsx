import { SourceInputBlock } from '@/components/project-setup/source-input-block';

export default function NewProjectPage() {
  return (
    <div className="space-y-6">
      <h2 className="text-lg font-semibold">New Project Wizard</h2>
      <section className="grid gap-3 md:grid-cols-2">
        <input className="rounded bg-slate-900 p-2" placeholder="Project title" />
        <input className="rounded bg-slate-900 p-2" placeholder="Topic/category" />
        <input className="rounded bg-slate-900 p-2" placeholder="Deadline (YYYY-MM-DD)" />
        <input className="rounded bg-slate-900 p-2" placeholder="Weekly time available (minutes)" />
      </section>
      <textarea className="w-full rounded bg-slate-900 p-2" placeholder="Why this matters" rows={3} />
      <textarea className="w-full rounded bg-slate-900 p-2" placeholder="Mastery goal" rows={3} />
      <SourceInputBlock />
      <button className="rounded bg-blue-600 px-4 py-2 text-sm font-medium">Generate Draft Plan</button>
    </div>
  );
}
