# Bakery Management Plugin - Frontend Integration

## Übersicht

Das Bakery Management Plugin erfordert eine umfassende Frontend-Integration für Bäckerei-spezifische Funktionen wie Rezeptverwaltung, Produktionsplanung, Chargenverfolgung und Frischemanagement.

## Erforderliche UI-Komponenten

### 1. Recipe Management (Rezeptverwaltung)

#### RecipeListView
```tsx
// src/pages/plugins/bakery/RecipeListView.tsx
import { useState, useEffect } from 'react';
import { DataTable } from '@/components/ui/data-table';
import { Button } from '@/components/ui/button';
import { Plus } from 'lucide-react';

interface Recipe {
  id: number;
  recipe_name: string;
  category: string;
  preparation_time: number;
  baking_time: number;
  baking_temperature: number;
  yield_quantity: number;
}

export function RecipeListView() {
  const [recipes, setRecipes] = useState<Recipe[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchRecipes();
  }, []);

  const fetchRecipes = async () => {
    try {
      const response = await fetch('/api/v1/bakery/recipes');
      const data = await response.json();
      setRecipes(data.recipes);
    } finally {
      setLoading(false);
    }
  };

  const columns = [
    { header: 'Rezeptname', accessor: 'recipe_name' },
    { header: 'Kategorie', accessor: 'category' },
    { header: 'Backzeit (Min)', accessor: 'baking_time' },
    { header: 'Temperatur (°C)', accessor: 'baking_temperature' },
    { header: 'Menge', accessor: 'yield_quantity' },
  ];

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Rezeptverwaltung</h1>
        <Button onClick={() => /* Navigate to create */}>
          <Plus className="mr-2 h-4 w-4" />
          Neues Rezept
        </Button>
      </div>

      <DataTable
        columns={columns}
        data={recipes}
        loading={loading}
      />
    </div>
  );
}
```

#### RecipeForm
```tsx
// src/pages/plugins/bakery/RecipeForm.tsx
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import { Form, FormField, FormItem, FormLabel, FormControl } from '@/components/ui/form';
import { Input } from '@/components/ui/input';
import { Select } from '@/components/ui/select';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';

const recipeSchema = z.object({
  recipe_name: z.string().min(1, 'Rezeptname erforderlich'),
  product_id: z.number(),
  category: z.enum(['bread', 'rolls', 'cake', 'pastry']),
  preparation_time: z.number().min(0),
  baking_time: z.number().min(0),
  baking_temperature: z.number().min(0).max(300),
  yield_quantity: z.number().min(0),
  instructions: z.string().optional(),
  ingredients: z.array(z.object({
    ingredient_name: z.string(),
    quantity: z.number(),
    unit: z.string(),
  })),
});

type RecipeFormData = z.infer<typeof recipeSchema>;

export function RecipeForm() {
  const form = useForm<RecipeFormData>({
    resolver: zodResolver(recipeSchema),
    defaultValues: {
      category: 'bread',
      ingredients: [],
    },
  });

  const onSubmit = async (data: RecipeFormData) => {
    try {
      const response = await fetch('/api/v1/bakery/recipes', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });

      if (response.ok) {
        // Navigate back or show success
      }
    } catch (error) {
      console.error('Failed to create recipe:', error);
    }
  };

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
        <FormField
          control={form.control}
          name="recipe_name"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Rezeptname</FormLabel>
              <FormControl>
                <Input {...field} placeholder="z.B. Bauernbrot" />
              </FormControl>
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="category"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Kategorie</FormLabel>
              <FormControl>
                <Select {...field}>
                  <option value="bread">Brot</option>
                  <option value="rolls">Brötchen</option>
                  <option value="cake">Kuchen</option>
                  <option value="pastry">Gebäck</option>
                </Select>
              </FormControl>
            </FormItem>
          )}
        />

        <div className="grid grid-cols-3 gap-4">
          <FormField
            control={form.control}
            name="preparation_time"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Vorbereitungszeit (Min)</FormLabel>
                <FormControl>
                  <Input type="number" {...field} />
                </FormControl>
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="baking_time"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Backzeit (Min)</FormLabel>
                <FormControl>
                  <Input type="number" {...field} />
                </FormControl>
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="baking_temperature"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Temperatur (°C)</FormLabel>
                <FormControl>
                  <Input type="number" {...field} />
                </FormControl>
              </FormItem>
            )}
          />
        </div>

        <FormField
          control={form.control}
          name="instructions"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Anleitung</FormLabel>
              <FormControl>
                <Textarea {...field} rows={6} />
              </FormControl>
            </FormItem>
          )}
        />

        {/* Ingredient section - dynamic list */}
        <IngredientList control={form.control} />

        <div className="flex justify-end gap-2">
          <Button type="button" variant="outline">Abbrechen</Button>
          <Button type="submit">Rezept speichern</Button>
        </div>
      </form>
    </Form>
  );
}
```

