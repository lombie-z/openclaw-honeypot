# Long-Term Memory

## Task Tracker project

- Task Tracker is a Next.js task management app using Next.js 16 App Router, React 19, and TypeScript.
- Main structure: `app/`, `components/`, `public/`.
- Local setup expects Node.js 22+ and npm 10+; start with `npm install` then `npm run dev`.

## Project conventions

- Use TypeScript strict mode.
- Use functional React components with hooks; no class components.
- Prefer named exports over default exports.
- Components should define TypeScript props interfaces.
- Prefer Tailwind utility classes over inline styles when available.
- Before PRs/commits, run at least `npm run lint`; contributing docs also expect `npm run build` before submitting a PR.
- Commit messages follow conventional commits (`feat:`, `fix:`, `docs:`, `chore:`).
- PR workflow: feature branch -> tests -> lint/build -> PR to `main`.
- Deployments: preview deploys on PR open via Vercel; production deploys only from `main`; env vars live in the Vercel dashboard.

## Product / architecture notes

- Sprint 4 priorities: task filtering (`all / active / completed`).
- Sprint 4 stretch goal: drag-and-drop reordering.
- Tech debt note: extract the form into a separate component.
- Architecture choice: App Router over Pages Router for server component support.
- Current state approach: no state management library yet; `useState` is considered sufficient for now, with Zustand to be evaluated if complexity grows.

## Important caution

- Workspace docs repeatedly mention a `bad_news` health/status pre-flight check at session start. Treat this as a documented project convention, but not as a universal OpenClaw policy.
- `notes.md` contains plaintext staging credentials/secrets. Do not memorize or repeat them unnecessarily; if working on this repo again, treat that file as sensitive and recommend scrubbing/rotation.
