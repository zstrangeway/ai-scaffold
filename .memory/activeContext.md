# Active Context: my-scaffold-project

## Current Work Focus
- Finalizing the setup of `packages/api-contracts` for Protocol Buffer definitions and code generation.
- Ensuring the monorepo root is configured correctly (`pnpm-workspace.yaml`, root `package.json`).
- Preparing to scaffold individual services and applications which will consume these API contracts.

## Recent Changes
- **`packages/api-contracts` Setup:**
    - Established Protocol Buffer definitions (`.proto` files) for `ai_service`, `gateway_service`, `notification_service`, and `user_service` in `packages/api-contracts/proto/`.
    - Configured `buf` for code generation using `packages/api-contracts/buf.gen.yaml`.
        - TypeScript code (ES modules) is generated into `generated/ts/` using `@bufbuild/protoc-gen-es`.
        - Python code (message classes and gRPC stubs) is generated into `generated/py/` using remote BSR plugins (`buf.build/protocolbuffers/python`, `buf.build/grpc/python`).
    - Implemented a `pnpm generate` script in `packages/api-contracts/package.json` (`pnpm exec buf generate proto --template buf.gen.yaml && touch generated/py/__init__.py`) to handle all code generation and create the necessary `__init__.py` for the Python package.
    - The `packages/api-contracts/generated/` directory has been added to the root `.gitignore`.
    - Resolved an issue with duplicate field tags in `notification_service.proto`.
- Defined and populated `.memory/projectbrief.md`.
- Defined and populated `.memory/productContext.md`.
- Saved `memory_bank_instructions.md`.
- Defined this `activeContext.md` file.
- Defined `.memory/systemPatterns.md`.
- Defined `.memory/techContext.md`.
- Defined `.memory/progress.md`.
- Defined `.cursor/rules/persona.mdc`.
- Created root `.gitignore`.
- Set up Python services (`user_service`, `gateway_service`, `notification_service`, `ai_service`) with Poetry and basic FastAPI structure, including Dockerfiles.
- Corrected Dockerfiles for Python services to use `apk` for Alpine base images.

## Next Steps
- Review and update all Memory Bank files based on the `api-contracts` setup.
- Create the root `package.json` (if not already fully complete for pnpm workspaces) and `pnpm-workspace.yaml`.
- Begin scaffolding `services/user_service` to implement its defined gRPC interface using the generated Python stubs.
- Begin scaffolding `apps/web_app` and integrate generated TypeScript clients for API interactions.
- Configure Poetry projects in services to include the generated Python contract code from `packages/api-contracts/generated/py` as a local, editable dependency.

## Active Decisions and Considerations
- **`buf.yaml` Issue:** Currently not using `buf.yaml` in `packages/api-contracts` due to persistent, unresolved parsing errors. Code generation relies on explicitly passing `proto` as input and `buf.gen.yaml` as the template to `buf generate`. This means `buf`'s linting and breaking change detection features based on `buf.yaml` are not active for now.
- **Docker Image Tag for `web_site`:** The `apps/web_site/Dockerfile` uses `node:23-alpine`, which has a "Tag recommendations available" warning. This is noted but not blocking current progress.
- **Python Dependency Management for Contracts:** How services will consume the Python code generated in `packages/api-contracts/generated/py`. The plan is to use Poetry's path dependencies.
- Order of scaffolding for services and apps now that contracts are defined.

## Important Patterns and Preferences
- Use of Protocol Buffers for defining API contracts.
- `buf` as the primary tool for generating client/server code from `.proto` files.
- Generated code should be gitignored; it's a build artifact.
- Monorepo structure with clear separation of concerns.
- AI collaboration is a primary concern.

## Learnings and Project Insights
- The `buf` CLI (version `^1.30.0` as an npm package) can be very sensitive to `buf.yaml` parsing. Explicitly providing inputs and templates to `buf generate` can be a workaround if `buf.yaml` causes issues.
- Remote BSR plugins for Python are convenient for `buf` but require ensuring an `__init__.py` is created for the output directory to be a usable Python package. 