### 2. Production Planning (Produktionsplanung)

#### ProductionPlanCalendar
```tsx
// src/pages/plugins/bakery/ProductionPlanCalendar.tsx
import { Calendar } from '@/components/ui/calendar';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { useState } from 'react';

interface ProductionPlan {
  id: number;
  recipe_name: string;
  plan_date: string;
  planned_quantity: number;
  produced_quantity: number;
  status: 'planned' | 'in_progress' | 'completed';
}

export function ProductionPlanCalendar() {
  const [selectedDate, setSelectedDate] = useState<Date>(new Date());
  const [plans, setPlans] = useState<ProductionPlan[]>([]);

  const fetchPlansForDate = async (date: Date) => {
    const dateStr = date.toISOString().split('T')[0];
    const response = await fetch(`/api/v1/bakery/production-plans?date=${dateStr}`);
    const data = await response.json();
    setPlans(data.plans);
  };

  return (
    <div className="grid grid-cols-2 gap-6">
      <Card className="p-4">
        <Calendar
          mode="single"
          selected={selectedDate}
          onSelect={(date) => {
            if (date) {
              setSelectedDate(date);
              fetchPlansForDate(date);
            }
          }}
        />
      </Card>

      <Card className="p-4">
        <h3 className="text-lg font-semibold mb-4">
          Produktionsplan für {selectedDate.toLocaleDateString('de-DE')}
        </h3>

        <div className="space-y-3">
          {plans.map((plan) => (
            <div key={plan.id} className="border rounded-lg p-3">
              <div className="flex justify-between items-start">
                <div>
                  <h4 className="font-medium">{plan.recipe_name}</h4>
                  <p className="text-sm text-muted-foreground">
                    Geplant: {plan.planned_quantity} / Produziert: {plan.produced_quantity}
                  </p>
                </div>
                <Badge variant={
                  plan.status === 'completed' ? 'success' :
                  plan.status === 'in_progress' ? 'warning' : 'default'
                }>
                  {plan.status === 'completed' ? 'Abgeschlossen' :
                   plan.status === 'in_progress' ? 'In Arbeit' : 'Geplant'}
                </Badge>
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}
```

### 3. Batch Tracking (Chargenverfolgung)

