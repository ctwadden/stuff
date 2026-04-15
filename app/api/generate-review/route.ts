import { NextResponse } from 'next/server';

export async function POST(req: Request) {
  const body = await req.json();

  return NextResponse.json({
    message: 'Stub: generate-review',
    input: body,
    output: {
      recallQuestion: '',
      explainQuestion: '',
      transferQuestion: '',
    },
  });
}
