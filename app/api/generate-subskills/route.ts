import { NextResponse } from 'next/server';

export async function POST(req: Request) {
  const body = await req.json();

  return NextResponse.json({
    message: 'Stub: generate-subskills',
    input: body,
    output: {
      subskills: [],
      ranking: [],
      bottlenecks: [],
    },
  });
}
