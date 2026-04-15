# Learning OS MVP Skeleton

This repository contains a Next.js (App Router) starter skeleton for the Learning OS MVP.

## Included

- Route structure for key MVP pages
- Shared layout with sidebar + header
- Mock data for projects, subskills, reviews, and mistakes
- Firebase-ready client/server placeholders
- API route stubs for planned AI endpoints

## Routes

- `/dashboard`
- `/projects/new`
- `/projects/[projectId]`
- `/mapper`
- `/socratic`
- `/study`
- `/reviews`
- `/errors`

## API stubs

- `POST /api/create-project`
- `POST /api/generate-subskills`
- `POST /api/generate-socratic`
- `POST /api/grade-recall`
- `POST /api/generate-review`
- `POST /api/generate-transfer`

## Preview the app locally

1. Install dependencies:

   ```bash
   npm install
   ```

2. Start the app:

   ```bash
   npm run dev
   ```

   or to expose on your network:

   ```bash
   npm run dev:host
   ```

3. Open:

   - http://localhost:3000
   - (or your machine IP on port 3000 when using `dev:host`)

## Note about this environment

In this execution environment, `npm install` failed with a registry access restriction (HTTP 403).
If you run this on your local machine with normal npm access, preview should work with the commands above.
