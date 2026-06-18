import { NextResponse } from 'next/server';

export async function POST(req: Request) {
  const body = await req.json();

  return NextResponse.json({
    message: 'Stub: grade-recall',
    input: body,
    output: {
      correctness: 'partial',
      missingIdeas: [],
      mistakenIdeas: [],
      repairSuggestion: '',
      reviewIntervalSignal: 'shorter',
    },
  });
}