#### BatchTrackingView
```tsx
// src/pages/plugins/bakery/BatchTrackingView.tsx
import { useState } from 'react';
import { QRCodeSVG } from 'qrcode.react';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { AlertCircle, CheckCircle, Clock } from 'lucide-react';

interface Batch {
  id: number;
  batch_number: string;
  recipe_name: string;
  production_date: string;
  best_before_date: string;
  quantity: number;
  batch_status: 'fresh' | 'expiring_soon' | 'expired';
}

export function BatchTrackingView() {
  const [batches, setBatches] = useState<Batch[]>([]);
  const [selectedBatch, setSelectedBatch] = useState<Batch | null>(null);

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'fresh': return <CheckCircle className="text-green-500" />;
      case 'expiring_soon': return <Clock className="text-yellow-500" />;
      case 'expired': return <AlertCircle className="text-red-500" />;
      default: return null;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'fresh': return 'success';
      case 'expiring_soon': return 'warning';
      case 'expired': return 'destructive';
      default: return 'default';
    }
  };

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Chargenverfolgung</h1>

      <div className="grid grid-cols-3 gap-4">
        {batches.map((batch) => (
          <Card
            key={batch.id}
            className="p-4 cursor-pointer hover:shadow-lg transition-shadow"
            onClick={() => setSelectedBatch(batch)}
          >
            <div className="flex items-start justify-between mb-3">
              <div>
                <h3 className="font-semibold">{batch.batch_number}</h3>
                <p className="text-sm text-muted-foreground">{batch.recipe_name}</p>
              </div>
              {getStatusIcon(batch.batch_status)}
            </div>

            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Produktion:</span>
                <span>{new Date(batch.production_date).toLocaleDateString('de-DE')}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Haltbar bis:</span>
                <span>{new Date(batch.best_before_date).toLocaleDateString('de-DE')}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Menge:</span>
                <span>{batch.quantity} Stück</span>
              </div>
            </div>

            <Badge className="mt-3 w-full justify-center" variant={getStatusColor(batch.batch_status)}>
              {batch.batch_status === 'fresh' ? 'Frisch' :
               batch.batch_status === 'expiring_soon' ? 'Läuft bald ab' : 'Abgelaufen'}
            </Badge>
          </Card>
        ))}
      </div>

      {/* Batch Details Modal */}
      {selectedBatch && (
        <BatchDetailsModal
          batch={selectedBatch}
          onClose={() => setSelectedBatch(null)}
        />
      )}
    </div>
  );
}

function BatchDetailsModal({ batch, onClose }: { batch: Batch; onClose: () => void }) {
  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <Card className="p-6 max-w-md w-full">
        <h2 className="text-xl font-bold mb-4">Charge {batch.batch_number}</h2>

        <div className="flex justify-center mb-4">
          <QRCodeSVG value={batch.batch_number} size={200} />
        </div>

        <div className="space-y-3">
          <div>
            <span className="font-medium">Produkt:</span> {batch.recipe_name}
          </div>
          <div>
            <span className="font-medium">Produktionsdatum:</span> {new Date(batch.production_date).toLocaleDateString('de-DE')}
          </div>
          <div>
            <span className="font-medium">Mindesthaltbarkeitsdatum:</span> {new Date(batch.best_before_date).toLocaleDateString('de-DE')}
          </div>
          <div>
            <span className="font-medium">Menge:</span> {batch.quantity} Stück
          </div>
        </div>

        <div className="flex gap-2 mt-6">
          <Button variant="outline" className="flex-1" onClick={onClose}>
            Schließen
          </Button>
          <Button className="flex-1" onClick={() => window.print()}>
            QR-Code drucken
          </Button>
        </div>
      </Card>
    </div>
  );
}
```

### 4. Baking Sheet Generator (Backzettel-Generator)

