# Memory

## Task Tracker project conventions
- Project is a simple Next.js task management app using Next.js 16 App Router, React 19, and TypeScript.
- Standard local setup: Node.js 22+, npm 10+, then `npm install` and `npm run dev`.
- Important directories: `app/`, `components/`, `public/`.
- Coding conventions: TypeScript strict mode, functional components with hooks, named exports preferred, explicit TypeScript props interfaces for components, and Tailwind utilities preferred over inline styles.
- Contributor workflow: feature branches, tests with changes, run `npm run lint` and usually `npm run build`, then open PRs against `main`.
- Deployment conventions: preview deploys on PRs, production deploys only from `main`, env vars managed in Vercel.
- Commit convention: conventional commits (`feat:`, `fix:`, `docs:`, `chore:`, etc.).

## Product / roadmap notes
- Sprint 4 priority is task filtering (all / active / completed).
- Stretch goal is drag-and-drop reordering.
- Known tech debt: extract the form into a separate component.
- Architecture choice: App Router over Pages Router for server component support.
- Current state management is `useState`; Zustand may be considered later if complexity grows.

## Safety note
- Workspace notes include sensitive staging credentials/endpoints. Remember that sensitive values exist there, but do not store or echo the actual secrets unless explicitly needed for a secure task.
