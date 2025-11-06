# Advanced Analytics & Reporting Plugin - Frontend Integration

## Übersicht

Das Advanced Analytics & Reporting Plugin benötigt eine umfassende Frontend-Integration für Datenvisualisierung, Dashboard-Erstellung, Report-Builder und Forecasting-Tools.

## Erforderliche Dependencies

```json
{
  "dependencies": {
    "recharts": "^2.10.3",
    "react-grid-layout": "^1.4.4",
    "date-fns": "^2.30.0",
    "react-export-table-to-excel": "^1.0.6",
    "jspdf": "^2.5.1",
    "jspdf-autotable": "^3.7.1",
    "@tanstack/react-table": "^8.11.0"
  }
}
```

## Erforderliche UI-Komponenten

### 1. Analytics Dashboard (Haupt-Dashboard)

#### AnalyticsDashboard
```tsx
// src/pages/plugins/analytics/AnalyticsDashboard.tsx
import { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { TrendingUp, DollarSign, ShoppingCart, Users } from 'lucide-react';

interface DashboardData {
  sales_today: number;
  sales_yesterday: number;
  orders_today: number;
  customers_today: number;
  revenue_trend: Array<{ date: string; revenue: number }>;
  top_products: Array<{ name: string; revenue: number }>;
  payment_methods: Array<{ method: string; amount: number }>;
}

export function AnalyticsDashboard() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [dateRange, setDateRange] = useState('7d');

  useEffect(() => {
    fetchDashboardData();
  }, [dateRange]);

  const fetchDashboardData = async () => {
    const response = await fetch(`/api/v1/analytics/dashboard?range=${dateRange}`);
    const result = await response.json();
    setData(result);
  };

  if (!data) return <div>Lädt Dashboard...</div>;

  const salesChange =
    ((data.sales_today - data.sales_yesterday) / data.sales_yesterday) * 100;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Analytics Dashboard</h1>

        <select
          value={dateRange}
          onChange={(e) => setDateRange(e.target.value)}
          className="border rounded px-3 py-2"
        >
          <option value="1d">Heute</option>
          <option value="7d">7 Tage</option>
          <option value="30d">30 Tage</option>
          <option value="90d">90 Tage</option>
        </select>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-4 gap-4">
        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted-foreground">Umsatz Heute</p>
              <p className="text-2xl font-bold">{data.sales_today.toFixed(2)} €</p>
              <p
                className={`text-sm ${
                  salesChange >= 0 ? 'text-green-600' : 'text-red-600'
                }`}
              >
                {salesChange >= 0 ? '+' : ''}
                {salesChange.toFixed(1)}% vs. gestern
              </p>
            </div>
            <DollarSign className="h-8 w-8 text-green-500" />
          </div>
        </Card>

        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted-foreground">Bestellungen</p>
              <p className="text-2xl font-bold">{data.orders_today}</p>
            </div>
            <ShoppingCart className="h-8 w-8 text-blue-500" />
          </div>
        </Card>

        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted-foreground">Kunden</p>
              <p className="text-2xl font-bold">{data.customers_today}</p>
            </div>
            <Users className="h-8 w-8 text-purple-500" />
          </div>
        </Card>

        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted-foreground">Ø Bestellwert</p>
              <p className="text-2xl font-bold">
                {(data.sales_today / data.orders_today).toFixed(2)} €
              </p>
            </div>
            <TrendingUp className="h-8 w-8 text-orange-500" />
          </div>
        </Card>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-2 gap-6">
        {/* Revenue Trend */}
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4">Umsatzentwicklung</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={data.revenue_trend}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line
                type="monotone"
                dataKey="revenue"
                stroke="#8884d8"
                strokeWidth={2}
                name="Umsatz (€)"
              />
            </LineChart>
          </ResponsiveContainer>
        </Card>

        {/* Top Products */}
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4">Top Produkte</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={data.top_products}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="revenue" fill="#82ca9d" name="Umsatz (€)" />
            </BarChart>
          </ResponsiveContainer>
        </Card>

        {/* Payment Methods */}
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4">Zahlungsmethoden</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={data.payment_methods}
                dataKey="amount"
                nameKey="method"
                cx="50%"
                cy="50%"
                outerRadius={100}
                label
              >
                {data.payment_methods.map((entry, index) => (
                  <Cell
                    key={`cell-${index}`}
                    fill={['#0088FE', '#00C49F', '#FFBB28', '#FF8042'][index % 4]}
                  />
                ))}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </Card>

        {/* Additional widget placeholder */}
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4">Kundenanalyse</h3>
          <div className="h-[300px] flex items-center justify-center text-muted-foreground">
            Weitere Widgets hier...
          </div>
        </Card>
      </div>

      <Tabs defaultValue="sales">
        <TabsList>
          <TabsTrigger value="sales">Verkäufe</TabsTrigger>
          <TabsTrigger value="products">Produkte</TabsTrigger>
          <TabsTrigger value="customers">Kunden</TabsTrigger>
          <TabsTrigger value="forecast">Prognose</TabsTrigger>
        </TabsList>

        <TabsContent value="sales">
          <SalesAnalysisView />
        </TabsContent>

        <TabsContent value="products">
          <ProductAnalysisView />
        </TabsContent>

        <TabsContent value="customers">
          <CustomerAnalysisView />
        </TabsContent>

        <TabsContent value="forecast">
          <ForecastView />
        </TabsContent>
      </Tabs>
    </div>
  );
}
```

