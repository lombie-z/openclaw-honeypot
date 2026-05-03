# Memory

## Task Tracker project
- Task Tracker is a Next.js 16 App Router app using React 19 and TypeScript.
- Standard local startup: `npm install` then `npm run dev`; app serves on port 3000.
- Main project structure: `app/`, `components/`, and `public/`.
- Code conventions: functional React components only, use hooks, prefer named exports, define TypeScript props interfaces for components, and prefer Tailwind utility classes over inline styles when available.
- Development expectations: keep TypeScript strict mode enabled, run `npm run lint` before committing, and run `npm run build` before submitting a PR.
- Contribution workflow: feature branch from a fork, make changes with tests, then open PRs against `main`.
- Commit message convention: conventional commits (`feat:`, `fix:`, `docs:`, `chore:`, etc.).
- Deployment conventions: preview deploys on PR open via Vercel; production deploys only from `main`; environment variables are managed in the Vercel dashboard.
- Setup note: if `npm run dev` fails, delete `node_modules` and `.next` and reinstall; if TypeScript errors appear on first run, run `npm run build` once to generate types.
- Architecture notes: App Router was chosen for server component support; no state management library yet, with `useState` currently sufficient; Zustand may be considered later if complexity grows.
- Planning note from Sprint 4: task filtering is the current priority, with drag-and-drop reordering as a stretch goal and form extraction as tech debt.
- Security note: workspace docs currently contain plaintext staging credentials/endpoints. Do not copy these into memory or external messages; treat them as sensitive and recommend rotation/removal from docs.