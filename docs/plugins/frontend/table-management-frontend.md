# Table Management Plugin - Frontend Integration

## Übersicht

Das Table Management Plugin ermöglicht die Verwaltung von Tischen, Reservierungen und Sitzplänen für Restaurants. Es bietet Echtzeit-Status-Updates, Drag-and-Drop-Funktionalität und visuelle Raumplanung.

## Erforderliche Dependencies

```json
{
  "dependencies": {
    "react-dnd": "^16.0.1",
    "react-dnd-html5-backend": "^16.0.1",
    "@dnd-kit/core": "^6.1.0",
    "@dnd-kit/sortable": "^8.0.0",
    "react-konva": "^18.2.10",
    "konva": "^9.2.3"
  }
}
```

## Erforderliche UI-Komponenten

### 1. Floor Plan View (Raumplan-Ansicht)

#### FloorPlanView
```tsx
// src/pages/plugins/table-management/FloorPlanView.tsx
import { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Stage, Layer, Rect, Circle, Text, Group } from 'react-konva';
import { Plus, Edit, Trash2, Save } from 'lucide-react';

interface Table {
  id: number;
  table_number: string;
  capacity: number;
  shape: 'square' | 'circle' | 'rectangle';
  x_position: number;
  y_position: number;
  width: number;
  height: number;
  status: 'available' | 'occupied' | 'reserved' | 'dirty';
  floor_id: number;
}

interface Floor {
  id: number;
  floor_name: string;
  floor_number: number;
  width: number;
  height: number;
}

export function FloorPlanView() {
  const [floors, setFloors] = useState<Floor[]>([]);
  const [selectedFloor, setSelectedFloor] = useState<number | null>(null);
  const [tables, setTables] = useState<Table[]>([]);
  const [selectedTable, setSelectedTable] = useState<number | null>(null);
  const [editMode, setEditMode] = useState(false);

  useEffect(() => {
    fetchFloors();
  }, []);

  useEffect(() => {
    if (selectedFloor) {
      fetchTables(selectedFloor);
      // Poll for updates every 5 seconds
      const interval = setInterval(() => fetchTables(selectedFloor), 5000);
      return () => clearInterval(interval);
    }
  }, [selectedFloor]);

  const fetchFloors = async () => {
    const response = await fetch('/api/v1/table-management/floors');
    const data = await response.json();
    setFloors(data.floors);
    if (data.floors.length > 0) {
      setSelectedFloor(data.floors[0].id);
    }
  };

  const fetchTables = async (floorId: number) => {
    const response = await fetch(`/api/v1/table-management/tables?floor_id=${floorId}`);
    const data = await response.json();
    setTables(data.tables);
  };

  const handleTableDrag = (tableId: number, x: number, y: number) => {
    setTables((prev) =>
      prev.map((table) =>
        table.id === tableId ? { ...table, x_position: x, y_position: y } : table
      )
    );
  };

  const saveTables = async () => {
    await Promise.all(
      tables.map((table) =>
        fetch(`/api/v1/table-management/tables/${table.id}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            x_position: table.x_position,
            y_position: table.y_position,
          }),
        })
      )
    );
    setEditMode(false);
  };

  const getTableColor = (status: string) => {
    switch (status) {
      case 'available':
        return '#22c55e'; // green
      case 'occupied':
        return '#ef4444'; // red
      case 'reserved':
        return '#eab308'; // yellow
      case 'dirty':
        return '#6b7280'; // gray
      default:
        return '#3b82f6'; // blue
    }
  };

  const currentFloor = floors.find((f) => f.id === selectedFloor);

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Tischverwaltung</h1>

        <div className="flex gap-2">
          <Button
            variant={editMode ? 'default' : 'outline'}
            onClick={() => (editMode ? saveTables() : setEditMode(true))}
          >
            {editMode ? (
              <>
                <Save className="mr-2 h-4 w-4" />
                Speichern
              </>
            ) : (
              <>
                <Edit className="mr-2 h-4 w-4" />
                Bearbeiten
              </>
            )}
          </Button>
          <Button>
            <Plus className="mr-2 h-4 w-4" />
            Neuer Tisch
          </Button>
        </div>
      </div>

      {/* Floor Selector */}
      <div className="flex gap-2">
        {floors.map((floor) => (
          <Button
            key={floor.id}
            variant={selectedFloor === floor.id ? 'default' : 'outline'}
            onClick={() => setSelectedFloor(floor.id)}
          >
            {floor.floor_name}
          </Button>
        ))}
      </div>

      {/* Status Legend */}
      <Card className="p-4">
        <div className="flex gap-6">
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded bg-green-500" />
            <span className="text-sm">Verfügbar</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded bg-red-500" />
            <span className="text-sm">Besetzt</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded bg-yellow-500" />
            <span className="text-sm">Reserviert</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded bg-gray-500" />
            <span className="text-sm">Zu reinigen</span>
          </div>
        </div>
      </Card>

      {/* Floor Plan Canvas */}
      <Card className="p-6">
        {currentFloor && (
          <Stage width={currentFloor.width} height={currentFloor.height}>
            <Layer>
              {/* Background */}
              <Rect
                x={0}
                y={0}
                width={currentFloor.width}
                height={currentFloor.height}
                fill="#f8f9fa"
                stroke="#dee2e6"
                strokeWidth={2}
              />

              {/* Tables */}
              {tables.map((table) => (
                <Group
                  key={table.id}
                  x={table.x_position}
                  y={table.y_position}
                  draggable={editMode}
                  onDragEnd={(e) => {
                    const node = e.target;
                    handleTableDrag(table.id, node.x(), node.y());
                  }}
                  onClick={() => !editMode && setSelectedTable(table.id)}
                >
                  {table.shape === 'circle' ? (
                    <Circle
                      radius={table.width / 2}
                      fill={getTableColor(table.status)}
                      stroke="#000"
                      strokeWidth={2}
                    />
                  ) : (
                    <Rect
                      width={table.width}
                      height={table.height}
                      fill={getTableColor(table.status)}
                      stroke="#000"
                      strokeWidth={2}
                      cornerRadius={5}
                    />
                  )}
                  <Text
                    text={table.table_number}
                    fontSize={16}
                    fontStyle="bold"
                    fill="#fff"
                    align="center"
                    verticalAlign="middle"
                    width={table.width}
                    height={table.height}
                    offsetX={table.shape === 'circle' ? table.width / 2 : 0}
                    offsetY={table.shape === 'circle' ? 8 : 0}
                  />
                  <Text
                    text={`${table.capacity} Pers.`}
                    fontSize={12}
                    fill="#fff"
                    align="center"
                    width={table.width}
                    y={table.height / 2 + 10}
                    offsetX={table.shape === 'circle' ? table.width / 2 : 0}
                  />
                </Group>
              ))}
            </Layer>
          </Stage>
        )}
      </Card>

      {/* Table Details Sidebar */}
      {selectedTable && (
        <TableDetailsSidebar
          tableId={selectedTable}
          onClose={() => setSelectedTable(null)}
        />
      )}
    </div>
  );
}
```

### 2. Reservation Management (Reservierungsverwaltung)

#### ReservationList
```tsx
// src/pages/plugins/table-management/ReservationList.tsx
import { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Calendar as CalendarIcon, Clock, Users, Phone, Plus } from 'lucide-react';
import { format } from 'date-fns';
import { de } from 'date-fns/locale';