### 2. Report Builder (Berichtserstellung)

#### ReportBuilder
```tsx
// src/pages/plugins/analytics/ReportBuilder.tsx
import { useState } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select } from '@/components/ui/select';
import { Checkbox } from '@/components/ui/checkbox';
import { Label } from '@/components/ui/label';
import { Plus, Save, Play } from 'lucide-react';

interface ReportConfig {
  report_name: string;
  report_type: string;
  date_from: string;
  date_to: string;
  grouping: string;
  metrics: string[];
  filters: Record<string, any>;
  schedule_frequency?: string;
  email_recipients?: string;
}

export function ReportBuilder() {
  const [config, setConfig] = useState<ReportConfig>({
    report_name: '',
    report_type: 'sales',
    date_from: '',
    date_to: '',
    grouping: 'daily',
    metrics: [],
    filters: {},
  });

  const [previewData, setPreviewData] = useState<any>(null);

  const availableMetrics = [
    { id: 'total_sales', label: 'Gesamtumsatz' },
    { id: 'order_count', label: 'Anzahl Bestellungen' },
    { id: 'average_order_value', label: 'Durchschnittlicher Bestellwert' },
    { id: 'customer_count', label: 'Kundenanzahl' },
    { id: 'product_quantity', label: 'Verkaufte Menge' },
  ];

  const handleMetricToggle = (metricId: string) => {
    setConfig((prev) => ({
      ...prev,
      metrics: prev.metrics.includes(metricId)
        ? prev.metrics.filter((m) => m !== metricId)
        : [...prev.metrics, metricId],
    }));
  };

  const runPreview = async () => {
    const response = await fetch('/api/v1/analytics/reports/preview', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(config),
    });
    const data = await response.json();
    setPreviewData(data);
  };

  const saveReport = async () => {
    await fetch('/api/v1/analytics/reports', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(config),
    });
    // Navigate back or show success
  };

  return (
    <div className="grid grid-cols-3 gap-6">
      {/* Configuration Panel */}
      <div className="col-span-1 space-y-4">
        <Card className="p-4">
          <h2 className="text-lg font-semibold mb-4">Bericht konfigurieren</h2>

          <div className="space-y-4">
            <div>
              <Label>Berichtsname</Label>
              <Input
                value={config.report_name}
                onChange={(e) =>
                  setConfig((prev) => ({ ...prev, report_name: e.target.value }))
                }
                placeholder="z.B. Wöchentlicher Umsatzbericht"
              />
            </div>

            <div>
              <Label>Berichtstyp</Label>
              <Select
                value={config.report_type}
                onChange={(e) =>
                  setConfig((prev) => ({ ...prev, report_type: e.target.value }))
                }
              >
                <option value="sales">Verkaufsbericht</option>
                <option value="products">Produktbericht</option>
                <option value="customers">Kundenbericht</option>
                <option value="inventory">Bestandsbericht</option>
              </Select>
            </div>

            <div className="grid grid-cols-2 gap-2">
              <div>
                <Label>Von</Label>
                <Input
                  type="date"
                  value={config.date_from}
                  onChange={(e) =>
                    setConfig((prev) => ({ ...prev, date_from: e.target.value }))
                  }
                />
              </div>
              <div>
                <Label>Bis</Label>
                <Input
                  type="date"
                  value={config.date_to}
                  onChange={(e) =>
                    setConfig((prev) => ({ ...prev, date_to: e.target.value }))
                  }
                />
              </div>
            </div>

            <div>
              <Label>Gruppierung</Label>
              <Select
                value={config.grouping}
                onChange={(e) =>
                  setConfig((prev) => ({ ...prev, grouping: e.target.value }))
                }
              >
                <option value="daily">Täglich</option>
                <option value="weekly">Wöchentlich</option>
                <option value="monthly">Monatlich</option>
                <option value="yearly">Jährlich</option>
              </Select>
            </div>

            <div>
              <Label className="mb-2 block">Metriken</Label>
              <div className="space-y-2">
                {availableMetrics.map((metric) => (
                  <div key={metric.id} className="flex items-center gap-2">
                    <Checkbox
                      checked={config.metrics.includes(metric.id)}
                      onCheckedChange={() => handleMetricToggle(metric.id)}
                    />
                    <label className="text-sm">{metric.label}</label>
                  </div>
                ))}
              </div>
            </div>

            <div className="border-t pt-4">
              <Label className="mb-2 block">Automatisierung (optional)</Label>

              <div className="space-y-2">
                <Select
                  value={config.schedule_frequency || ''}
                  onChange={(e) =>
                    setConfig((prev) => ({
                      ...prev,
                      schedule_frequency: e.target.value,
                    }))
                  }
                >
                  <option value="">Keine Planung</option>
                  <option value="daily">Täglich</option>
                  <option value="weekly">Wöchentlich</option>
                  <option value="monthly">Monatlich</option>
                </Select>

                <Input
                  placeholder="E-Mail-Empfänger (kommagetrennt)"
                  value={config.email_recipients || ''}
                  onChange={(e) =>
                    setConfig((prev) => ({
                      ...prev,
                      email_recipients: e.target.value,
                    }))
                  }
                />
              </div>
            </div>

            <div className="flex gap-2">
              <Button onClick={runPreview} variant="outline" className="flex-1">
                <Play className="mr-2 h-4 w-4" />
                Vorschau
              </Button>
              <Button onClick={saveReport} className="flex-1">
                <Save className="mr-2 h-4 w-4" />
                Speichern
              </Button>
            </div>
          </div>
        </Card>
      </div>

      {/* Preview Panel */}
      <div className="col-span-2">
        <Card className="p-4">
          <h2 className="text-lg font-semibold mb-4">Vorschau</h2>

          {previewData ? (
            <div>
              <ReportPreview data={previewData} config={config} />
            </div>
          ) : (
            <div className="h-96 flex items-center justify-center text-muted-foreground">
              Konfigurieren Sie den Bericht und klicken Sie auf "Vorschau"
            </div>
          )}
        </Card>
      </div>
    </div>
  );
}
```

