import { ProjectCard } from '@/components/cards/project-card';
import { ReviewCard } from '@/components/cards/review-card';
import { MasteryChart } from '@/components/dashboard/mastery-chart';
import { projects, reviewItems, mistakes } from '@/lib/mock/data';

export default function DashboardPage() {
  return (
    <div className="space-y-6">
      <section>
        <h2 className="mb-3 text-lg font-semibold">Active Projects</h2>
        <div className="grid gap-3 md:grid-cols-2">{projects.map((project) => <ProjectCard key={project.id} project={project} />)}</div>
      </section>

      <section>
        <h2 className="mb-3 text-lg font-semibold">Reviews Due</h2>
        <div className="grid gap-3 md:grid-cols-2">{reviewItems.map((item) => <ReviewCard key={item.id} item={item} />)}</div>
      </section>

      <section className="rounded border border-slate-800 p-4">
        <h2 className="text-lg font-semibold">Weak-link Alerts</h2>
        <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-slate-300">
          {mistakes.map((mistake) => (
            <li key={mistake.id}>
              {mistake.errorType}: {mistake.prompt}
            </li>
          ))}
        </ul>
      </section>

      <MasteryChart />
    </div>
  );
}