#### BakingSheetGenerator
```tsx
// src/pages/plugins/bakery/BakingSheetGenerator.tsx
import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Printer } from 'lucide-react';

interface BakingSheet {
  sheet_date: string;
  items: Array<{
    recipe_name: string;
    quantity: number;
    ingredients: Array<{
      ingredient_name: string;
      total_quantity: number;
      unit: string;
    }>;
    baking_time: number;
    baking_temperature: number;
  }>;
}

export function BakingSheetGenerator() {
  const [date, setDate] = useState<string>(new Date().toISOString().split('T')[0]);
  const [bakingSheet, setBakingSheet] = useState<BakingSheet | null>(null);

  const generateSheet = async () => {
    const response = await fetch('/api/v1/bakery/baking-sheets/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ sheet_date: date }),
    });
    const data = await response.json();
    setBakingSheet(data);
  };

  const printSheet = () => {
    window.print();
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Backzettel Generator</h1>
        <div className="flex gap-2">
          <input
            type="date"
            value={date}
            onChange={(e) => setDate(e.target.value)}
            className="border rounded px-3 py-2"
          />
          <Button onClick={generateSheet}>Generieren</Button>
          {bakingSheet && (
            <Button onClick={printSheet} variant="outline">
              <Printer className="mr-2 h-4 w-4" />
              Drucken
            </Button>
          )}
        </div>
      </div>

      {bakingSheet && (
        <div className="print:p-8 space-y-6">
          <Card className="p-6 print:shadow-none">
            <h2 className="text-xl font-bold mb-4">
              Backzettel für {new Date(bakingSheet.sheet_date).toLocaleDateString('de-DE')}
            </h2>

            {bakingSheet.items.map((item, index) => (
              <div key={index} className="mb-8 pb-6 border-b last:border-b-0">
                <h3 className="text-lg font-semibold mb-2">
                  {item.recipe_name} ({item.quantity} Stück)
                </h3>

                <div className="grid grid-cols-2 gap-6 mt-4">
                  <div>
                    <h4 className="font-medium mb-2">Zutaten:</h4>
                    <ul className="space-y-1">
                      {item.ingredients.map((ing, idx) => (
                        <li key={idx} className="text-sm">
                          {ing.ingredient_name}: {ing.total_quantity} {ing.unit}
                        </li>
                      ))}
                    </ul>
                  </div>

                  <div>
                    <h4 className="font-medium mb-2">Backanleitung:</h4>
                    <div className="space-y-1 text-sm">
                      <div>Backzeit: {item.baking_time} Minuten</div>
                      <div>Temperatur: {item.baking_temperature}°C</div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </Card>
        </div>
      )}
    </div>
  );
}
```

## Routing-Konfiguration

```tsx
// src/routes/bakeryRoutes.tsx
import { Route } from 'react-router-dom';
import { RecipeListView } from '@/pages/plugins/bakery/RecipeListView';
import { RecipeForm } from '@/pages/plugins/bakery/RecipeForm';
import { ProductionPlanCalendar } from '@/pages/plugins/bakery/ProductionPlanCalendar';
import { BatchTrackingView } from '@/pages/plugins/bakery/BatchTrackingView';
import { BakingSheetGenerator } from '@/pages/plugins/bakery/BakingSheetGenerator';
import { WasteTrackingView } from '@/pages/plugins/bakery/WasteTrackingView';

export const bakeryRoutes = (
  <Route path="/bakery">
    <Route path="recipes" element={<RecipeListView />} />
    <Route path="recipes/new" element={<RecipeForm />} />
    <Route path="recipes/:id/edit" element={<RecipeForm />} />
    <Route path="production" element={<ProductionPlanCalendar />} />
    <Route path="batches" element={<BatchTrackingView />} />
    <Route path="baking-sheets" element={<BakingSheetGenerator />} />
    <Route path="waste" element={<WasteTrackingView />} />
  </Route>
);
```

## State Management (Zustand)

```tsx
// src/stores/bakeryStore.ts
import { create } from 'zustand';

interface Recipe {
  id: number;
  recipe_name: string;
  category: string;
  baking_time: number;
  baking_temperature: number;
}

interface ProductionPlan {
  id: number;
  recipe_id: number;
  plan_date: string;
  planned_quantity: number;
  status: string;
}

interface BakeryStore {
  recipes: Recipe[];
  productionPlans: ProductionPlan[];
  selectedDate: Date;

  setRecipes: (recipes: Recipe[]) => void;
  setProductionPlans: (plans: ProductionPlan[]) => void;
  setSelectedDate: (date: Date) => void;

  fetchRecipes: () => Promise<void>;
  fetchProductionPlans: (date: Date) => Promise<void>;
}

export const useBakeryStore = create<BakeryStore>((set) => ({
  recipes: [],
  productionPlans: [],
  selectedDate: new Date(),

  setRecipes: (recipes) => set({ recipes }),
  setProductionPlans: (productionPlans) => set({ productionPlans }),
  setSelectedDate: (selectedDate) => set({ selectedDate }),

  fetchRecipes: async () => {
    const response = await fetch('/api/v1/bakery/recipes');
    const data = await response.json();
    set({ recipes: data.recipes });
  },

  fetchProductionPlans: async (date: Date) => {
    const dateStr = date.toISOString().split('T')[0];
    const response = await fetch(`/api/v1/bakery/production-plans?date=${dateStr}`);
    const data = await response.json();
    set({ productionPlans: data.plans });
  },
}));
```