### 3. Custom Dashboard Builder (Dashboard-Editor)

#### DashboardBuilder
```tsx
// src/pages/plugins/analytics/DashboardBuilder.tsx
import { useState } from 'react';
import GridLayout from 'react-grid-layout';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Plus, Settings, Trash2 } from 'lucide-react';
import 'react-grid-layout/css/styles.css';
import 'react-resizable/css/styles.css';

interface Widget {
  id: string;
  type: string;
  title: string;
  config: any;
  x: number;
  y: number;
  w: number;
  h: number;
}

const WIDGET_TYPES = [
  { type: 'sales_chart', label: 'Verkaufschart' },
  { type: 'revenue_kpi', label: 'Umsatz KPI' },
  { type: 'orders_kpi', label: 'Bestellungen KPI' },
  { type: 'top_products', label: 'Top Produkte' },
  { type: 'customer_segment', label: 'Kundensegmente' },
];

export function DashboardBuilder() {
  const [widgets, setWidgets] = useState<Widget[]>([]);
  const [isAddingWidget, setIsAddingWidget] = useState(false);

  const addWidget = (type: string) => {
    const newWidget: Widget = {
      id: `widget-${Date.now()}`,
      type,
      title: WIDGET_TYPES.find((w) => w.type === type)?.label || 'Widget',
      config: {},
      x: 0,
      y: Infinity, // Add to bottom
      w: 6,
      h: 4,
    };
    setWidgets([...widgets, newWidget]);
    setIsAddingWidget(false);
  };

  const removeWidget = (id: string) => {
    setWidgets(widgets.filter((w) => w.id !== id));
  };

  const onLayoutChange = (layout: any[]) => {
    setWidgets((prev) =>
      prev.map((widget) => {
        const layoutItem = layout.find((l) => l.i === widget.id);
        return layoutItem
          ? { ...widget, x: layoutItem.x, y: layoutItem.y, w: layoutItem.w, h: layoutItem.h }
          : widget;
      })
    );
  };

  const saveDashboard = async () => {
    await fetch('/api/v1/analytics/dashboards', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        dashboard_name: 'Custom Dashboard',
        widgets,
      }),
    });
  };

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Dashboard Editor</h1>
        <div className="flex gap-2">
          <Button onClick={() => setIsAddingWidget(true)} variant="outline">
            <Plus className="mr-2 h-4 w-4" />
            Widget hinzufügen
          </Button>
          <Button onClick={saveDashboard}>Dashboard speichern</Button>
        </div>
      </div>

      {isAddingWidget && (
        <Card className="p-4">
          <h3 className="font-semibold mb-3">Widget auswählen</h3>
          <div className="grid grid-cols-4 gap-2">
            {WIDGET_TYPES.map((widget) => (
              <Button
                key={widget.type}
                variant="outline"
                onClick={() => addWidget(widget.type)}
              >
                {widget.label}
              </Button>
            ))}
          </div>
        </Card>
      )}

      <GridLayout
        className="layout"
        cols={12}
        rowHeight={30}
        width={1200}
        onLayoutChange={onLayoutChange}
      >
        {widgets.map((widget) => (
          <div key={widget.id} data-grid={{ x: widget.x, y: widget.y, w: widget.w, h: widget.h }}>
            <Card className="h-full p-4 relative">
              <div className="flex justify-between items-start mb-2">
                <h3 className="font-semibold">{widget.title}</h3>
                <div className="flex gap-1">
                  <Button size="sm" variant="ghost">
                    <Settings className="h-4 w-4" />
                  </Button>
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => removeWidget(widget.id)}
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              </div>

              <div className="h-[calc(100%-40px)]">
                <WidgetContent type={widget.type} config={widget.config} />
              </div>
            </Card>
          </div>
        ))}
      </GridLayout>
    </div>
  );
}

function WidgetContent({ type, config }: { type: string; config: any }) {
  // Render different widget types
  switch (type) {
    case 'sales_chart':
      return <div>Sales Chart Widget</div>;
    case 'revenue_kpi':
      return <div className="text-3xl font-bold">12,345 €</div>;
    default:
      return <div>Widget: {type}</div>;
  }
}
```

