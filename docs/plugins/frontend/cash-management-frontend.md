# Cash Management Plugin - Frontend Integration

## Übersicht

Kassenverwaltung mit Kassenöffnung/-schließung, Bargeldeinlagen, Ausgaben, Zählungen und Z-Bericht-Erstellung (GoBD & KassenSichV konform).

## Key Components

### 1. Cash Register Overview
```tsx
// Active registers and their status
- Register balance
- Open/closed status
- Last transaction
- Assigned employee
```

### 2. Cash Count Interface
```tsx
// Denomination counting tool
- Input fields for each denomination
- Automatic total calculation
- Expected vs. actual comparison
- Variance reporting
```

### 3. Cash Transaction Form
```tsx
// Deposits, withdrawals, expenses
- Transaction type selection
- Amount input
- Reason/notes
- Receipt printing
```

### 4. Z-Report Generator
```tsx
// End-of-day report
- Daily sales summary
- Cash vs. card breakdown
- Opening/closing balance
- All transactions listed
- PDF export
- Legal compliance info
```

## Main Views

```tsx
// Cash Register Dashboard
export function CashRegisterDashboard() {
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-3 gap-4">
        {registers.map(register => (
          <RegisterCard key={register.id} register={register} />
        ))}
      </div>

      <RecentTransactionsTable />
      <PendingFloats />
    </div>
  );
}

// Open Register Flow
export function OpenRegisterFlow({ registerId }) {
  const [step, setStep] = useState(1);

  return (
    <Dialog>
      {step === 1 && (
        <CountStartingCash onNext={(amount) => setStep(2)} />
      )}
      {step === 2 && (
        <ConfirmOpening onConfirm={handleOpenRegister} />
      )}
    </Dialog>
  );
}

// Cash Count Component
export function CashCountForm({ registerId, expectedAmount }) {
  const [counts, setCounts] = useState({
    '0.01': 0, '0.02': 0, '0.05': 0, '0.10': 0, '0.20': 0, '0.50': 0,
    '1.00': 0, '2.00': 0,
    '5': 0, '10': 0, '20': 0, '50': 0, '100': 0, '200': 0, '500': 0
  });

  const totalCounted = Object.entries(counts).reduce(
    (sum, [denom, count]) => sum + (parseFloat(denom) * count),
    0
  );

  const variance = totalCounted - expectedAmount;

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-bold">Bargeld zählen</h2>

      {/* Coins */}
      <div>
        <h3 className="font-semibold mb-2">Münzen</h3>
        <div className="grid grid-cols-4 gap-3">
          {['0.01', '0.02', '0.05', '0.10', '0.20', '0.50', '1.00', '2.00'].map(denom => (
            <DenominationInput
              key={denom}
              denomination={denom}
              value={counts[denom]}
              onChange={(val) => setCounts({...counts, [denom]: val})}
            />
          ))}
        </div>
      </div>

      {/* Bills */}
      <div>
        <h3 className="font-semibold mb-2">Scheine</h3>
        <div className="grid grid-cols-4 gap-3">
          {['5', '10', '20', '50', '100', '200', '500'].map(denom => (
            <DenominationInput
              key={denom}
              denomination={denom}
              value={counts[denom]}
              onChange={(val) => setCounts({...counts, [denom]: val})}
            />
          ))}
        </div>
      </div>

      {/* Summary */}
      <Card className="p-4 bg-gray-50">
        <div className="space-y-2">
          <div className="flex justify-between text-lg">
            <span>Gezählt:</span>
            <span className="font-bold">{totalCounted.toFixed(2)} €</span>
          </div>
          <div className="flex justify-between text-lg">
            <span>Erwartet:</span>
            <span>{expectedAmount.toFixed(2)} €</span>
          </div>
          <div className={`flex justify-between text-xl font-bold ${
            variance === 0 ? 'text-green-600' :
            Math.abs(variance) < 5 ? 'text-yellow-600' :
            'text-red-600'
          }`}>
            <span>Differenz:</span>
            <span>{variance >= 0 ? '+' : ''}{variance.toFixed(2)} €</span>
          </div>
        </div>
      </Card>

      <Button onClick={handleSubmitCount} className="w-full">
        Zählung speichern
      </Button>
    </div>
  );
}

// Denomination Input Component
function DenominationInput({ denomination, value, onChange }) {
  const displayValue = parseFloat(denomination) < 5 ? `${denomination} €` : `${denomination} €`;

  return (
    <div className="flex flex-col items-center">
      <label className="text-sm font-medium mb-1">{displayValue}</label>
      <Input
        type="number"
        min="0"
        value={value}
        onChange={(e) => onChange(parseInt(e.target.value) || 0)}
        className="w-20 text-center text-lg"
      />
      <span className="text-xs text-muted-foreground mt-1">
        = {(parseFloat(denomination) * value).toFixed(2)} €
      </span>
    </div>
  );
}

// Z-Report Component
export function ZReportGenerator({ registerId, date }) {
  const { data: reportData, isLoading } = useZReport(registerId, date);

  if (isLoading) return <LoadingState />;

  return (
    <div className="max-w-4xl mx-auto">
      <Card className="p-8">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold">Z-Bericht</h1>
          <p className="text-muted-foreground">
            Kasse {reportData.register_name} - {format(new Date(date), 'dd.MM.yyyy')}
          </p>
        </div>

        {/* Opening/Closing */}
        <div className="grid grid-cols-2 gap-6 mb-6">
          <div>
            <h3 className="font-semibold mb-2">Kassenöffnung</h3>
            <p>Zeit: {reportData.opened_at}</p>
            <p>Anfangsbestand: {reportData.opening_balance} €</p>
            <p>Mitarbeiter: {reportData.opened_by}</p>
          </div>
          <div>
            <h3 className="font-semibold mb-2">Kassenschluss</h3>
            <p>Zeit: {reportData.closed_at || '-'}</p>
            <p>Endbestand: {reportData.closing_balance} €</p>
            <p>Mitarbeiter: {reportData.closed_by || '-'}</p>
          </div>
        </div>

        {/* Sales Summary */}
        <div className="mb-6">
          <h3 className="font-semibold mb-3">Umsatzübersicht</h3>
          <table className="w-full">
            <tbody>
              <tr className="border-b">
                <td className="py-2">Barzahlungen</td>
                <td className="text-right font-semibold">{reportData.cash_sales} €</td>
              </tr>
              <tr className="border-b">
                <td className="py-2">Kartenzahlungen</td>
                <td className="text-right">{reportData.card_sales} €</td>
              </tr>
              <tr className="border-b">
                <td className="py-2">Sonstige</td>
                <td className="text-right">{reportData.other_sales} €</td>
              </tr>
              <tr className="font-bold text-lg">
                <td className="py-2">Gesamtumsatz</td>
                <td className="text-right">{reportData.total_sales} €</td>
              </tr>
            </tbody>
          </table>
        </div>

        {/* Cash Movement */}
        <div className="mb-6">
          <h3 className="font-semibold mb-3">Bargeldbewegungen</h3>
          <table className="w-full text-sm">
            <tbody>
              <tr className="border-b">
                <td className="py-2">Einlagen (+)</td>
                <td className="text-right text-green-600">+{reportData.deposits} €</td>
              </tr>
              <tr className="border-b">
                <td className="py-2">Entnahmen (-)</td>
                <td className="text-right text-red-600">-{reportData.withdrawals} €</td>
              </tr>
              <tr className="border-b">
                <td className="py-2">Ausgaben (-)</td>
                <td className="text-right text-red-600">-{reportData.expenses} €</td>
              </tr>
            </tbody>
          </table>
        </div>

        {/* Expected vs Actual */}
        <div className="bg-gray-50 p-4 rounded mb-6">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-sm text-muted-foreground">Soll-Bestand</p>
              <p className="text-2xl font-bold">{reportData.expected_balance} €</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Ist-Bestand</p>
              <p className="text-2xl font-bold">{reportData.actual_balance} €</p>
            </div>
          </div>
          <div className={`mt-2 text-lg font-semibold ${
            reportData.variance === 0 ? 'text-green-600' : 'text-red-600'
          }`}>
            Differenz: {reportData.variance >= 0 ? '+' : ''}{reportData.variance} €
          </div>
        </div>

        {/* Legal Notice */}
        <div className="text-xs text-muted-foreground border-t pt-4">
          <p>Dieser Bericht entspricht den Anforderungen der GoBD und KassenSichV.</p>
          <p>TSE-Signatur: {reportData.tse_signature}</p>
          <p>Erstellt: {new Date().toLocaleString('de-DE')}</p>
        </div>

        {/* Actions */}
        <div className="flex gap-2 mt-6">
          <Button onClick={() => window.print()} variant="outline" className="flex-1">
            Drucken
          </Button>
          <Button onClick={handleExportPDF} variant="outline" className="flex-1">
            PDF Export
          </Button>
          <Button onClick={handleClose} className="flex-1">
            Kasse schließen
          </Button>
        </div>
      </Card>
    </div>
  );
}
```

