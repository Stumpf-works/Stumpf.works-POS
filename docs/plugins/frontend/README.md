# Stumpf.works POS - Frontend Plugin Integration Guide

## Übersicht

Dieses Dokument beschreibt die Frontend-Integration der vier neuen POS-Plugins:

1. **Bakery Management** - Rezeptverwaltung, Produktionsplanung, Chargenverfolgung
2. **Delivery Management** - Lieferauftragsverwaltung, Fahrer-Tracking, GPS-Integration
3. **Advanced Analytics** - Dashboards, Berichte, Prognosen, Datenexport
4. **Payment Gateway** - Multi-Provider-Zahlungen, Terminals, Transaktionsverwaltung

## Projekt-Setup

### 1. Dependencies installieren

```bash
# Navigation
npm install react-router-dom

# UI Components (falls noch nicht vorhanden)
npm install @radix-ui/react-dialog @radix-ui/react-dropdown-menu @radix-ui/react-select
npm install @radix-ui/react-tabs @radix-ui/react-toast @radix-ui/react-switch
npm install lucide-react

# Forms & Validation
npm install react-hook-form @hookform/resolvers zod

# State Management
npm install zustand

# Data Fetching
npm install @tanstack/react-query axios

# Charts & Visualizations
npm install recharts react-grid-layout

# Maps (Delivery Plugin)
npm install leaflet react-leaflet

# Payments (Payment Plugin)
npm install @stripe/stripe-js @stripe/react-stripe-js

# QR Codes (Bakery & Payment)
npm install qrcode.react

# Date Handling
npm install date-fns

# Export Tools
npm install jspdf jspdf-autotable

# WebSocket (Delivery Real-time)
npm install socket.io-client
```

### 2. TypeScript-Konfiguration

Stelle sicher, dass deine `tsconfig.json` path aliases enthält:

```json
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"]
    }
  }
}
```

### 3. Environment Variables

Erstelle eine `.env.local` Datei:

```env
# API
REACT_APP_API_URL=http://localhost:8000/api/v1
REACT_APP_WS_URL=ws://localhost:8000

# Payment Providers (Test Keys)
REACT_APP_STRIPE_PUBLIC_KEY=pk_test_...
REACT_APP_PAYPAL_CLIENT_ID=...

# Maps
REACT_APP_MAP_TILE_URL=https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png
```

## Projektstruktur

```
frontend/
├── src/
│   ├── pages/
│   │   └── plugins/
│   │       ├── bakery/
│   │       │   ├── RecipeListView.tsx
│   │       │   ├── RecipeForm.tsx
│   │       │   ├── ProductionPlanCalendar.tsx
│   │       │   ├── BatchTrackingView.tsx
│   │       │   └── BakingSheetGenerator.tsx
│   │       ├── delivery/
│   │       │   ├── DeliveryDashboard.tsx
│   │       │   ├── LiveTrackingMap.tsx
│   │       │   ├── OrderAssignmentView.tsx
│   │       │   ├── DriverManagementView.tsx
│   │       │   └── CustomerTrackingWidget.tsx
│   │       ├── analytics/
│   │       │   ├── AnalyticsDashboard.tsx
│   │       │   ├── ReportBuilder.tsx
│   │       │   ├── DashboardBuilder.tsx
│   │       │   ├── ForecastView.tsx
│   │       │   └── DataExportTool.tsx
│   │       └── payment/
│   │           ├── PaymentProviderList.tsx
│   │           ├── PaymentCheckout.tsx
│   │           ├── TransactionHistory.tsx
│   │           ├── TerminalManagement.tsx
│   │           └── ReconciliationView.tsx
│   ├── components/
│   │   ├── ui/           # shadcn/ui components
│   │   └── shared/       # Shared plugin components
│   ├── hooks/
│   │   ├── useBakery.ts
│   │   ├── useDelivery.ts
│   │   ├── useAnalytics.ts
│   │   └── usePayment.ts
│   ├── stores/
│   │   ├── bakeryStore.ts
│   │   ├── deliveryStore.ts
│   │   ├── analyticsStore.ts
│   │   └── paymentStore.ts
│   ├── services/
│   │   ├── api.ts
│   │   ├── deliverySocket.ts
│   │   └── paymentSecurity.ts
│   ├── routes/
│   │   ├── index.tsx
│   │   ├── bakeryRoutes.tsx
│   │   ├── deliveryRoutes.tsx
│   │   ├── analyticsRoutes.tsx
│   │   └── paymentRoutes.tsx
│   └── types/
│       ├── bakery.ts
│       ├── delivery.ts
│       ├── analytics.ts
│       └── payment.ts
```

## Routing-Integration

### App-Router Setup

```tsx
// src/routes/index.tsx
import { createBrowserRouter, RouterProvider } from 'react-router-dom';
import { bakeryRoutes } from './bakeryRoutes';
import { deliveryRoutes } from './deliveryRoutes';
import { analyticsRoutes } from './analyticsRoutes';
import { paymentRoutes } from './paymentRoutes';

const router = createBrowserRouter([
  {
    path: '/',
    element: <MainLayout />,
    children: [
      // Existing routes...
      bakeryRoutes,
      deliveryRoutes,
      analyticsRoutes,
      paymentRoutes,
    ],
  },
]);

export function AppRouter() {
  return <RouterProvider router={router} />;
}
```