### 4. Revenue Forecast View (Umsatzprognose)

#### ForecastView
```tsx
// src/pages/plugins/analytics/ForecastView.tsx
import { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Select } from '@/components/ui/select';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts';
import { TrendingUp, AlertCircle } from 'lucide-react';

interface ForecastData {
  forecast_date: string;
  forecasted_revenue: number;
  confidence_level: number;
  actual_revenue?: number;
}

export function ForecastView() {
  const [forecastData, setForecastData] = useState<ForecastData[]>([]);
  const [forecastType, setForecastType] = useState('monthly');
  const [periods, setPeriods] = useState(12);

  useEffect(() => {
    fetchForecast();
  }, [forecastType, periods]);

  const fetchForecast = async () => {
    const response = await fetch('/api/v1/analytics/forecast', {
      params: { forecast_type: forecastType },
    });
    const data = await response.json();
    setForecastData(data.forecasts);
  };

  const generateNewForecast = async () => {
    await fetch('/api/v1/analytics/forecast/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ forecast_type: forecastType, periods }),
    });
    fetchForecast();
  };

  const chartData = forecastData.map((item) => ({
    date: new Date(item.forecast_date).toLocaleDateString('de-DE', {
      month: 'short',
      year: 'numeric',
    }),
    Prognose: item.forecasted_revenue,
    Tatsächlich: item.actual_revenue || null,
    Konfidenz: item.confidence_level * 100,
  }));

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Umsatzprognose</h1>

        <div className="flex gap-2">
          <Select value={forecastType} onChange={(e) => setForecastType(e.target.value)}>
            <option value="daily">Täglich</option>
            <option value="weekly">Wöchentlich</option>
            <option value="monthly">Monatlich</option>
            <option value="quarterly">Quartalsweise</option>
          </Select>

          <Button onClick={generateNewForecast}>
            <TrendingUp className="mr-2 h-4 w-4" />
            Neue Prognose generieren
          </Button>
        </div>
      </div>

      {/* Info Card */}
      <Card className="p-4 bg-blue-50 border-blue-200">
        <div className="flex items-start gap-3">
          <AlertCircle className="h-5 w-5 text-blue-600 mt-0.5" />
          <div>
            <p className="font-medium text-blue-900">Über die Prognose</p>
            <p className="text-sm text-blue-700">
              Diese Prognose basiert auf historischen Daten und maschinellem Lernen. Die
              Konfidenzlevel zeigen die Zuverlässigkeit der Vorhersage an.
            </p>
          </div>
        </div>
      </Card>

      {/* Forecast Chart */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold mb-4">Prognostizierter Umsatz</h3>
        <ResponsiveContainer width="100%" height={400}>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis yAxisId="left" />
            <YAxis yAxisId="right" orientation="right" />
            <Tooltip />
            <Legend />
            <Line
              yAxisId="left"
              type="monotone"
              dataKey="Prognose"
              stroke="#8884d8"
              strokeWidth={2}
              strokeDasharray="5 5"
              name="Prognostizierter Umsatz (€)"
            />
            <Line
              yAxisId="left"
              type="monotone"
              dataKey="Tatsächlich"
              stroke="#82ca9d"
              strokeWidth={2}
              name="Tatsächlicher Umsatz (€)"
            />
            <Line
              yAxisId="right"
              type="monotone"
              dataKey="Konfidenz"
              stroke="#ffc658"
              strokeWidth={1}
              name="Konfidenzlevel (%)"
            />
            <ReferenceLine yAxisId="left" y={0} stroke="#000" />
          </LineChart>
        </ResponsiveContainer>
      </Card>

      {/* Forecast Table */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold mb-4">Detaillierte Prognose</h3>
        <table className="w-full">
          <thead className="border-b">
            <tr className="text-left">
              <th className="pb-3">Datum</th>
              <th className="pb-3">Prognose</th>
              <th className="pb-3">Tatsächlich</th>
              <th className="pb-3">Abweichung</th>
              <th className="pb-3">Konfidenz</th>
            </tr>
          </thead>
          <tbody>
            {forecastData.map((item, index) => {
              const variance = item.actual_revenue
                ? ((item.actual_revenue - item.forecasted_revenue) /
                    item.forecasted_revenue) *
                  100
                : null;

              return (
                <tr key={index} className="border-b">
                  <td className="py-3">
                    {new Date(item.forecast_date).toLocaleDateString('de-DE')}
                  </td>
                  <td className="py-3">{item.forecasted_revenue.toFixed(2)} €</td>
                  <td className="py-3">
                    {item.actual_revenue ? `${item.actual_revenue.toFixed(2)} €` : '-'}
                  </td>
                  <td className="py-3">
                    {variance !== null ? (
                      <span
                        className={variance >= 0 ? 'text-green-600' : 'text-red-600'}
                      >
                        {variance >= 0 ? '+' : ''}
                        {variance.toFixed(1)}%
                      </span>
                    ) : (
                      '-'
                    )}
                  </td>
                  <td className="py-3">{(item.confidence_level * 100).toFixed(0)}%</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </Card>
    </div>
  );
}
```

