export const DEFAULT_REVIEW_INTERVAL_DAYS = [0, 1, 3, 7, 14, 30] as const;

export function buildDefaultReviewDates(startDate: Date): Date[] {
  return DEFAULT_REVIEW_INTERVAL_DAYS.map((interval) => {
    const d = new Date(startDate);
    d.setDate(d.getDate() + interval);
    return d;
  });
}
