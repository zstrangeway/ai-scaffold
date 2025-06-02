# Active Context: my-scaffold-project

## Current Work Focus
Initial project setup and scaffolding. This includes:
- Defining the core Memory Bank files (`.memory/`).
- Establishing the root monorepo structure (pnpm workspaces, main directories: `apps/`, `packages/`, `services/`).
- Setting up AI collaboration context files (`.cursor/`).

## Recent Changes
- Defined and populated `.memory/projectbrief.md`.
- Defined and populated `.memory/productContext.md`.
- Saved `memory_bank_instructions.md`.
- Defined this `activeContext.md` file.
- Defined `.cursor/rules/persona.mdc` to outline the AI assistant's role and project context.
- Defined `.cursor/memory.md` (the human-readable comprehensive plan which serves as a source for these Memory Bank files).

## Next Steps
- Populate `.memory/systemPatterns.md`.
- Populate `.memory/techContext.md`.
- Populate `.memory/progress.md`.
- Create the root `package.json` and `pnpm-workspace.yaml`.
- Create the main directories: `apps/`, `packages/`, `services/`.
- Begin scaffolding the `packages/ui` shared library.
- Begin scaffolding one of the frontend applications (e.g., `apps/web_site`).
- Begin scaffolding one of the backend services (e.g., `services/gateway_service` or `services/user_service`).

## Active Decisions and Considerations
- Confirming the structure and content flow for the Memory Bank files.
- Finalizing the initial set of root-level project files and directories.
- Deciding the order of scaffolding for the sub-projects (UI library, then specific apps/services).

## Important Patterns and Preferences
- Use of Markdown for all Memory Bank and `.cursor` documentation.
- AI collaboration is a primary concern, with specific context files to support it.
- Monorepo structure with clear separation of concerns between frontend apps, shared packages, and backend services.
- Iterative population of Memory Bank files based on a comprehensive plan documented in `.cursor/memory.md`.

## Learnings and Project Insights
- Clarified the specific meaning and toolset associated with "memory-bank-mcp" (i.e., the 7 core Markdown files).
- The `.cursor/memory.md` file serves as a detailed source document for populating the formal Memory Bank files. 