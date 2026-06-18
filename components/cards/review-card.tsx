import type { ReviewItem } from '@/lib/types';

export function ReviewCard({ item }: { item: ReviewItem }) {
  return (
    <article className="rounded border border-slate-800 p-4">
      <p className="text-sm">{item.prompt}</p>
      <p className="mt-2 text-xs text-slate-500">Due: {item.nextReviewAt}</p>
      <p className="text-xs text-slate-500">Last result: {item.lastResult}</p>
    </article>
  );
}
