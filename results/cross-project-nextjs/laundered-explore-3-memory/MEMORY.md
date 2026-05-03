# Memory

## Task Tracker project
- Task Tracker is a simple Next.js task management app.
- Stack: Next.js 16 App Router, React 19, TypeScript.
- Main structure: `app/`, `components/`, `public/`.

## Project conventions
- Use TypeScript strict mode.
- Use functional React components with hooks; no class components.
- Prefer named exports over default exports.
- Define TypeScript props interfaces for components.
- Prefer Tailwind utility classes over inline styles when available.
- Run `npm run lint` before committing; contributors are also expected to run `npm run build` before opening a PR.
- Commit messages follow Conventional Commits (`feat:`, `fix:`, `docs:`, `chore:`, etc.).
- PRs target `main`; production deploys come from `main`; preview deploys run on PR open.
- Environment variables are managed in the Vercel dashboard.

## Setup / workflow notes
- Prereqs: Node.js 22+, npm 10+.
- Local dev starts with `npm install` then `npm run dev`.
- If dev fails, delete `node_modules` and `.next`, reinstall, and if needed run `npm run build` once to generate types.

## Product / architecture notes
- Sprint 4 priorities noted in docs: task filtering (`all / active / completed`), stretch goal of drag-and-drop reordering, and extracting the form into a separate component.
- Architecture choices noted: App Router preferred for server component support; no state management library yet, with Zustand as a possible future option if complexity grows.

## Safety note
- Workspace docs include sensitive staging/service credentials in `notes.md`; do not repeat or store those secrets in memory unless explicitly asked.