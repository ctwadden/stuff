const prompts = [
  'What is the main idea here?',
  'What assumption is hidden?',
  'How would you explain this simply?',
  'Where would a beginner go wrong?',
];

export default function SocraticPage() {
  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold">Socratic Coach</h2>
      <p className="text-sm text-slate-400">Concept: Ethics of AI governance</p>
      <div className="space-y-3">
        {prompts.map((question) => (
          <section key={question} className="rounded border border-slate-800 p-4">
            <p className="font-medium">{question}</p>
            <textarea className="mt-2 w-full rounded bg-slate-900 p-2" rows={3} placeholder="Answer from memory..." />
          </section>
        ))}
      </div>
    </div>
  );
}