## API Hooks

```tsx
export function useRegister(registerId) {
  return useQuery({
    queryKey: ['cash', 'register', registerId],
    queryFn: () => api.get(`/cash-management/registers/${registerId}`),
  });
}

export function useOpenRegister() {
  return useMutation({
    mutationFn: (data) => api.post('/cash-management/registers/open', data),
  });
}

export function useCloseRegister() {
  return useMutation({
    mutationFn: ({ registerId, closingBalance }) =>
      api.post(`/cash-management/registers/${registerId}/close`, { closing_balance: closingBalance }),
  });
}

export function useZReport(registerId, date) {
  return useQuery({
    queryKey: ['cash', 'z-report', registerId, date],
    queryFn: () => api.get(`/cash-management/z-report/${registerId}?date=${date}`),
  });
}
```

## Features
- **Register opening/closing workflow**
- **Denomination-based cash counting**
- **Variance tracking**
- **Safe deposits**
- **Expense tracking**
- **Z-Report generation**
- **GoBD/KassenSichV compliant**
- **TSE integration ready**
- **Audit trail**
- **Multi-register support**

## Routing
```tsx
/cash-management
  /registers - Register overview
  /count - Cash counting interface
  /transactions - Transaction history
  /z-reports - Z-Report archive
  /settings - Register configuration
```

## Compliance Notes
⚠️ **German Legal Requirements**:
- **GoBD**: Proper documentation and archiving
- **KassenSichV**: TSE (Technical Security Equipment) required
- **Data retention**: 10 years
- **Audit-proof**: No deletion of records
- **Daily Z-Reports**: Mandatory

## Security
- **Access control**: Only authorized users
- **Four-eyes principle**: Large cash movements
- **Automatic backups**: All transactions
- **Tamper-proof**: Immutable records
