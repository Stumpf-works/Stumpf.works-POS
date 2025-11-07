# Employee Time Tracking Plugin - Frontend Integration

## Übersicht

Arbeitszeiterfassung mit Stempeluhr, Pausenverwaltung, Schichtplanung und Überstundenberechnung.

## Key Components

### 1. Time Clock Interface
```tsx
// Clock In/Out Terminal
- Large clock in/out buttons
- PIN or badge scan
- Current shift display
- Break management
```

### 2. Time Sheet View
```tsx
// Employee time records
- Calendar view of work hours
- Daily/weekly/monthly summaries
- Edit time entries
- Export to payroll
```

### 3. Shift Planner
```tsx
// Shift scheduling
- Drag-and-drop schedule builder
- Employee availability
- Conflict detection
- Template creation
```

### 4. Overtime Dashboard
```tsx
// Overtime tracking
- Automatic calculation
- Approval workflow
- Report generation
```

## Main Views

```tsx
// Clock Terminal (for employees)
export function ClockTerminal() {
  return (
    <Card className="max-w-md mx-auto p-8">
      <CurrentTime />
      <EmployeePinInput />
      <ClockInOutButton />
      <CurrentShiftInfo />
      <BreakButtons />
    </Card>
  );
}

// Admin Time Sheet View
export function TimeSheetView() {
  return (
    <div>
      <EmployeeSelector />
      <DateRangePicker />
      <TimeEntriesTable />
      <OvertimeSummary />
      <ExportButton />
    </div>
  );
}

// Shift Planner
export function ShiftPlanner() {
  return (
    <div>
      <WeekSelector />
      <EmployeeList />
      <ShiftGrid />
      <SaveButton />
    </div>
  );
}
```

## API Hooks

```tsx
export function useClockIn() {
  return useMutation({
    mutationFn: (employeePin) =>
      api.post('/time-tracking/clock-in', { employee_pin: employeePin }),
  });
}

export function useTimeEntries(employeeId, dateRange) {
  return useQuery({
    queryKey: ['time-entries', employeeId, dateRange],
    queryFn: () => api.get(`/time-tracking/entries`, { params: { employeeId, ...dateRange }}),
  });
}
```

## Features
- **Simple clock terminal UI**
- **PIN-based authentication**
- **Automatic overtime calculation**
- **Break management**
- **Shift templates**
- **Mobile-friendly**
- **Payroll export**

## Routing
```tsx
/time-tracking
  /clock - Employee clock terminal
  /timesheet - Admin time sheet view
  /shifts - Shift planning
  /overtime - Overtime management
  /reports - Time reports
```

## Important Notes
- Large touch-friendly buttons for terminal
- Auto-logout after clock in/out
- Offline mode support for clock terminal
- Real-time sync when connection restored
