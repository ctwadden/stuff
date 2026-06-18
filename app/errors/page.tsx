import { mistakes } from '@/lib/mock/data';

export default function ErrorsPage() {
  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold">Error Log</h2>
      <ul className="space-y-2">
        {mistakes.map((mistake) => (
          <li key={mistake.id} className="rounded border border-slate-800 p-3 text-sm">
            <p className="font-medium">{mistake.errorType}</p>
            <p className="text-slate-300">{mistake.prompt}</p>
            <p className="text-xs text-slate-500">{mistake.createdAt}</p>
          </li>
        ))}
      </ul>
    </div>
  );
}
