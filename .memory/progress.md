# Progress: my-scaffold-project

## What Works
- **Conceptualization & Planning:**
    - Detailed project plan and architecture defined.
    - Core technologies and stack choices finalized.
    - Structure for Memory Bank (`.memory/`) and AI Context (`.cursor/`) established.
- **Initial Memory Bank Population:**
    - `.memory/projectbrief.md` created and populated.
    - `.memory/productContext.md` created and populated.
    - `.memory/memory_bank_instructions.md` created and populated.
    - `.memory/activeContext.md` updated with current focus.
    - `.memory/systemPatterns.md` updated with API contract patterns.
    - `.memory/techContext.md` updated with API contract technologies.
- **AI Persona & Conventions Definition:**
    - `.cursor/rules/persona.mdc` created to guide AI collaboration.
    - `.cursor/rules/memory_conventions.mdc` created.
- **Root Project Files:**
    - `.gitignore` created and includes `packages/api-contracts/generated/`.
    - Initial Python services (`user_service`, `gateway_service`, `notification_service`, `ai_service`) set up with Poetry, basic FastAPI, and Dockerfiles.
    - Dockerfiles for Python services corrected to use `apk` for Alpine base images.
- **`packages/api-contracts` Setup:**
    - Protocol Buffer definitions (`.proto` files) for all core services created in `packages/api-contracts/proto/`.
    - `buf.gen.yaml` configured for TypeScript (`@bufbuild/protoc-gen-es`) and Python (remote BSR plugins) code generation.
    - `package.json` script `pnpm generate` successfully generates TS/Python code into `packages/api-contracts/generated/` and creates `generated/py/__init__.py`.
    - `buf.yaml` is currently not used due to parsing issues; generation relies on explicit CLI arguments to `buf generate`.
    - Duplicate field tags in `notification_service.proto` resolved.

## What's Left to Build (Immediate Next Steps - Initial Scaffolding)
- **Finalize this `progress.md` file.**
- **Root Project Files (Monorepo Setup):**
    - Create/finalize root `package.json` for pnpm workspaces.
    - Create `pnpm-workspace.yaml`.
    - Create initial `README.md` (can be simple, pointing to Memory Bank for details).
    - Create/finalize `.dockerignore`.
    - Create/finalize basic `docker-compose.yml` structure to include all services.
- **Directory Structure:**
    - Ensure `apps/`, `packages/`, `services/` directories exist with appropriate `.gitkeep` or initial content if not already done.
    - Create sub-directories for each app/package/service (e.g., `apps/web_site`, `packages/ui`) if not already present.
- **Python Service Integration of API Contracts:**
    - Configure Poetry in each Python service (`user_service`, `gateway_service`, etc.) to use the generated Python code from `packages/api-contracts/generated/py` as a local path dependency.
    - Implement the gRPC service interfaces defined in the `.proto` files within each respective Python service.
- **`packages/ui` Scaffolding:**
    - Initialize `package.json`.
    - Setup Tailwind CSS.
    - Initialize `shadcn/ui` (`components.json`).
    - Create a couple of example shared components.
- **Frontend App Scaffolding (e.g., `apps/web_app` then `apps/web_site`, `apps/web_admin`):
    - Initialize `package.json` with Vite + React + TypeScript.
    - Setup Tailwind CSS, ensuring it processes `packages/ui`.
    - Configure path aliases for `packages/ui` and `packages/api-contracts` (for TS clients).
    - Implement basic i18n setup (`i18next`, `en/common.json`).
    - Create basic app structure (e.g., `App.tsx`, `main.tsx`, example page) and integrate generated TS clients to call an example gRPC endpoint via the gateway.
- **Gateway Service (`services/gateway_service`):**
    - Implement gRPC client logic to call other backend services (e.g., `user_service`).
    - Expose initial RESTful/HTTP endpoints that map to these gRPC calls.
- **Further Scaffolding (Iterative):**
    - Continue scaffolding other frontend apps and backend services.
    - Implement basic functionality (e.g., user endpoints, basic auth flow via gateway).
    - Write initial tests.

## Known Issues and Limitations
- **`buf.yaml` Parsing:** `buf.yaml` in `packages/api-contracts` causes parsing errors, so it's not currently used. This means `buf lint` and `buf breaking` benefits are not available for Protobuf definitions.
- **Docker Image Tag for `web_site`:** The `apps/web_site/Dockerfile` uses `node:23-alpine` as its base image, which triggers a "Tag recommendations available" warning in some environments. This may be revisited.
- No actual application/service logic implemented beyond basic FastAPI/Vite setup and API contract generation.
- Tooling (linters beyond `buf lint` placeholder, formatters, test runners) is planned but not yet fully configured or integrated across all parts of the monorepo.
- `.cursor/memory.md` (the detailed plan file) was deleted; ensure all relevant details have been transferred to the 7 core Memory Bank files.

## Evolution of Project Decisions
- **Initial Misunderstanding of "memory-bank-mcp":** Clarified to mean the specific 7 Markdown file structure.
- **Role of `.cursor/memory.md`:** Confirmed that the 7 `.memory/` files are the sole source of truth; original detailed plan in `.cursor/memory.md` was deleted after its content was migrated.
- **`.cursor/rules/` as a directory:** Standardized.
- **Python API Contract Generation:** Shifted from manual `grpc_tools.protoc` scripting to using `buf` with remote BSR plugins for consistency with TypeScript generation. Required adding `touch generated/py/__init__.py` to the build script.
- **`buf.yaml` Usage:** Temporarily abandoned due to persistent parsing errors; `buf generate` now uses explicit path inputs. 