import type { Project } from '@/lib/types';

export function ProjectCard({ project }: { project: Project }) {
  return (
    <article className="rounded border border-slate-800 p-4">
      <h3 className="font-medium">{project.title}</h3>
      <p className="mt-1 text-sm text-slate-400">{project.description}</p>
      <div className="mt-3 text-xs text-slate-500">
        <p>Deadline: {project.deadline}</p>
        <p>Weekly target: {project.weeklyTimeMinutes} min</p>
      </div>
    </article>
  );
}
