# Stumpf.works POS - Frontend

React + Vite + TypeScript frontend for the Stumpf.works POS system.

## Tech Stack

- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool & dev server
- **TailwindCSS** - Styling
- **TanStack Query** - Server state management
- **Zustand** - Client state management
- **React Router** - Routing
- **Axios** - HTTP client
- **React Hot Toast** - Notifications

## Getting Started

### Prerequisites

- Node.js 18+
- npm 9+

### Installation

```bash
cd frontend

# Install dependencies
npm install

# Copy environment variables
cp ../.env.example ../.env

# Start development server
npm run dev
```

The app will be available at http://localhost:5173

## Project Structure

```
src/
├── components/     # Reusable UI components
├── pages/          # Page components (routes)
├── services/       # API services
├── stores/         # Zustand state stores
├── hooks/          # Custom React hooks
├── types/          # TypeScript types
├── utils/          # Utility functions
├── App.tsx         # Main app component
└── main.tsx        # Entry point
```

## Available Scripts

```bash
# Development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Linting
npm run lint

# Format code
npm run format

# Run tests
npm test
```

## Features

### Authentication

- Email/password login
- PIN-based quick login (for POS)
- JWT token management
- Automatic token refresh
- Multi-tenant support

### POS Interface

- Touch-optimized UI
- Product search & barcode scanning
- Shopping cart
- Multiple payment methods
- Receipt generation

### Offline Support

- IndexedDB for local storage
- Automatic sync when online
- Queue for pending transactions

## State Management

### Zustand Stores

- `authStore` - Authentication & user state
- `cartStore` - Shopping cart (POS)
- `offlineStore` - Offline queue & sync

### TanStack Query

Used for server state management:
- Automatic caching
- Background refetching
- Optimistic updates
- Pagination

## API Integration

All API calls go through `src/services/api.ts`:

```typescript
import { api } from '@/services/api'

// Example: Login
const response = await api.auth.login(email, password)

// Example: Get products
const products = await api.get('/products')
```

### Authentication

API client automatically:
- Adds JWT token to requests
- Adds tenant ID header
- Refreshes expired tokens
- Redirects to login on 401

## Styling

Uses TailwindCSS with custom configuration:

```typescript
// Custom colors
colors: {
  primary: { /* blue shades */ }
}
```

### Touch Optimization

```css
.touch-manipulation {
  touch-action: manipulation;
}
```

Prevents zoom on double-tap for better UX on touch devices.

## Environment Variables

Create `.env` file:

```env
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000/ws
VITE_APP_NAME=Stumpf.works POS
VITE_ENABLE_OFFLINE=true
```

## Building for Production

```bash
npm run build
```

Output in `dist/` directory.

### Docker

Frontend is served via Nginx in production:

```bash
docker-compose up frontend
```

## Code Quality

### Linting

```bash
npm run lint
```

### Formatting

```bash
npm run format
```

Uses Prettier with custom configuration.

## Testing

```bash
# Run tests
npm test

# Run with UI
npm run test:ui

# Coverage
npm run test:coverage
```

Uses Vitest + React Testing Library.

## Troubleshooting

### Port already in use

Change port in `vite.config.ts`:

```typescript
server: {
  port: 5174
}
```

### API connection errors

Check:
1. Backend is running on correct port
2. CORS is configured correctly
3. Environment variables are set

## Contributing

1. Follow TypeScript best practices
2. Use functional components with hooks
3. Add types for all props and state
4. Write tests for new features
5. Format code before committing

## License

MIT License - see LICENSE file
