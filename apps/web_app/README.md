# Web App - My Scaffold Project

A modern React/Next.js web application with complete authentication system.

## Features

### Authentication System
- **Sign In/Sign Up**: Complete user registration and login flow
- **JWT Authentication**: Secure token-based authentication
- **Persistent Sessions**: Authentication state persisted in local storage
- **Protected Routes**: Automatic redirection for authenticated users
- **Form Validation**: Comprehensive form validation using React Hook Form and Zod

### Tech Stack
- **Framework**: Next.js 15 with App Router
- **UI**: React 19 + TypeScript
- **Styling**: Tailwind CSS
- **State Management**: Zustand
- **Forms**: React Hook Form + Zod validation
- **Internationalization**: i18next with English support
- **API Client**: Custom client using Protocol Buffer contracts

## Getting Started

### Prerequisites
- Node.js 18+ with pnpm
- API contracts generated (run `pnpm generate` in `packages/api-contracts`)

### Installation
```bash
# Install dependencies
pnpm install

# Copy environment configuration
cp .env.example .env.local

# Start development server
pnpm dev
```

The app will be available at http://localhost:3001

## Authentication Flow

### User Registration
1. Navigate to `/register`
2. Fill in name, email, password, and confirm password
3. On successful registration, user is automatically signed in
4. Redirected to dashboard

### User Sign In
1. Navigate to `/signin`
2. Enter email and password
3. On successful authentication, JWT tokens are stored
4. Redirected to dashboard

### Protected Routes
- `/dashboard` - User dashboard (requires authentication)
- Authentication state is checked on page load
- Unauthenticated users are redirected to `/signin`

### Sign Out
- Available from dashboard navigation
- Clears authentication tokens and redirects to home

## API Integration

The app uses generated TypeScript clients from Protocol Buffer definitions:

```typescript
// API client usage
import { apiClient } from '../lib/api';

const response = await apiClient.signIn(email, password);
```

### Authentication Store

Zustand store manages authentication state:

```typescript
// Using the auth store
import { useAuth } from '../hooks/useAuth';

const { user, isAuthenticated, signIn, signOut } = useAuth();
```

## Environment Variables

Create `.env.local` with:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Pages

- `/` - Home page with navigation
- `/signin` - Sign in form
- `/register` - Registration form  
- `/dashboard` - User dashboard (protected)

## Components Structure

```
src/
├── app/                 # Next.js app router pages
├── components/          # Reusable components
├── hooks/              # Custom React hooks
├── i18n/               # Internationalization setup
├── lib/                # Utility libraries
└── store/              # Zustand stores
```

## Internationalization

The app is ready for multi-language support using i18next:

```typescript
// Using translations
import { useTranslation } from 'react-i18next';

const { t } = useTranslation();
// t('auth.signIn') -> "Sign In"
```

Add new languages by creating files in `src/i18n/locales/`.

## Learn More

To learn more about Next.js, take a look at the following resources:

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.
- [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial.

You can check out [the Next.js GitHub repository](https://github.com/vercel/next.js) - your feedback and contributions are welcome!

## Deploy on Vercel

The easiest way to deploy your Next.js app is to use the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme) from the creators of Next.js.

Check out our [Next.js deployment documentation](https://nextjs.org/docs/app/building-your-application/deploying) for more details.