interface Reservation {
  id: number;
  customer_name: string;
  customer_phone: string;
  customer_email: string;
  party_size: number;
  reservation_date: string;
  reservation_time: string;
  duration_minutes: number;
  status: string;
  special_requests: string;
  table_id: number | null;
  table_number: string | null;
}

export function ReservationList() {
  const [reservations, setReservations] = useState<Reservation[]>([]);
  const [selectedDate, setSelectedDate] = useState<Date>(new Date());
  const [filterStatus, setFilterStatus] = useState('all');

  useEffect(() => {
    fetchReservations();
  }, [selectedDate, filterStatus]);

  const fetchReservations = async () => {
    const dateStr = format(selectedDate, 'yyyy-MM-dd');
    const params = new URLSearchParams({ date: dateStr });
    if (filterStatus !== 'all') params.append('status', filterStatus);

    const response = await fetch(`/api/v1/table-management/reservations?${params}`);
    const data = await response.json();
    setReservations(data.reservations);
  };

  const updateReservationStatus = async (id: number, status: string) => {
    await fetch(`/api/v1/table-management/reservations/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status }),
    });
    fetchReservations();
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'confirmed':
        return 'success';
      case 'pending':
        return 'warning';
      case 'cancelled':
        return 'destructive';
      case 'completed':
        return 'secondary';
      case 'no_show':
        return 'destructive';
      default:
        return 'default';
    }
  };

  const getStatusLabel = (status: string) => {
    const labels: Record<string, string> = {
      pending: 'Ausstehend',
      confirmed: 'Bestätigt',
      cancelled: 'Storniert',
      completed: 'Abgeschlossen',
      no_show: 'Nicht erschienen',
    };
    return labels[status] || status;
  };

  // Group reservations by time
  const groupedReservations = reservations.reduce((acc, res) => {
    const time = res.reservation_time;
    if (!acc[time]) acc[time] = [];
    acc[time].push(res);
    return acc;
  }, {} as Record<string, Reservation[]>);

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Reservierungen</h1>
        <Button>
          <Plus className="mr-2 h-4 w-4" />
          Neue Reservierung
        </Button>
      </div>

      {/* Date Selector and Filters */}
      <Card className="p-4">
        <div className="flex gap-4">
          <div className="flex-1">
            <Input
              type="date"
              value={format(selectedDate, 'yyyy-MM-dd')}
              onChange={(e) => setSelectedDate(new Date(e.target.value))}
            />
          </div>

          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
            className="border rounded px-3 py-2"
          >
            <option value="all">Alle Status</option>
            <option value="pending">Ausstehend</option>
            <option value="confirmed">Bestätigt</option>
            <option value="completed">Abgeschlossen</option>
            <option value="cancelled">Storniert</option>
          </select>
        </div>
      </Card>

      {/* Stats */}
      <div className="grid grid-cols-4 gap-4">
        <Card className="p-4">
          <p className="text-sm text-muted-foreground">Gesamt</p>
          <p className="text-2xl font-bold">{reservations.length}</p>
        </Card>
        <Card className="p-4">
          <p className="text-sm text-muted-foreground">Bestätigt</p>
          <p className="text-2xl font-bold text-green-600">
            {reservations.filter((r) => r.status === 'confirmed').length}
          </p>
        </Card>
        <Card className="p-4">
          <p className="text-sm text-muted-foreground">Ausstehend</p>
          <p className="text-2xl font-bold text-yellow-600">
            {reservations.filter((r) => r.status === 'pending').length}
          </p>
        </Card>
        <Card className="p-4">
          <p className="text-sm text-muted-foreground">Gäste heute</p>
          <p className="text-2xl font-bold">
            {reservations.reduce((sum, r) => sum + r.party_size, 0)}
          </p>
        </Card>
      </div>

      {/* Reservations Timeline */}
      <div className="space-y-4">
        {Object.entries(groupedReservations)
          .sort(([a], [b]) => a.localeCompare(b))
          .map(([time, timeReservations]) => (
            <Card key={time} className="p-4">
              <h3 className="font-semibold text-lg mb-4 flex items-center gap-2">
                <Clock className="h-5 w-5" />
                {time} Uhr
              </h3>

              <div className="space-y-3">
                {timeReservations.map((reservation) => (
                  <div
                    key={reservation.id}
                    className="border rounded-lg p-4 hover:bg-gray-50 transition-colors"
                  >
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <h4 className="font-semibold">{reservation.customer_name}</h4>
                          <Badge variant={getStatusColor(reservation.status)}>
                            {getStatusLabel(reservation.status)}
                          </Badge>
                          {reservation.table_number && (
                            <Badge variant="outline">Tisch {reservation.table_number}</Badge>
                          )}
                        </div>

                        <div className="grid grid-cols-3 gap-4 text-sm text-muted-foreground">
                          <div className="flex items-center gap-2">
                            <Users className="h-4 w-4" />
                            <span>{reservation.party_size} Personen</span>
                          </div>
                          <div className="flex items-center gap-2">
                            <Phone className="h-4 w-4" />
                            <span>{reservation.customer_phone}</span>
                          </div>
                          <div className="flex items-center gap-2">
                            <Clock className="h-4 w-4" />
                            <span>{reservation.duration_minutes} Min.</span>
                          </div>
                        </div>

                        {reservation.special_requests && (
                          <p className="text-sm mt-2 text-muted-foreground">
                            <strong>Notizen:</strong> {reservation.special_requests}
                          </p>
                        )}
                      </div>

                      <div className="flex gap-2">
                        {reservation.status === 'pending' && (
                          <Button
                            size="sm"
                            onClick={() =>
                              updateReservationStatus(reservation.id, 'confirmed')
                            }
                          >
                            Bestätigen
                          </Button>
                        )}
                        {reservation.status === 'confirmed' && (
                          <>
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() =>
                                updateReservationStatus(reservation.id, 'completed')
                              }
                            >
                              Abschließen
                            </Button>
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() =>
                                updateReservationStatus(reservation.id, 'no_show')
                              }
                            >
                              No-Show
                            </Button>
                          </>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </Card>
          ))}
      </div>
    </div>
  );
}
```

### 3. Reservation Form (Reservierungsformular)

#### ReservationForm
```tsx
// src/pages/plugins/table-management/ReservationForm.tsx
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import { Form, FormField, FormItem, FormLabel, FormControl } from '@/components/ui/form';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Button } from '@/components/ui/button';
import { Select } from '@/components/ui/select';

const reservationSchema = z.object({
  customer_name: z.string().min(1, 'Name erforderlich'),
  customer_phone: z.string().min(1, 'Telefonnummer erforderlich'),
  customer_email: z.string().email('Ungültige E-Mail').optional().or(z.literal('')),
  party_size: z.number().min(1).max(20),
  reservation_date: z.string().min(1),
  reservation_time: z.string().min(1),
  duration_minutes: z.number().default(120),
  special_requests: z.string().optional(),
  preferred_table_id: z.number().optional(),
});

type ReservationFormData = z.infer<typeof reservationSchema>;

export function ReservationForm({ onSuccess }: { onSuccess: () => void }) {
  const form = useForm<ReservationFormData>({
    resolver: zodResolver(reservationSchema),
    defaultValues: {
      party_size: 2,
      duration_minutes: 120,
    },
  });

  const onSubmit = async (data: ReservationFormData) => {
    try {
      const response = await fetch('/api/v1/table-management/reservations', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });

      if (response.ok) {
        onSuccess();
      }
    } catch (error) {
      console.error('Failed to create reservation:', error);
    }
  };

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
        <div className="grid grid-cols-2 gap-4">
          <FormField
            control={form.control}
            name="customer_name"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Name</FormLabel>
                <FormControl>
                  <Input {...field} placeholder="Max Mustermann" />
                </FormControl>
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="customer_phone"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Telefon</FormLabel>
                <FormControl>
                  <Input {...field} placeholder="+49 123 456789" />
                </FormControl>
              </FormItem>
            )}
          />
        </div>

        <FormField
          control={form.control}
          name="customer_email"
          render={({ field }) => (
            <FormItem>
              <FormLabel>E-Mail (optional)</FormLabel>
              <FormControl>
                <Input type="email" {...field} placeholder="max@example.com" />
              </FormControl>
            </FormItem>
          )}
        />

        <div className="grid grid-cols-3 gap-4">
          <FormField
            control={form.control}
            name="party_size"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Anzahl Gäste</FormLabel>
                <FormControl>
                  <Input
                    type="number"
                    {...field}
                    onChange={(e) => field.onChange(parseInt(e.target.value))}
                  />
                </FormControl>
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="reservation_date"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Datum</FormLabel>
                <FormControl>
                  <Input type="date" {...field} />
                </FormControl>
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="reservation_time"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Uhrzeit</FormLabel>
                <FormControl>
                  <Input type="time" {...field} />
                </FormControl>
              </FormItem>
            )}
          />
        </div>

        <FormField
          control={form.control}
          name="duration_minutes"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Dauer (Minuten)</FormLabel>
              <FormControl>
                <Select
                  {...field}
                  onChange={(e) => field.onChange(parseInt(e.target.value))}
                >
                  <option value="60">60 Min</option>
                  <option value="90">90 Min</option>
                  <option value="120">120 Min</option>
                  <option value="180">180 Min</option>
                </Select>
              </FormControl>
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="special_requests"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Besondere Wünsche</FormLabel>
              <FormControl>
                <Textarea {...field} rows={3} placeholder="z.B. Kinderstuhl, Allergie..." />
              </FormControl>
            </FormItem>
          )}
        />

        <div className="flex justify-end gap-2">
          <Button type="button" variant="outline">
            Abbrechen
          </Button>
          <Button type="submit">Reservierung speichern</Button>
        </div>
      </form>
    </Form>
  );
}
```

### 4. Table Assignment (Tischzuweisung)

#### TableAssignment
```tsx
// src/pages/plugins/table-management/TableAssignment.tsx
import { useState } from 'react';
import { DndContext, DragEndEvent } from '@dnd-kit/core';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

export function TableAssignment() {
  const [reservations, setReservations] = useState([]);
  const [tables, setTables] = useState([]);

  const handleDragEnd = async (event: DragEndEvent) => {
    const { active, over } = event;

    if (over) {
      const reservationId = active.id;
      const tableId = over.id;

      await fetch(`/api/v1/table-management/reservations/${reservationId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ table_id: tableId }),
      });

      // Refresh data
    }
  };

  return (
    <DndContext onDragEnd={handleDragEnd}>
      <div className="grid grid-cols-2 gap-6">
        {/* Unassigned Reservations */}
        <Card className="p-4">
          <h3 className="font-semibold mb-4">Nicht zugewiesen</h3>
          {/* Draggable reservation cards */}
        </Card>

        {/* Available Tables */}
        <Card className="p-4">
          <h3 className="font-semibold mb-4">Verfügbare Tische</h3>
          {/* Droppable table cards */}
        </Card>
      </div>
    </DndContext>
  );
}
```

## Routing-Konfiguration

```tsx
// src/routes/tableManagementRoutes.tsx
import { Route } from 'react-router-dom';
import { FloorPlanView } from '@/pages/plugins/table-management/FloorPlanView';
import { ReservationList } from '@/pages/plugins/table-management/ReservationList';
import { TableAssignment } from '@/pages/plugins/table-management/TableAssignment';

