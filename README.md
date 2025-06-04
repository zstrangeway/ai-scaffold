# my-scaffold-project

This is a comprehensive, modern scaffold project designed to accelerate the development of new full-stack applications. It features a monorepo structure, multiple frontend applications, a microservices-oriented backend, and clear conventions for AI-assisted development.

## Overview

This project aims to:
- Accelerate setup time for new full-stack projects.
- Promote consistency and best practices.
- Provide a clear, modular architecture.
- Optimize for AI-assisted development workflows.

For detailed information about the project architecture, technologies used, setup instructions, and current progress, please refer to the **Memory Bank** documentation located in the `.memory/` directory.

## Quick Start (Conceptual)

1.  **Clone the repository.**
2.  **Install dependencies:** `pnpm install`
3.  **Generate API contracts:** `pnpm run generate-contracts` (or `pnpm --filter @my-scaffold-project/api-contracts generate`)
4.  **Run services (local development):** `docker-compose up -d`
5.  **Run a frontend application:** `cd apps/web_app && pnpm dev` (example)

## Memory Bank

All detailed project documentation, including context, system patterns, tech stack, and progress, is maintained within the `.memory/` directory. Please consult these files for an in-depth understanding of the project.

Key files in the Memory Bank:
- `.memory/projectbrief.md`: Overall project scope and goals.
- `.memory/productContext.md`: The why and for whom of the project.
- `.memory/systemPatterns.md`: System architecture and design patterns.
- `.memory/techContext.md`: Technologies, tools, and setup.
- `.memory/activeContext.md`: Current work focus and next steps.
- `.memory/progress.md`: Detailed progress and what's left to build.
- `.memory/memory_bank_instructions.md`: Instructions for the AI on how to use this memory system. 