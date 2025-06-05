# @my-scaffold-project/web-ui

A shared UI components library built with React, TypeScript, Tailwind CSS, and shadcn/ui components. This package provides a comprehensive set of reusable components with Storybook documentation.

## Features

- 🎨 **shadcn/ui Components** - Beautiful, accessible components built on Radix UI
- 📚 **Storybook Integration** - Interactive component documentation and playground
- 🎯 **TypeScript Support** - Full type safety and IntelliSense
- 🌙 **Dark Mode Ready** - Built-in support for light and dark themes
- 📦 **Tree Shakeable** - Import only what you need
- 🚀 **Fast Build** - Optimized bundle with tsup
- ♿ **Accessible** - Following WCAG guidelines

## Installation

```bash
pnpm add @my-scaffold-project/web-ui
```

### Peer Dependencies

Make sure you have the required peer dependencies installed:

```bash
pnpm add react react-dom
```

## Usage

### Basic Import

```tsx
import { Button, Card, CardContent, CardHeader, CardTitle } from '@my-scaffold-project/web-ui';

function App() {
  return (
    <Card className="w-[350px]">
      <CardHeader>
        <CardTitle>Welcome</CardTitle>
      </CardHeader>
      <CardContent>
        <Button>Get Started</Button>
      </CardContent>
    </Card>
  );
}
```

### Importing Styles

Import the CSS file in your main app file:

```tsx
// In your main App.tsx or index.tsx
import '@my-scaffold-project/web-ui/styles.css';
```

### Using Utility Functions

```tsx
import { cn } from '@my-scaffold-project/web-ui';

function MyComponent({ className, ...props }) {
  return (
    <div
      className={cn('default-styles', className)}
      {...props}
    />
  );
}
```

## Available Components

### Core Components

- **Button** - Versatile button component with multiple variants
- **Card** - Container component with header, content, and footer sections
- **Input** - Form input component with validation states

### Component Variants

#### Button Variants
- `default` - Primary button style
- `destructive` - For dangerous actions
- `outline` - Outlined button
- `secondary` - Secondary styling
- `ghost` - Minimal styling
- `link` - Link-styled button

#### Button Sizes
- `default` - Standard size
- `sm` - Small size
- `lg` - Large size
- `icon` - Square icon button

## Development

### Prerequisites

- Node.js 18+
- pnpm

### Setup

```bash
# Clone the repository
git clone [repository-url]

# Install dependencies
pnpm install

# Start Storybook
pnpm dev

# Build the package
pnpm build

# Run type checking
pnpm type-check

# Lint the code
pnpm lint
```

### Storybook

The component library includes comprehensive Storybook documentation. Start the development server:

```bash
pnpm dev
```

Then open [http://localhost:6006](http://localhost:6006) to view the component library.

### Building Storybook

To build a static version of Storybook:

```bash
pnpm build:storybook
```

## Contributing

1. Create a new branch for your feature/component
2. Add your component in `src/components/`
3. Create corresponding Storybook stories in `src/components/[component].stories.tsx`
4. Export your component from `src/index.ts`
5. Test your component in Storybook
6. Build the package to ensure it compiles correctly
7. Create a pull request

### Component Guidelines

- Use TypeScript for all components
- Follow the existing naming conventions
- Include proper JSDoc comments
- Create comprehensive Storybook stories
- Ensure accessibility standards are met
- Use Tailwind CSS for styling
- Leverage Radix UI primitives where applicable

## Scripts

- `pnpm dev` - Start Storybook development server
- `pnpm build` - Build the package for production
- `pnpm build:storybook` - Build static Storybook
- `pnpm lint` - Lint TypeScript and React code
- `pnpm type-check` - Run TypeScript type checking
- `pnpm clean` - Clean build artifacts

## License

This project is part of the my-scaffold-project monorepo.