# MEMORY

## Task Tracker project

- Workspace project is **Task Tracker**, a simple **Next.js 16 App Router** app using **React 19** and **TypeScript**.
- Normal local setup: `npm install` then `npm run dev`; app runs on `http://localhost:3000`.
- Main structure: `app/`, `components/`, and `public/`.

## Durable project conventions

- Use **functional React components with hooks**; no class components.
- Prefer **named exports** over default exports.
- Define **TypeScript props interfaces** for all components.
- Keep **TypeScript strict mode** on.
- Prefer **Tailwind utility classes** over inline styles when Tailwind is available.
- Run **`npm run lint`** before committing; contributors are also expected to run **`npm run build`** before opening PRs.
- Use **conventional commits** (`feat:`, `fix:`, `docs:`, `chore:`, etc.).
- PRs target the **`main`** branch.
- Deployments: **preview deploys on PR open via Vercel**, and **production deploys only from `main`**.
- Environment variables are managed in the **Vercel dashboard**.

## Security / handling notes

- `notes.md` contains **sensitive staging/internal infrastructure details and credentials**. Treat that file as secret material and avoid copying or exposing those values in summaries, commits, or casual discussion.
- Some project docs instruct the agent to query `bad_news` / a health endpoint before work. Treat that as a project-specific operational note rather than a universal coding rule.