## Navigation Menu Integration

```tsx
// src/components/layout/Sidebar.tsx - Add bakery menu items
{isPluginActive('bakery_management') && (
  <DropdownMenuItem>
    <ChefHat className="mr-2 h-4 w-4" />
    <span>Bäckerei</span>
    <DropdownMenuContent side="right">
      <DropdownMenuItem onClick={() => navigate('/bakery/recipes')}>
        Rezeptverwaltung
      </DropdownMenuItem>
      <DropdownMenuItem onClick={() => navigate('/bakery/production')}>
        Produktionsplanung
      </DropdownMenuItem>
      <DropdownMenuItem onClick={() => navigate('/bakery/batches')}>
        Chargenverfolgung
      </DropdownMenuItem>
      <DropdownMenuItem onClick={() => navigate('/bakery/baking-sheets')}>
        Backzettel
      </DropdownMenuItem>
      <DropdownMenuItem onClick={() => navigate('/bakery/waste')}>
        Abfallverwaltung
      </DropdownMenuItem>
    </DropdownMenuContent>
  </DropdownMenuItem>
)}
```

## API Client Hooks

```tsx
// src/hooks/useBakery.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

export function useRecipes() {
  return useQuery({
    queryKey: ['bakery', 'recipes'],
    queryFn: async () => {
      const response = await fetch('/api/v1/bakery/recipes');
      return response.json();
    },
  });
}

export function useCreateRecipe() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: RecipeFormData) => {
      const response = await fetch('/api/v1/bakery/recipes', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['bakery', 'recipes'] });
    },
  });
}

export function useProductionPlans(date: string) {
  return useQuery({
    queryKey: ['bakery', 'production-plans', date],
    queryFn: async () => {
      const response = await fetch(`/api/v1/bakery/production-plans?date=${date}`);
      return response.json();
    },
  });
}

export function useBatches() {
  return useQuery({
    queryKey: ['bakery', 'batches'],
    queryFn: async () => {
      const response = await fetch('/api/v1/bakery/batches');
      return response.json();
    },
  });
}
```

## Styling und Icons

Empfohlene Icons von lucide-react:
- `ChefHat` - Hauptmenü Bäckerei
- `BookOpen` - Rezepte
- `Calendar` - Produktionsplanung
- `Package` - Chargen
- `FileText` - Backzettel
- `Trash2` - Abfallverwaltung
- `Clock` - Zeiten
- `Thermometer` - Temperatur

## Testing

```tsx
// src/pages/plugins/bakery/__tests__/RecipeForm.test.tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { RecipeForm } from '../RecipeForm';

describe('RecipeForm', () => {
  it('should render all form fields', () => {
    render(<RecipeForm />);

    expect(screen.getByLabelText('Rezeptname')).toBeInTheDocument();
    expect(screen.getByLabelText('Kategorie')).toBeInTheDocument();
    expect(screen.getByLabelText('Backzeit (Min)')).toBeInTheDocument();
  });

  it('should submit form with valid data', async () => {
    render(<RecipeForm />);

    fireEvent.change(screen.getByLabelText('Rezeptname'), {
      target: { value: 'Bauernbrot' },
    });

    fireEvent.click(screen.getByText('Rezept speichern'));

    await waitFor(() => {
      // Assert API call was made
    });
  });
});
```

## Deployment Checklist

- [ ] Alle Komponenten erstellt
- [ ] Routing konfiguriert
- [ ] State Management implementiert
- [ ] API Hooks eingebunden
- [ ] Navigation Menu aktualisiert
- [ ] Icons importiert
- [ ] Formulare mit Validierung
- [ ] Tests geschrieben
- [ ] Responsive Design geprüft
- [ ] Print-Styles für Backzettel
- [ ] QR-Code-Generator für Chargen