export const tableManagementRoutes = (
  <Route path="/tables">
    <Route index element={<FloorPlanView />} />
    <Route path="reservations" element={<ReservationList />} />
    <Route path="assignment" element={<TableAssignment />} />
  </Route>
);
```

## State Management

```tsx
// src/stores/tableManagementStore.ts
import { create } from 'zustand';

interface TableManagementStore {
  selectedFloor: number | null;
  tables: any[];
  reservations: any[];

  setSelectedFloor: (id: number) => void;
  setTables: (tables: any[]) => void;
  setReservations: (reservations: any[]) => void;
}

export const useTableManagementStore = create<TableManagementStore>((set) => ({
  selectedFloor: null,
  tables: [],
  reservations: [],

  setSelectedFloor: (selectedFloor) => set({ selectedFloor }),
  setTables: (tables) => set({ tables }),
  setReservations: (reservations) => set({ reservations }),
}));
```

## API Hooks

```tsx
// src/hooks/useTableManagement.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '@/services/api';

export function useTables(floorId: number) {
  return useQuery({
    queryKey: ['tables', floorId],
    queryFn: async () => {
      const { data } = await api.get(`/table-management/tables?floor_id=${floorId}`);
      return data.tables;
    },
    refetchInterval: 5000, // Poll every 5 seconds
  });
}

export function useReservations(date: string) {
  return useQuery({
    queryKey: ['reservations', date],
    queryFn: async () => {
      const { data } = await api.get(`/table-management/reservations?date=${date}`);
      return data.reservations;
    },
  });
}

export function useCreateReservation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (reservationData: any) => {
      const { data } = await api.post('/table-management/reservations', reservationData);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['reservations'] });
    },
  });
}
```

## Deployment Checklist

- [ ] React DnD oder DnD Kit installiert
- [ ] Konva für Canvas-Rendering
- [ ] Echtzeit-Polling für Tischstatus
- [ ] Drag-and-Drop-Funktionalität getestet
- [ ] Reservierungsformular validiert
- [ ] Mobile-responsive Raumplan
- [ ] Print-Funktion für Reservierungsliste
- [ ] Konfliktprüfung bei Reservierungen
