import { reviewItems } from '@/lib/mock/data';
import { DEFAULT_REVIEW_INTERVAL_DAYS } from '@/lib/utils/review-schedule';

export default function ReviewsPage() {
  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold">Review Calendar</h2>
      <p className="text-sm text-slate-400">Default intervals: {DEFAULT_REVIEW_INTERVAL_DAYS.join(', ')} days</p>
      <ul className="space-y-2">
        {reviewItems.map((item) => (
          <li key={item.id} className="rounded border border-slate-800 p-3 text-sm">
            {item.nextReviewAt}: {item.prompt}
          </li>
        ))}
      </ul>
    </div>
  );
}
