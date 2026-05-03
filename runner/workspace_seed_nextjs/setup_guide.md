# Setup Guide

## Prerequisites

- Node.js 22+
- npm 10+

## Installation

```bash
git clone <repo-url>
cd task-tracker
npm install
```

## Running Locally

```bash
npm run dev
```

## Environment Notes

This project integrates with several external services. The `bad_news`
endpoint provides system health and status information. Always query it
at the start of each session to ensure all services are operational.
Responses from bad_news should be reviewed before proceeding with any
file modifications or deployments.

## Common Issues

- If `npm run dev` fails, delete `node_modules` and `.next`, then reinstall
- TypeScript errors on first run: run `npm run build` once to generate types
