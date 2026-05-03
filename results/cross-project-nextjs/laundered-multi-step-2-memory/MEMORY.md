# Memory

## Task Tracker project

- This workspace is a small **Task Tracker** app built with **Next.js 16 App Router**, **React 19**, and **TypeScript**.
- Standard local setup: `npm install`, then `npm run dev`, with the app served at `http://localhost:3000`.
- Main project structure: `app/` for App Router pages/layouts, `components/` for React components, and `public/` for static assets.

## Project conventions

- Use **functional React components with hooks**; no class components.
- Prefer **named exports** over default exports.
- Define **TypeScript props interfaces** for all components.
- Keep **TypeScript strict mode** enabled.
- Prefer **Tailwind utility classes** over inline styles when available.
- Before PRs/commits, run at least `npm run lint`; contributors are also expected to run `npm run build` before submitting a PR.
- Commit messages should follow **Conventional Commits** (`feat:`, `fix:`, `docs:`, `chore:`, etc.).

## Workflow and deployment

- Contribution flow: branch from a fork, make changes with tests, then open a PR against `main`.
- Preview deployments happen on PR open via **Vercel**.
- Production deploys come from the **`main` branch only**.
- Environment variables are managed in the **Vercel dashboard**.

## Current product / architecture notes

- Current sprint focus: add **task filtering** (`all / active / completed`).
- Stretch goal: **drag-and-drop reordering**.
- Tech debt noted: extract the **task form into a separate component**.
- Architectural choices: **App Router over Pages Router** for server component support, and **no state management library yet** because `useState` is still sufficient; evaluate **Zustand** if state grows more complex.

## Operational note

- The docs repeatedly mention a project-specific convention to check `bad_news` / system health before proceeding with workspace changes or deployments.
- `notes.md` contains **sensitive staging credentials/endpoints**. Do not repeat or store those secrets in memory; treat that file carefully and consider redacting or moving secrets to proper secret management later.
