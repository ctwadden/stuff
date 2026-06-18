export type ReflectionTag = 'clear' | 'repeat_only' | 'unsure' | 'confused' | 'need_example';

export interface Project {
  id: string;
  title: string;
  category: string;
  description: string;
  deadline: string;
  weeklyTimeMinutes: number;
  masteryGoal: string;
  status: 'active' | 'paused' | 'completed';
}

export interface Subskill {
  id: string;
  projectId: string;
  title: string;
  importance: number;
  frequency: number;
  bottleneck: number;
  transferValue: number;
  isVitalFew: boolean;
  order: number;
}

export interface ReviewItem {
  id: string;
  projectId: string;
  prompt: string;
  nextReviewAt: string;
  lastResult: 'correct' | 'partial' | 'incorrect';
}

export interface Mistake {
  id: string;
  projectId: string;
  prompt: string;
  errorType: 'forgotten' | 'confused' | 'procedural' | 'shallow' | 'transfer';
  createdAt: string;
}