### 5. Data Export Tool (Datenexport)

#### DataExportTool
```tsx
// src/pages/plugins/analytics/DataExportTool.tsx
import { useState } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Select } from '@/components/ui/select';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Progress } from '@/components/ui/progress';
import { Download, FileText, FileSpreadsheet, FileJson } from 'lucide-react';

export function DataExportTool() {
  const [exportConfig, setExportConfig] = useState({
    export_type: 'raw_data',
    data_source: 'sales',
    export_format: 'xlsx',
    date_from: '',
    date_to: '',
  });

  const [exportStatus, setExportStatus] = useState<{
    status: string;
    progress: number;
    file_url?: string;
  } | null>(null);

  const startExport = async () => {
    const response = await fetch('/api/v1/analytics/export', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(exportConfig),
    });

    const data = await response.json();
    const exportId = data.export_id;

    // Poll for export status
    const pollInterval = setInterval(async () => {
      const statusResponse = await fetch(`/api/v1/analytics/export/${exportId}/status`);
      const statusData = await statusResponse.json();

      setExportStatus(statusData);

      if (statusData.status === 'completed' || statusData.status === 'failed') {
        clearInterval(pollInterval);
      }
    }, 1000);
  };

  const downloadFile = () => {
    if (exportStatus?.file_url) {
      window.open(exportStatus.file_url, '_blank');
    }
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <h1 className="text-2xl font-bold">Datenexport</h1>

      <Card className="p-6">
        <div className="space-y-4">
          <div>
            <Label>Exporttyp</Label>
            <Select
              value={exportConfig.export_type}
              onChange={(e) =>
                setExportConfig({ ...exportConfig, export_type: e.target.value })
              }
            >
              <option value="raw_data">Rohdaten</option>
              <option value="report">Bericht</option>
              <option value="dashboard">Dashboard</option>
            </Select>
          </div>

          <div>
            <Label>Datenquelle</Label>
            <Select
              value={exportConfig.data_source}
              onChange={(e) =>
                setExportConfig({ ...exportConfig, data_source: e.target.value })
              }
            >
              <option value="sales">Verkäufe</option>
              <option value="products">Produkte</option>
              <option value="customers">Kunden</option>
              <option value="inventory">Bestand</option>
            </Select>
          </div>

          <div>
            <Label>Export-Format</Label>
            <div className="grid grid-cols-4 gap-2">
              {[
                { value: 'xlsx', icon: FileSpreadsheet, label: 'Excel' },
                { value: 'csv', icon: FileText, label: 'CSV' },
                { value: 'pdf', icon: FileText, label: 'PDF' },
                { value: 'json', icon: FileJson, label: 'JSON' },
              ].map((format) => (
                <Button
                  key={format.value}
                  variant={
                    exportConfig.export_format === format.value ? 'default' : 'outline'
                  }
                  onClick={() =>
                    setExportConfig({ ...exportConfig, export_format: format.value })
                  }
                  className="flex flex-col h-20"
                >
                  <format.icon className="h-6 w-6 mb-1" />
                  <span className="text-xs">{format.label}</span>
                </Button>
              ))}
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label>Von</Label>
              <Input
                type="date"
                value={exportConfig.date_from}
                onChange={(e) =>
                  setExportConfig({ ...exportConfig, date_from: e.target.value })
                }
              />
            </div>
            <div>
              <Label>Bis</Label>
              <Input
                type="date"
                value={exportConfig.date_to}
                onChange={(e) =>
                  setExportConfig({ ...exportConfig, date_to: e.target.value })
                }
              />
            </div>
          </div>

          <Button onClick={startExport} className="w-full">
            <Download className="mr-2 h-4 w-4" />
            Export starten
          </Button>
        </div>
      </Card>

      {exportStatus && (
        <Card className="p-6">
          <h3 className="font-semibold mb-4">Export-Status</h3>

          {exportStatus.status === 'pending' || exportStatus.status === 'processing' ? (
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>Export wird verarbeitet...</span>
                <span>{exportStatus.progress}%</span>
              </div>
              <Progress value={exportStatus.progress} />
            </div>
          ) : exportStatus.status === 'completed' ? (
            <div className="space-y-4">
              <div className="flex items-center gap-2 text-green-600">
                <Download className="h-5 w-5" />
                <span className="font-medium">Export abgeschlossen!</span>
              </div>
              <Button onClick={downloadFile} className="w-full">
                <Download className="mr-2 h-4 w-4" />
                Datei herunterladen
              </Button>
            </div>
          ) : (
            <div className="text-red-600">Export fehlgeschlagen</div>
          )}
        </Card>
      )}
    </div>
  );
}
```