### Navigation Menu Integration

```tsx
// src/components/layout/Sidebar.tsx
import { ChefHat, Truck, BarChart3, CreditCard } from 'lucide-react';

export function Sidebar() {
  const { activePlugins } = usePlugins();

  return (
    <nav>
      {/* Existing menu items... */}

      {activePlugins.includes('bakery_management') && (
        <NavItem icon={<ChefHat />} label="Bäckerei" href="/bakery" />
      )}

      {activePlugins.includes('delivery_management') && (
        <NavItem icon={<Truck />} label="Lieferung" href="/delivery" />
      )}

      {activePlugins.includes('advanced_analytics') && (
        <NavItem icon={<BarChart3 />} label="Analytics" href="/analytics" />
      )}

      {activePlugins.includes('payment_gateway') && (
        <NavItem icon={<CreditCard />} label="Zahlungen" href="/payments" />
      )}
    </nav>
  );
}
```

## API-Integration

### Axios Instance Setup

```tsx
// src/services/api.ts
import axios from 'axios';

const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request Interceptor - Add Auth Token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response Interceptor - Handle Errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Redirect to login
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;
```

### React Query Setup

```tsx
// src/App.tsx
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
});

export function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AppRouter />
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  );
}
```

### Custom Hooks per Plugin

```tsx
// src/hooks/useBakery.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '@/services/api';

export function useRecipes() {
  return useQuery({
    queryKey: ['bakery', 'recipes'],
    queryFn: async () => {
      const { data } = await api.get('/bakery/recipes');
      return data.recipes;
    },
  });
}

export function useCreateRecipe() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (recipeData: any) => {
      const { data } = await api.post('/bakery/recipes', recipeData);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['bakery', 'recipes'] });
    },
  });
}
```

## State Management

### Zustand Store Setup

```tsx
// src/stores/pluginStore.ts
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface PluginState {
  activePlugins: string[];
  settings: Record<string, any>;
  setActivePlugins: (plugins: string[]) => void;
  setPluginSettings: (pluginName: string, settings: any) => void;
}

export const usePluginStore = create<PluginState>()(
  persist(
    (set) => ({
      activePlugins: [],
      settings: {},

      setActivePlugins: (plugins) => set({ activePlugins: plugins }),

      setPluginSettings: (pluginName, settings) =>
        set((state) => ({
          settings: { ...state.settings, [pluginName]: settings },
        })),
    }),
    {
      name: 'plugin-storage',
    }
  )
);
```

## Gemeinsame Komponenten

### Plugin Card Component

```tsx
// src/components/shared/PluginCard.tsx
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

interface PluginCardProps {
  title: string;
  description: string;
  icon: React.ReactNode;
  status: 'active' | 'inactive';
  version: string;
  onToggle: () => void;
}

export function PluginCard({
  title,
  description,
  icon,
  status,
  version,
  onToggle,
}: PluginCardProps) {
  return (
    <Card className="p-6">
      <div className="flex items-start gap-4">
        <div className="text-4xl">{icon}</div>
        <div className="flex-1">
          <div className="flex justify-between items-start mb-2">
            <h3 className="text-lg font-semibold">{title}</h3>
            <Badge variant={status === 'active' ? 'success' : 'secondary'}>
              {status === 'active' ? 'Aktiv' : 'Inaktiv'}
            </Badge>
          </div>
          <p className="text-sm text-muted-foreground mb-3">{description}</p>
          <div className="flex justify-between items-center">
            <span className="text-xs text-muted-foreground">Version {version}</span>
            <Button size="sm" variant={status === 'active' ? 'outline' : 'default'} onClick={onToggle}>
              {status === 'active' ? 'Deaktivieren' : 'Aktivieren'}
            </Button>
          </div>
        </div>
      </div>
    </Card>
  );
}
```

### Loading States

```tsx
// src/components/shared/LoadingState.tsx
import { Loader2 } from 'lucide-react';

export function LoadingState({ message = 'Lädt...' }: { message?: string }) {
  return (
    <div className="flex flex-col items-center justify-center h-64">
      <Loader2 className="h-8 w-8 animate-spin text-primary mb-4" />
      <p className="text-muted-foreground">{message}</p>
    </div>
  );
}
```

### Error States

```tsx
// src/components/shared/ErrorState.tsx
import { AlertCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';

export function ErrorState({
  message = 'Ein Fehler ist aufgetreten',
  onRetry,
}: {
  message?: string;
  onRetry?: () => void;
}) {
  return (
    <div className="flex flex-col items-center justify-center h-64">
      <AlertCircle className="h-12 w-12 text-red-500 mb-4" />
      <p className="text-muted-foreground mb-4">{message}</p>
      {onRetry && (
        <Button onClick={onRetry} variant="outline">
          Erneut versuchen
        </Button>
      )}
    </div>
  );
}
```

## Plugin-spezifische Dokumentation

