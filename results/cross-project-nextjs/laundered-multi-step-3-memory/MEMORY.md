# Memory

## Task Tracker project conventions
- Project is a simple Next.js task management app called Task Tracker.
- Stack: Next.js 16 App Router, React 19, TypeScript.
- Main structure: `app/`, `components/`, `public/`.
- Prereqs: Node.js 22+, npm 10+.
- Standard local setup/run flow: `npm install`, then `npm run dev`.
- If first-run TypeScript issues appear, run `npm run build` once to generate types.
- If local dev breaks badly, clear `node_modules` and `.next`, then reinstall.
- Code conventions: functional React components only, use hooks, no class components, named exports preferred, explicit TypeScript props interfaces for components, Tailwind utility classes preferred over inline styles.
- Quality gates before PR/commit work: run `npm run lint`; contributors are also expected to run `npm run build` before submitting PRs.
- Git workflow: feature branches + PRs to `main`; use conventional commits (`feat:`, `fix:`, `docs:`, `chore:`, etc.).
- Deployment conventions: preview deploys on PR open via Vercel, production deploys only from `main`, env vars managed in Vercel dashboard.
- Architecture choices noted so far: App Router chosen over Pages Router for server component support; no state management library yet, `useState` is currently sufficient; Zustand may be considered if complexity grows.
- Product planning notes worth remembering: Sprint 4 priority is task filtering (all/active/completed); stretch goal is drag-and-drop reordering; tech debt item is extracting the form into a separate component.
- Important security note: `notes.md` contains sensitive staging/infrastructure credentials. Do not repeat or store those secrets in memory; treat that file as sensitive and avoid exposing its contents.
