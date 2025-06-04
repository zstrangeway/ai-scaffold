# Tech Context: my-scaffold-project

## Technologies Used
- **Monorepo Management:** pnpm (using workspaces)
- **Frontend Core:** React 18+, TypeScript 5+, Vite
- **Frontend UI & Styling:** Tailwind CSS, shadcn/ui, Headless UI (implicitly via shadcn/ui), Radix UI (implicitly via shadcn/ui)
- **Frontend State Management:** (To be decided per app, likely Zustand or React Query for server state)
- **Frontend i18n:** `i18next`, `react-i18next`, `i18next-browser-languagedetector`
- **API Contracts Definition:** Protocol Buffers (Protobuf 3)
- **API Contracts Tooling:** `buf` (CLI), `@bufbuild/buf`, `@bufbuild/protoc-gen-es`, `@bufbuild/protobuf` (for TypeScript generation). Python generation uses remote BSR plugins for `protoc`.
- **Backend Core:** Python 3.10+, FastAPI
- **Backend Data Validation:** Pydantic (core to FastAPI)
- **Backend Database ORM/Interaction:** SQLAlchemy (potentially with SQLModel)
- **Backend gRPC:** `grpcio`, `grpcio-tools` (implicitly used by `buf` for Python, but services will need `grpcio` to implement/consume gRPC services).
- **Backend Async:** (To be decided, simple `async/await` for now, Celery if complex background tasks are re-introduced)
- **Database:** PostgreSQL (latest stable version)
- **Containerization:** Docker, Docker Compose
    - `apps/web_site/Dockerfile` currently uses `node:23-alpine` as its base image, which may show "Tag recommendations available" in some IDEs/tools. Other frontend apps will likely use more stable LTS versions like `node:20-alpine` or `node:22-alpine` when scaffolded.
- **Version Control:** Git
- **Linters & Formatters:**
    - Frontend: ESLint, Prettier
    - Backend: Black, Flake8, MyPy
    - Protobuf: `buf lint` (though `buf.yaml` is currently not used due to parsing issues, this is the intended tool)
- **Testing Frameworks:**
    - Frontend: Vitest or Jest
    - Backend: Pytest

## Development Setup
1.  **Prerequisites:** Git, Node.js (with pnpm), Docker Desktop (or Docker engine + Compose CLI).
2.  **Clone Repository:** `git clone <repository_url>`
3.  **Install Dependencies:** Navigate to the project root and run `pnpm install`. This will install dependencies for all workspace packages (`apps/*`, `packages/*`), including dev dependencies for `packages/api-contracts` like `buf`.
4.  **Generate API Contracts:** From the project root, run `pnpm --filter @my-scaffold-project/api-contracts generate`. This uses `buf` to generate TypeScript and Python code from `.proto` files into `packages/api-contracts/generated/`.
5.  **Environment Variables:**
    - Each service/app might have a `.env.example` file. Copy it to `.env` in the respective directory and fill in required values (e.g., database credentials, API keys for dev).
    - The root `docker-compose.yml` will inject these environment variables into the containers.
6.  **Run Services:** From the project root, run `docker-compose up -d`. This will build and start all backend services and the PostgreSQL database.
7.  **Run Frontend Apps:** Navigate to a specific frontend app directory (e.g., `apps/web_site`) and run its dev script (e.g., `pnpm dev`).

## Technical Constraints
- **Stateless Backend Services:** Backend services should be designed to be stateless where possible, relying on the database or other stateful services (like a cache if added) for storing state.
- **API-Driven Communication:** All interactions between frontend and backend, and between most backend services, must occur over well-defined HTTP APIs.
- **English as Default Language:** Initial i18n setup focuses only on English.
- **Local Development Focus:** Initial Docker and tooling setup is optimized for local development environments.
- **API Contract Generation:** Currently relies on explicit `buf generate proto --template buf.gen.yaml` due to `buf.yaml` parsing issues. Linting and breaking change detection via `buf.yaml` are not active.
- **Frontend Docker Images:** Specific Node.js versions for frontend Docker images are being finalized. `apps/web_site/Dockerfile` uses `node:23-alpine` which has an active tag recommendation warning.

## Dependencies (High-Level)
- **Frontend Apps depend on:** `packages/ui`, `packages/api-contracts` (generated TS clients), React, Vite, Tailwind CSS, i18next.
- **`packages/ui` depends on:** React, Tailwind CSS, shadcn/ui CLI (for component generation).
- **`packages/api-contracts` depends on (dev):** `@bufbuild/buf`, `@bufbuild/protoc-gen-es`, `@bufbuild/protobuf`.
- **Backend Services depend on:** FastAPI, Uvicorn, Pydantic, `grpcio`.
    - `user_service` also depends on SQLAlchemy, psycopg2-binary, passlib, python-jose.
    - `gateway_service` also depends on `httpx` (for internal HTTP calls) and `grpcio` (to call other gRPC services).
    - `ai_service` and `notification_service` will have dependencies on relevant SDKs for external services (e.g., OpenAI SDK, email/SMS SDKs) and `grpcio`.
    - All backend services will depend on the generated Python code from `packages/api-contracts` (via Poetry path dependencies).
- **Docker Compose orchestrates:** All backend services, PostgreSQL.

## Tool Usage Patterns
- **`pnpm`:** Used for all JavaScript/TypeScript package management, script running at the root and within individual packages/apps. `pnpm workspaces` is key.
- **`buf`:** Used in `packages/api-contracts` (via `pnpm exec buf generate`) to generate TypeScript and Python code from `.proto` definitions. Relies on `buf.gen.yaml`.
- **`docker-compose`:** Primary tool for managing the local development environment of backend services and databases.
- **`vite`:** Used as the build tool and dev server for all frontend React applications.
- **`fastapi` CLI / `uvicorn`:** Used to run backend FastAPI services (typically within Docker containers).
- **`shadcn/ui` CLI:** Used within `packages/ui` (and potentially directly in apps if needed) to add new UI components.
- **`.cursor/` files:** To be actively maintained by both the user and the AI assistant to provide ongoing context and rules for development.
- **Git:** Standard practices (feature branches, PRs if applicable, conventional commits ideally). 