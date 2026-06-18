import { projects, subskills, reviewItems } from '@/lib/mock/data';

export default function ProjectDetailPage({ params }: { params: { projectId: string } }) {
  const project = projects.find((p) => p.id === params.projectId) ?? projects[0];
  const projectSubskills = subskills.filter((s) => s.projectId === project.id);

  return (
    <div className="space-y-6">
      <section>
        <h2 className="text-xl font-semibold">{project.title}</h2>
        <p className="text-sm text-slate-400">{project.masteryGoal}</p>
      </section>

      <section className="rounded border border-slate-800 p-4">
        <h3 className="font-medium">Vital Few Subskills</h3>
        <ul className="mt-2 list-disc pl-5 text-sm">
          {projectSubskills.filter((s) => s.isVitalFew).map((s) => <li key={s.id}>{s.title}</li>)}
        </ul>
      </section>

      <section className="rounded border border-slate-800 p-4">
        <h3 className="font-medium">Upcoming Reviews</h3>
        <ul className="mt-2 list-disc pl-5 text-sm">
          {reviewItems.map((item) => <li key={item.id}>{item.prompt}</li>)}
        </ul>
      </section>
    </div>
  );
}
