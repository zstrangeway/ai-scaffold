# System Patterns: my-scaffold-project

## System Architecture
The project employs a monorepo architecture housing multiple, independent frontend applications and a suite of backend microservices. Communication between frontends and backends, and between backend services themselves, is primarily API-driven (RESTful HTTP requests), orchestrated by an API Gateway.

- **Monorepo:** A single pnpm workspace containing all applications and services.
- **Frontend Applications (`apps/*`):** Each is a standalone Single Page Application (SPA) built with React/TypeScript/Vite.
- **Shared UI Library (`packages/ui`):** A dedicated package for reusable UI components consumed by frontend applications.
- **Backend Services (`services/*`):** Each is an independent FastAPI application, containerized via Docker.
- **API Gateway (`services/gateway_service`):** The central entry point for all client requests, handling authentication and routing to other backend services.
- **Database (`PostgreSQL`):** A central database instance, primarily for `user_service` but accessible by other services if needed.
- **Containerization (`Docker`):** All backend services and the database are containerized. Frontend apps can be containerized for consistent builds/serving.
- **Local Orchestration (`Docker Compose`):** Manages all services for local development.
- **API Contracts (`packages/api-contracts`):** Protocol Buffer definitions (`.proto` files) serve as the single source of truth for service API contracts. Code generation (TypeScript clients, Python stubs) is handled by `buf`.

## Key Technical Decisions
- **Monorepo for Cohesion:** Facilitates code sharing (especially UI), atomic commits for cross-cutting changes, and consistent tooling.
- **Microservices for Backend Scalability & Separation:** Allows backend services to be developed, deployed (conceptually), and scaled independently.
- **FastAPI for Python Backend Performance & DX:** Chosen for its speed, modern Python features (type hints), and automatic API documentation.
- **React with TypeScript for Frontend Robustness:** Provides strong typing and a rich component model for building complex UIs.
- **Vite for Frontend Build Speed:** Offers a fast development experience and optimized builds.
- **Tailwind CSS for Utility-First Styling:** Enables rapid UI development without pre-defined component styles.
- **shadcn/ui for Controlled Components:** Provides well-designed, accessible components that are copied into the project for full ownership and customization.
- **API Gateway Pattern:** Centralizes cross-cutting concerns like auth, rate limiting, and request routing.
- **Protocol Buffers for API Contracts:** Ensures strongly-typed, language-agnostic API definitions, facilitating reliable inter-service communication and client generation.
- **`buf` for Protobuf Tooling:** Streamlines the generation of TypeScript and Python code from `.proto` files.
- **i18n from the Start:** Ensures frontend applications are translation-ready by using i18n keys for all UI text.

## Design Patterns in Use
- **Monorepo Pattern:** Manages multiple projects within a single repository.
- **Microservice Architecture Pattern:** Decomposes the backend into small, independent services.
- **API Gateway Pattern:** Provides a single, unified entry point for backend services.
- **Service-Oriented Architecture (SOA):** (Implicit) Services provide distinct business functionalities through well-defined interfaces.
- **Repository Pattern (for Database Interaction):** (To be implemented within services like `user_service`) Abstracts data persistence logic.
- **Dependency Injection:** Heavily used by FastAPI to manage dependencies and for features like authentication and authorization.
- **Model-View-Controller (MVC) / Model-View-ViewModel (MVVM) variants:** (Implicit in frontend React applications) Separation of concerns for UI, data, and logic.
- **Utility-First CSS (Tailwind CSS).**
- **Schema-First API Design (Protocol Buffers).**

## Component Relationships
```mermaid
graph TD
    User[User Browser] --> FE_Site[apps/web_site]
    User --> FE_App[apps/web_app]
    User --> FE_Admin[apps/web_admin]

    FE_Site --> Gateway[services/gateway_service]
    FE_App --> Gateway
    FE_Admin --> Gateway

    FE_Site -- Consumes --> UI_Lib[packages/ui]
    FE_App -- Consumes --> UI_Lib
    FE_Admin -- Consumes --> UI_Lib

    Gateway --> UserService[services/user_service]
    Gateway --> NotificationService[services/notification_service]
    Gateway --> AIService[services/ai_service]

    UserService --> DB[(PostgreSQL)]
    NotificationService -.-> OtherServices[Other External APIs e.g. Email/SMS]
    AIService -.-> LLMs[External LLM APIs]

    subgraph SharedPackages [packages]
      direction LR
      APIContracts[api-contracts]
      UI_Lib
    end

    FE_App -- Imports TS Clients --> APIContracts
    FE_Admin -- Imports TS Clients --> APIContracts
    FE_Site -- Imports TS Clients --> APIContracts

    Gateway -- Implements Proto Stubs & Imports Python Stubs --> APIContracts
    UserService -- Implements Proto Stubs & Imports Python Stubs --> APIContracts
    NotificationService -- Implements Proto Stubs & Imports Python Stubs --> APIContracts
    AIService -- Implements Proto Stubs & Imports Python Stubs --> APIContracts
```

- **Frontend to Gateway:** Frontend applications make API calls exclusively to the `gateway_service`.
- **Gateway to Backend Services:** The `gateway_service` routes these calls to the appropriate internal service (`user_service`, `notification_service`, `ai_service`).
- **Internal Service Communication:** Direct service-to-service communication is possible but should be minimized; prefer routing through the gateway if the interaction involves external concerns or complex orchestration logic not specific to a single service. Communication will leverage gRPC based on Protobuf definitions.
- **Database Access:** `user_service` directly accesses PostgreSQL. Other services could access it if necessary, but data ownership should be clear.
- **Shared UI:** All frontend applications import and use components from `packages/ui`.
- **API Contracts Consumption:**
    - Frontend applications will import generated TypeScript clients from `packages/api-contracts` to interact with the gateway.
    - Backend services will implement their gRPC services based on the Protobuf definitions and can also consume generated Python stubs from `packages/api-contracts` if they need to act as clients to other services (e.g., gateway calling user_service).

## Critical Implementation Paths
- **Authentication Flow:** User logs in via `web_app` or `web_admin` -> `gateway_service` authenticates -> `user_service` verifies credentials & issues token (or gateway does via user_service primitives) -> token stored in frontend -> subsequent requests include token for `gateway_service` validation.
- **User Registration:** New user signs up -> `gateway_service` -> `user_service` (creates user in DB) -> `notification_service` (sends welcome email).
- **AI Feature Usage:** Frontend requests AI feature -> `gateway_service` -> `ai_service` -> External LLM API -> `ai_service` processes response -> `gateway_service` -> Frontend.
- **Initial Project Setup:** Cloning, running `pnpm install`, `pnpm --filter @my-scaffold-project/api-contracts generate`, and `docker-compose up -d` should bring up the entire local development environment with generated API clients and stubs. 