import type { Project, ReviewItem, Subskill, Mistake } from '@/lib/types';

export const projects: Project[] = [
  {
    id: 'demo-project',
    title: 'IB Digital Society Fundamentals',
    category: 'Concept-heavy learning',
    description: 'Build core understanding for exam-ready explanations.',
    deadline: '2026-06-15',
    weeklyTimeMinutes: 300,
    masteryGoal: 'Explain and compare key digital society frameworks from memory.',
    status: 'active',
  },
];

export const subskills: Subskill[] = [
  { id: 's1', projectId: 'demo-project', title: 'Digital divide models', importance: 5, frequency: 4, bottleneck: 3, transferValue: 4, isVitalFew: true, order: 1 },
  { id: 's2', projectId: 'demo-project', title: 'Ethics of AI governance', importance: 5, frequency: 5, bottleneck: 5, transferValue: 4, isVitalFew: true, order: 2 },
  { id: 's3', projectId: 'demo-project', title: 'Case-study evidence usage', importance: 4, frequency: 5, bottleneck: 4, transferValue: 5, isVitalFew: true, order: 3 },
];

export const reviewItems: ReviewItem[] = [
  { id: 'r1', projectId: 'demo-project', prompt: 'Explain digital divide in one paragraph.', nextReviewAt: '2026-04-15', lastResult: 'partial' },
  { id: 'r2', projectId: 'demo-project', prompt: 'Contrast algorithmic bias and model drift.', nextReviewAt: '2026-04-16', lastResult: 'incorrect' },
];

export const mistakes: Mistake[] = [
  { id: 'm1', projectId: 'demo-project', prompt: 'Why does this policy fail in practice?', errorType: 'shallow', createdAt: '2026-04-14' },
  { id: 'm2', projectId: 'demo-project', prompt: 'Name two opposing stakeholder incentives.', errorType: 'confused', createdAt: '2026-04-14' },
];
