# Project Brief: my-scaffold-project

## Overview
A comprehensive, modern scaffold project to accelerate the development of new full-stack applications. It features a monorepo structure, multiple frontend applications (brochure site, main web app, admin panel), a microservices-oriented backend, and clear conventions for AI-assisted development.

## Core Requirements
- Develop a monorepo structure managed by pnpm workspaces.
- Create three distinct frontend applications: `web_site`, `web_app`, and `web_admin` using React, TypeScript, and Vite.
- Implement a shared UI library (`packages/ui`) using Tailwind CSS and shadcn/ui principles.
- Build backend services (`gateway_service`, `user_service`, `notification_service`, `ai_service`) using Python and FastAPI.
- Integrate PostgreSQL as the primary database, initially for `user_service`.
- Utilize Docker and Docker Compose for containerization and local orchestration.
- Establish conventions for AI collaboration using `.cursor/rules/` and `.cursor/memory.md` files.
- Implement i18n for frontends (defaulting to English, using translation files).

## Goals
- Accelerate setup time for new full-stack projects.
- Promote consistency and best practices across projects.
- Provide a clear, modular architecture that is easy to understand and extend.
- Optimize for AI-assisted development workflows.
- Offer a solid foundation for common application features (user management, notifications, AI integration).

## Project Scope
**In Scope:**
- Initial setup and basic functionality of all defined frontend apps and backend services.
- Core database schema for the User service.
- Basic API definitions and inter-service communication patterns.
- Dockerization of all services for local development.
- Setup of i18n, shared UI library, and AI collaboration context files.
- Documentation within `.cursor/memory.md` and `README.md` for setup and usage.

**Out of Scope (for initial scaffold - Deferred Features):**
- Full-fledged Payment Integration (Stripe, etc.).
- Real-time Chat Service.
- Advanced Task Queue implementation (Celery with message broker).
- Deployment scripts or configurations for production environments (beyond Docker basics).
- Extensive pre-built UI components beyond basic structure and examples.
- Complex business logic within the services beyond foundational capabilities. 