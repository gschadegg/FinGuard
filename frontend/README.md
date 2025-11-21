This is the presentation layer for FinGuard built with NextJS

_Note: the setup here focuses on local dev env for the Frontend, for Docker setup view the [root level README](../README.md)_

## Setup

_uses pnpm_

- Install dependencies running the following scripts:
  - `corepack enable`
  - `cd frontend`
  - `pnpm install --frozen-lockfile`

#### Running

- Dev Server: `pnpm run dev`
- Production Build: `pnpm build && pnpm start`

#### Testing

- Unit & Module Tests `pnpm run test`
- End-to-end Tests: `pnpm run e2e`
- End-to-end Tests in UI Mode: `pnpm run e2e:ui`

## Tech Stack

All ShadCN Components being used are found under `@/frontend/components/ui`.

|                   |                               |
| ----------------- | ----------------------------- |
| NextJS            | Framework                     |
| ShadCN + Tailwind | UI Framework & Utility styles |
| Playwright        | End-to-end testing            |
| Jest              | Unit & Module testing         |