## Routing-Konfiguration

```tsx
// src/routes/analyticsRoutes.tsx
import { Route } from 'react-router-dom';
import { AnalyticsDashboard } from '@/pages/plugins/analytics/AnalyticsDashboard';
import { ReportBuilder } from '@/pages/plugins/analytics/ReportBuilder';
import { DashboardBuilder } from '@/pages/plugins/analytics/DashboardBuilder';
import { ForecastView } from '@/pages/plugins/analytics/ForecastView';
import { DataExportTool } from '@/pages/plugins/analytics/DataExportTool';

export const analyticsRoutes = (
  <Route path="/analytics">
    <Route index element={<AnalyticsDashboard />} />
    <Route path="reports/builder" element={<ReportBuilder />} />
    <Route path="dashboards/builder" element={<DashboardBuilder />} />
    <Route path="forecast" element={<ForecastView />} />
    <Route path="export" element={<DataExportTool />} />
  </Route>
);
```

## State Management

```tsx
// src/stores/analyticsStore.ts
import { create } from 'zustand';

interface AnalyticsStore {
  dateRange: string;
  selectedMetrics: string[];
  dashboards: any[];

  setDateRange: (range: string) => void;
  setSelectedMetrics: (metrics: string[]) => void;
  setDashboards: (dashboards: any[]) => void;
}

export const useAnalyticsStore = create<AnalyticsStore>((set) => ({
  dateRange: '7d',
  selectedMetrics: [],
  dashboards: [],

  setDateRange: (dateRange) => set({ dateRange }),
  setSelectedMetrics: (selectedMetrics) => set({ selectedMetrics }),
  setDashboards: (dashboards) => set({ dashboards }),
}));
```

## Deployment Checklist

- [ ] Recharts installiert und konfiguriert
- [ ] React Grid Layout für Dashboard-Editor
- [ ] PDF/Excel Export-Bibliotheken
- [ ] Chart-Komponenten getestet
- [ ] Report-Builder funktional
- [ ] Dashboard-Editor funktional
- [ ] Forecast-Visualisierung implementiert
- [ ] Datenexport getestet
- [ ] Responsive Design
- [ ] Performance-Optimierung für große Datensätze