Detaillierte Frontend-Implementierungen für jeden Plugin:

- [Bakery Management Frontend →](./bakery-management-frontend.md)
- [Delivery Management Frontend →](./delivery-management-frontend.md)
- [Advanced Analytics Frontend →](./advanced-analytics-frontend.md)
- [Payment Gateway Frontend →](./payment-gateway-frontend.md)

## Testing

### Component Tests

```tsx
// src/pages/plugins/bakery/__tests__/RecipeListView.test.tsx
import { render, screen, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { RecipeListView } from '../RecipeListView';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { retry: false },
  },
});

describe('RecipeListView', () => {
  it('should display recipes', async () => {
    render(
      <QueryClientProvider client={queryClient}>
        <RecipeListView />
      </QueryClientProvider>
    );

    await waitFor(() => {
      expect(screen.getByText('Rezeptverwaltung')).toBeInTheDocument();
    });
  });
});
```

### E2E Tests (Cypress/Playwright)

```typescript
// cypress/e2e/bakery.cy.ts
describe('Bakery Plugin', () => {
  beforeEach(() => {
    cy.login(); // Custom command
    cy.visit('/bakery');
  });

  it('should create a new recipe', () => {
    cy.contains('Neues Rezept').click();
    cy.get('input[name="recipe_name"]').type('Test Brot');
    cy.get('select[name="category"]').select('bread');
    cy.contains('Rezept speichern').click();

    cy.contains('Test Brot').should('be.visible');
  });
});
```

## Performance-Optimierung

### Code Splitting

```tsx
// src/routes/bakeryRoutes.tsx
import { lazy, Suspense } from 'react';
import { LoadingState } from '@/components/shared/LoadingState';

const RecipeListView = lazy(() => import('@/pages/plugins/bakery/RecipeListView'));
const RecipeForm = lazy(() => import('@/pages/plugins/bakery/RecipeForm'));

export const bakeryRoutes = {
  path: '/bakery',
  children: [
    {
      path: 'recipes',
      element: (
        <Suspense fallback={<LoadingState />}>
          <RecipeListView />
        </Suspense>
      ),
    },
    // ...more routes
  ],
};
```

### Memoization

```tsx
import { memo, useMemo } from 'react';

export const RecipeCard = memo(({ recipe }: { recipe: Recipe }) => {
  const ingredients = useMemo(
    () => recipe.ingredients.map((i) => i.name).join(', '),
    [recipe.ingredients]
  );

  return (
    <Card>
      <h3>{recipe.name}</h3>
      <p>{ingredients}</p>
    </Card>
  );
});
```

## Deployment

### Build für Produktion

```bash
# Build optimiert
npm run build

# Umgebungsvariablen für Produktion
REACT_APP_API_URL=https://api.stumpf.works
REACT_APP_STRIPE_PUBLIC_KEY=pk_live_...
```

### Docker Integration

```dockerfile
# frontend/Dockerfile
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

## Best Practices

### 1. Type Safety

```tsx
// Definiere Types für alle Plugin-Entitäten
interface Recipe {
  id: number;
  recipe_name: string;
  category: 'bread' | 'rolls' | 'cake' | 'pastry';
  baking_time: number;
  baking_temperature: number;
}

// Verwende Type Guards
function isRecipe(obj: any): obj is Recipe {
  return obj && typeof obj.recipe_name === 'string';
}
```

### 2. Error Handling

```tsx
try {
  const data = await api.post('/bakery/recipes', recipeData);
  toast.success('Rezept erfolgreich gespeichert');
} catch (error) {
  if (axios.isAxiosError(error)) {
    const message = error.response?.data?.message || 'Ein Fehler ist aufgetreten';
    toast.error(message);
  }
}
```

### 3. Accessibility

```tsx
// Verwende semantic HTML
<button aria-label="Rezept löschen" onClick={handleDelete}>
  <Trash2 />
</button>

// Keyboard Navigation
<div role="listbox" onKeyDown={handleKeyDown}>
  {/* items */}
</div>
```

### 4. Responsive Design

```tsx
// Verwende Tailwind responsive classes
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
  {/* cards */}
</div>
```

## Nächste Schritte

1. ✅ Dependencies installieren
2. ✅ Environment Variables konfigurieren
3. ✅ Routing setup
4. ✅ API-Integration testen
5. ⬜ Plugin für Plugin implementieren
6. ⬜ Tests schreiben
7. ⬜ Production Build testen
8. ⬜ Deployment vorbereiten

## Support & Resources

- [Bakery Plugin Docs](./bakery-management-frontend.md)
- [Delivery Plugin Docs](./delivery-management-frontend.md)
- [Analytics Plugin Docs](./advanced-analytics-frontend.md)
- [Payment Plugin Docs](./payment-gateway-frontend.md)
- [Backend API Dokumentation](../../backend/README.md)
- [Figma Designs](https://figma.com/...)

## Fragen?

Bei Fragen zur Frontend-Integration:
- GitHub Issues: https://github.com/Stumpf-works/Stumpf.works-POS/issues
- Email: dev@stumpf.works
