import { NextResponse } from 'next/server';

export async function POST(req: Request) {
  const body = await req.json();

  return NextResponse.json({
    message: 'Stub: create-project',
    input: body,
    output: {
      project: null,
      draftSubskills: [],
      firstStudyPlan: null,
    },
  });
}
