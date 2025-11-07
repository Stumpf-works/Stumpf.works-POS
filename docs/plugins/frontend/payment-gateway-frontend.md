# Payment Gateway Plugin - Frontend Integration

## Übersicht

Das Payment Gateway Plugin benötigt eine sichere und benutzerfreundliche Frontend-Integration für Zahlungsabwicklung, Provider-Management, Terminal-Integration und Transaktionsverwaltung.

## Erforderliche Dependencies

```json
{
  "dependencies": {
    "@stripe/stripe-js": "^2.2.0",
    "@stripe/react-stripe-js": "^2.4.0",
    "react-credit-cards-2": "^1.0.2",
    "qrcode.react": "^3.1.0"
  }
}
```

## Sicherheitshinweise

⚠️ **WICHTIG**:
- Niemals Kreditkartendaten im Frontend speichern
- Verwende immer HTTPS in Produktion
- PCI-DSS Compliance beachten
- Sensible Daten nie in LocalStorage/SessionStorage
- API-Keys und Secrets nur im Backend

## Erforderliche UI-Komponenten

### 1. Payment Provider Management

#### PaymentProviderList
```tsx
// src/pages/plugins/payment/PaymentProviderList.tsx
import { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Switch } from '@/components/ui/switch';
import { Plus, Settings, CreditCard } from 'lucide-react';

interface PaymentProvider {
  id: number;
  provider_name: string;
  provider_type: string;
  is_active: boolean;
  is_test_mode: boolean;
  is_default: boolean;
  health_status: string;
  transaction_fee_percentage: number;
  transaction_fee_fixed: number;
}

export function PaymentProviderList() {
  const [providers, setProviders] = useState<PaymentProvider[]>([]);

  useEffect(() => {
    fetchProviders();
  }, []);

  const fetchProviders = async () => {
    const response = await fetch('/api/v1/payments/providers');
    const data = await response.json();
    setProviders(data.providers);
  };

  const toggleProvider = async (id: number, isActive: boolean) => {
    await fetch(`/api/v1/payments/providers/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ is_active: isActive }),
    });
    fetchProviders();
  };

  const getProviderIcon = (name: string) => {
    const icons: Record<string, string> = {
      stripe: '💳 Stripe',
      paypal: '🅿️ PayPal',
      square: '⬛ Square',
      sumup: '🔷 SumUp',
    };
    return icons[name.toLowerCase()] || name;
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Zahlungsanbieter</h1>
        <Button>
          <Plus className="mr-2 h-4 w-4" />
          Anbieter hinzufügen
        </Button>
      </div>

      <div className="grid grid-cols-2 gap-4">
        {providers.map((provider) => (
          <Card key={provider.id} className="p-6">
            <div className="flex justify-between items-start mb-4">
              <div className="flex items-center gap-3">
                <div className="text-3xl">{getProviderIcon(provider.provider_name)}</div>
                <div>
                  <h3 className="font-semibold text-lg">{provider.provider_name}</h3>
                  <p className="text-sm text-muted-foreground capitalize">
                    {provider.provider_type.replace('_', ' ')}
                  </p>
                </div>
              </div>

              <Badge
                variant={
                  provider.health_status === 'healthy'
                    ? 'success'
                    : provider.health_status === 'degraded'
                    ? 'warning'
                    : 'destructive'
                }
              >
                {provider.health_status}
              </Badge>
            </div>

            <div className="space-y-3 mb-4">
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Gebühren</span>
                <span className="font-medium">
                  {provider.transaction_fee_percentage}% + {provider.transaction_fee_fixed}€
                </span>
              </div>

              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Testmodus</span>
                <Badge variant={provider.is_test_mode ? 'warning' : 'default'}>
                  {provider.is_test_mode ? 'Test' : 'Live'}
                </Badge>
              </div>

              {provider.is_default && (
                <Badge variant="outline" className="w-full justify-center">
                  Standard-Anbieter
                </Badge>
              )}
            </div>

            <div className="flex gap-2">
              <div className="flex items-center gap-2 flex-1">
                <Switch
                  checked={provider.is_active}
                  onCheckedChange={(checked) => toggleProvider(provider.id, checked)}
                />
                <span className="text-sm">
                  {provider.is_active ? 'Aktiv' : 'Inaktiv'}
                </span>
              </div>

              <Button variant="outline" size="sm">
                <Settings className="h-4 w-4" />
              </Button>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}
```

### 2. Payment Processing (Checkout Integration)

#### PaymentCheckout
```tsx
// src/pages/plugins/payment/PaymentCheckout.tsx
import { useState } from 'react';
import { loadStripe } from '@stripe/stripe-js';
import { Elements, CardElement, useStripe, useElements } from '@stripe/react-stripe-js';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Label } from '@/components/ui/label';
import { CreditCard, Smartphone, Wallet } from 'lucide-react';

const stripePromise = loadStripe(process.env.REACT_APP_STRIPE_PUBLIC_KEY || '');

interface PaymentCheckoutProps {
  orderId: number;
  amount: number;
  onSuccess: () => void;
  onError: (error: string) => void;
}

function CheckoutForm({ orderId, amount, onSuccess, onError }: PaymentCheckoutProps) {
  const stripe = useStripe();
  const elements = useElements();
  const [paymentMethod, setPaymentMethod] = useState('card');
  const [processing, setProcessing] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!stripe || !elements) return;

    setProcessing(true);

    try {
      if (paymentMethod === 'card') {
        const cardElement = elements.getElement(CardElement);
        if (!cardElement) return;

        const { error, paymentMethod: stripePaymentMethod } =
          await stripe.createPaymentMethod({
            type: 'card',
            card: cardElement,
          });

        if (error) {
          onError(error.message || 'Payment failed');
          setProcessing(false);
          return;
        }

        // Process payment on backend
        const response = await fetch('/api/v1/payments/process', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            order_id: orderId,
            amount,
            payment_method: 'credit_card',
            payment_method_id: stripePaymentMethod?.id,
          }),
        });

        const data = await response.json();

        if (data.status === 'succeeded' || data.status === 'authorized') {
          onSuccess();
        } else {
          onError('Payment processing failed');
        }
      }
    } catch (error) {
      onError('An error occurred during payment');
    } finally {
      setProcessing(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Payment Method Selection */}
      <div>
        <Label className="mb-3 block">Zahlungsmethode wählen</Label>
        <RadioGroup value={paymentMethod} onValueChange={setPaymentMethod}>
          <div className="grid grid-cols-3 gap-3">
            <Card
              className={`p-4 cursor-pointer ${
                paymentMethod === 'card' ? 'border-blue-500 border-2' : ''
              }`}
              onClick={() => setPaymentMethod('card')}
            >
              <RadioGroupItem value="card" id="card" className="sr-only" />
              <Label htmlFor="card" className="cursor-pointer">
                <div className="flex flex-col items-center gap-2">
                  <CreditCard className="h-8 w-8" />
                  <span className="text-sm font-medium">Kreditkarte</span>
                </div>
              </Label>
            </Card>

            <Card
              className={`p-4 cursor-pointer ${
                paymentMethod === 'apple_pay' ? 'border-blue-500 border-2' : ''
              }`}
              onClick={() => setPaymentMethod('apple_pay')}
            >
              <RadioGroupItem value="apple_pay" id="apple_pay" className="sr-only" />
              <Label htmlFor="apple_pay" className="cursor-pointer">
                <div className="flex flex-col items-center gap-2">
                  <Smartphone className="h-8 w-8" />
                  <span className="text-sm font-medium">Apple Pay</span>
                </div>
              </Label>
            </Card>

            <Card
              className={`p-4 cursor-pointer ${
                paymentMethod === 'google_pay' ? 'border-blue-500 border-2' : ''
              }`}
              onClick={() => setPaymentMethod('google_pay')}
            >
              <RadioGroupItem value="google_pay" id="google_pay" className="sr-only" />
              <Label htmlFor="google_pay" className="cursor-pointer">
                <div className="flex flex-col items-center gap-2">
                  <Wallet className="h-8 w-8" />
                  <span className="text-sm font-medium">Google Pay</span>
                </div>
              </Label>
            </Card>
          </div>
        </RadioGroup>
      </div>

      {/* Card Input */}
      {paymentMethod === 'card' && (
        <Card className="p-4">
          <Label className="mb-2 block">Kartendaten</Label>
          <CardElement
            options={{
              style: {
                base: {
                  fontSize: '16px',
                  color: '#424770',
                  '::placeholder': {
                    color: '#aab7c4',
                  },
                },
                invalid: {
                  color: '#9e2146',
                },
              },
            }}
          />
        </Card>
      )}

      {/* Payment Summary */}
      <Card className="p-4 bg-gray-50">
        <div className="flex justify-between items-center mb-2">
          <span className="font-medium">Zu zahlen:</span>
          <span className="text-2xl font-bold">{amount.toFixed(2)} €</span>
        </div>
      </Card>

      <Button
        type="submit"
        className="w-full"
        disabled={!stripe || processing}
        size="lg"
      >
        {processing ? 'Verarbeitung...' : `${amount.toFixed(2)} € bezahlen`}
      </Button>

      {/* Security Badge */}
      <div className="flex items-center justify-center gap-2 text-sm text-muted-foreground">
        <svg className="h-4 w-4" fill="currentColor" viewBox="0 0 20 20">
          <path
            fillRule="evenodd"
            d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z"
            clipRule="evenodd"
          />
        </svg>
        <span>Sichere Zahlung mit PCI-DSS Zertifizierung</span>
      </div>
    </form>
  );
}

export function PaymentCheckout(props: PaymentCheckoutProps) {
  return (
    <Elements stripe={stripePromise}>
      <CheckoutForm {...props} />
    </Elements>
  );
}
```

### 3. Transaction History (Transaktionshistorie)

#### TransactionHistory
```tsx
// src/pages/plugins/payment/TransactionHistory.tsx
import { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Download, Search, RefreshCcw, Eye } from 'lucide-react';

interface Transaction {
  id: number;
  order_number: string;
  provider_transaction_id: string;
  amount: number;
  currency: string;
  payment_method: string;
  status: string;
  created_at: string;
  customer_name: string;
}

export function TransactionHistory() {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    fetchTransactions();
  }, [filter]);

  const fetchTransactions = async () => {
    const params = new URLSearchParams();
    if (filter !== 'all') params.append('status', filter);

    const response = await fetch(`/api/v1/payments/transactions?${params}`);
    const data = await response.json();
    setTransactions(data.transactions);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'captured':
      case 'succeeded':
        return 'success';
      case 'authorized':
        return 'warning';
      case 'pending':
        return 'default';
      case 'failed':
      case 'voided':
        return 'destructive';
      case 'refunded':
        return 'secondary';
      default:
        return 'default';
    }
  };

  const getStatusLabel = (status: string) => {
    const labels: Record<string, string> = {
      pending: 'Ausstehend',
      authorized: 'Autorisiert',
      captured: 'Erfasst',
      succeeded: 'Erfolgreich',
      failed: 'Fehlgeschlagen',
      refunded: 'Erstattet',
      voided: 'Storniert',
    };
    return labels[status] || status;
  };

  const filteredTransactions = transactions.filter(
    (t) =>
      t.order_number.toLowerCase().includes(searchTerm.toLowerCase()) ||
      t.customer_name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Transaktionen</h1>
        <Button variant="outline">
          <Download className="mr-2 h-4 w-4" />
          Exportieren
        </Button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-4 gap-4">
        <Card className="p-4">
          <p className="text-sm text-muted-foreground">Heute</p>
          <p className="text-2xl font-bold">1,234.56 €</p>
        </Card>
        <Card className="p-4">
          <p className="text-sm text-muted-foreground">Erfolgreich</p>
          <p className="text-2xl font-bold text-green-600">156</p>
        </Card>
        <Card className="p-4">
          <p className="text-sm text-muted-foreground">Ausstehend</p>
          <p className="text-2xl font-bold text-yellow-600">8</p>
        </Card>
        <Card className="p-4">
          <p className="text-sm text-muted-foreground">Fehlgeschlagen</p>
          <p className="text-2xl font-bold text-red-600">3</p>
        </Card>
      </div>

      {/* Filters and Search */}
      <Card className="p-4">
        <div className="flex gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Suche nach Bestellnummer oder Kunde..."
              className="pl-10"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>

          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="border rounded px-3 py-2"
          >
            <option value="all">Alle Status</option>
            <option value="succeeded">Erfolgreich</option>
            <option value="pending">Ausstehend</option>
            <option value="failed">Fehlgeschlagen</option>
            <option value="refunded">Erstattet</option>
          </select>

          <Button variant="outline" onClick={fetchTransactions}>
            <RefreshCcw className="h-4 w-4" />
          </Button>
        </div>
      </Card>

      {/* Transactions Table */}
      <Card>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Bestellung</TableHead>
              <TableHead>Kunde</TableHead>
              <TableHead>Betrag</TableHead>
              <TableHead>Zahlungsmethode</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Datum</TableHead>
              <TableHead>Aktionen</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {filteredTransactions.map((transaction) => (
              <TableRow key={transaction.id}>
                <TableCell className="font-medium">{transaction.order_number}</TableCell>
                <TableCell>{transaction.customer_name}</TableCell>
                <TableCell>
                  {transaction.amount.toFixed(2)} {transaction.currency}
                </TableCell>
                <TableCell className="capitalize">
                  {transaction.payment_method.replace('_', ' ')}
                </TableCell>
                <TableCell>
                  <Badge variant={getStatusColor(transaction.status)}>
                    {getStatusLabel(transaction.status)}
                  </Badge>
                </TableCell>
                <TableCell>
                  {new Date(transaction.created_at).toLocaleString('de-DE')}
                </TableCell>
                <TableCell>
                  <Button variant="ghost" size="sm">
                    <Eye className="h-4 w-4" />
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </Card>
    </div>
  );
}
```

### 4. Refund Processing (Rückerstattung)

#### RefundDialog
```tsx
// src/pages/plugins/payment/RefundDialog.tsx
import { useState } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { AlertCircle } from 'lucide-react';

interface RefundDialogProps {
  transactionId: number;
  transactionAmount: number;
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

export function RefundDialog({
  transactionId,
  transactionAmount,
  isOpen,
  onClose,
  onSuccess,
}: RefundDialogProps) {
  const [refundType, setRefundType] = useState<'full' | 'partial'>('full');
  const [refundAmount, setRefundAmount] = useState(transactionAmount);
  const [reason, setReason] = useState('');
  const [processing, setProcessing] = useState(false);

  const handleSubmit = async () => {
    setProcessing(true);

    try {
      const response = await fetch('/api/v1/payments/refunds', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          transaction_id: transactionId,
          refund_amount: refundType === 'full' ? transactionAmount : refundAmount,
          refund_reason: reason,
          refund_type: refundType,
        }),
      });

      if (response.ok) {
        onSuccess();
        onClose();
      }
    } catch (error) {
      console.error('Refund failed:', error);
    } finally {
      setProcessing(false);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Rückerstattung verarbeiten</DialogTitle>
        </DialogHeader>

        <div className="space-y-4">
          {/* Warning */}
          <div className="flex items-start gap-3 p-3 bg-yellow-50 border border-yellow-200 rounded">
            <AlertCircle className="h-5 w-5 text-yellow-600 mt-0.5" />
            <div className="text-sm">
              <p className="font-medium text-yellow-900">Achtung</p>
              <p className="text-yellow-700">
                Diese Aktion kann nicht rückgängig gemacht werden. Der Betrag wird dem
                Kunden zurückerstattet.
              </p>
            </div>
          </div>

          {/* Refund Type */}
          <div>
            <Label className="mb-2 block">Art der Rückerstattung</Label>
            <RadioGroup value={refundType} onValueChange={(v) => setRefundType(v as any)}>
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <RadioGroupItem value="full" id="full" />
                  <Label htmlFor="full">
                    Vollständige Rückerstattung ({transactionAmount.toFixed(2)} €)
                  </Label>
                </div>
                <div className="flex items-center gap-2">
                  <RadioGroupItem value="partial" id="partial" />
                  <Label htmlFor="partial">Teilrückerstattung</Label>
                </div>
              </div>
            </RadioGroup>
          </div>

          {/* Partial Refund Amount */}
          {refundType === 'partial' && (
            <div>
              <Label>Rückerstattungsbetrag</Label>
              <Input
                type="number"
                step="0.01"
                min="0.01"
                max={transactionAmount}
                value={refundAmount}
                onChange={(e) => setRefundAmount(parseFloat(e.target.value))}
              />
              <p className="text-sm text-muted-foreground mt-1">
                Maximal: {transactionAmount.toFixed(2)} €
              </p>
            </div>
          )}

          {/* Reason */}
          <div>
            <Label>Grund (optional)</Label>
            <Textarea
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              placeholder="z.B. Kunde war unzufrieden, Artikel beschädigt..."
              rows={3}
            />
          </div>

          {/* Actions */}
          <div className="flex gap-2">
            <Button variant="outline" onClick={onClose} className="flex-1">
              Abbrechen
            </Button>
            <Button
              onClick={handleSubmit}
              disabled={processing}
              className="flex-1"
              variant="destructive"
            >
              {processing ? 'Wird verarbeitet...' : 'Rückerstattung durchführen'}
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
```

### 5. Terminal Management (Terminal-Verwaltung)

#### TerminalManagement
```tsx
// src/pages/plugins/payment/TerminalManagement.tsx
import { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { CreditCard, Power, Settings } from 'lucide-react';

interface Terminal {
  id: number;
  terminal_name: string;
  serial_number: string;
  terminal_type: string;
  status: string;
  connection_status: string;
  location: string;
  supports_contactless: boolean;
  last_transaction_at: string | null;
}

export function TerminalManagement() {
  const [terminals, setTerminals] = useState<Terminal[]>([]);

  useEffect(() => {
    fetchTerminals();
    const interval = setInterval(fetchTerminals, 5000); // Poll every 5s
    return () => clearInterval(interval);
  }, []);

  const fetchTerminals = async () => {
    const response = await fetch('/api/v1/payments/terminals');
    const data = await response.json();
    setTerminals(data.terminals);
  };

  const activateTerminal = async (terminalId: number) => {
    await fetch(`/api/v1/payments/terminals/${terminalId}/activate`, {
      method: 'POST',
    });
    fetchTerminals();
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Terminals</h1>
        <Button>
          <CreditCard className="mr-2 h-4 w-4" />
          Terminal hinzufügen
        </Button>
      </div>

      <div className="grid grid-cols-3 gap-4">
        {terminals.map((terminal) => (
          <Card key={terminal.id} className="p-4">
            <div className="flex justify-between items-start mb-3">
              <div>
                <h3 className="font-semibold">{terminal.terminal_name}</h3>
                <p className="text-sm text-muted-foreground">{terminal.location}</p>
              </div>
              <div className="flex gap-1">
                <Badge
                  variant={
                    terminal.connection_status === 'online' ? 'success' : 'destructive'
                  }
                >
                  {terminal.connection_status}
                </Badge>
              </div>
            </div>

            <div className="space-y-2 text-sm mb-4">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Typ:</span>
                <span className="capitalize">{terminal.terminal_type}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Seriennummer:</span>
                <span className="font-mono">{terminal.serial_number}</span>
              </div>
              {terminal.supports_contactless && (
                <Badge variant="outline" className="w-full justify-center">
                  📡 Kontaktlos-fähig
                </Badge>
              )}
              {terminal.last_transaction_at && (
                <div className="text-xs text-muted-foreground">
                  Letzte Transaktion:{' '}
                  {new Date(terminal.last_transaction_at).toLocaleString('de-DE')}
                </div>
              )}
            </div>

            <div className="flex gap-2">
              {terminal.status === 'inactive' ? (
                <Button
                  variant="outline"
                  size="sm"
                  className="flex-1"
                  onClick={() => activateTerminal(terminal.id)}
                >
                  <Power className="mr-2 h-4 w-4" />
                  Aktivieren
                </Button>
              ) : (
                <Badge variant="success" className="flex-1 justify-center">
                  Aktiv
                </Badge>
              )}
              <Button variant="outline" size="sm">
                <Settings className="h-4 w-4" />
              </Button>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}
```

### 6. Reconciliation View (Zahlungsabstimmung)

#### ReconciliationView
```tsx
// src/pages/plugins/payment/ReconciliationView.tsx
import { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { CheckCircle, AlertCircle, Clock } from 'lucide-react';

interface Reconciliation {
  id: number;
  reconciliation_date: string;
  provider_name: string;
  total_transactions: number;
  successful_transactions: number;
  total_charged: number;
  total_refunded: number;
  total_fees: number;
  net_amount: number;
  expected_payout: number;
  actual_payout: number | null;
  status: string;
  variance_amount: number | null;
}

export function ReconciliationView() {
  const [reconciliations, setReconciliations] = useState<Reconciliation[]>([]);
  const [selectedDate, setSelectedDate] = useState(
    new Date().toISOString().split('T')[0]
  );

  useEffect(() => {
    fetchReconciliations();
  }, [selectedDate]);

  const fetchReconciliations = async () => {
    const response = await fetch(
      `/api/v1/payments/reconciliation?start_date=${selectedDate}`
    );
    const data = await response.json();
    setReconciliations(data.reconciliation);
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'balanced':
        return <CheckCircle className="text-green-500" />;
      case 'unbalanced':
        return <AlertCircle className="text-red-500" />;
      default:
        return <Clock className="text-yellow-500" />;
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Zahlungsabstimmung</h1>
        <input
          type="date"
          value={selectedDate}
          onChange={(e) => setSelectedDate(e.target.value)}
          className="border rounded px-3 py-2"
        />
      </div>

      {reconciliations.map((recon) => (
        <Card key={recon.id} className="p-6">
          <div className="flex justify-between items-start mb-6">
            <div>
              <h3 className="text-lg font-semibold">{recon.provider_name}</h3>
              <p className="text-sm text-muted-foreground">
                {new Date(recon.reconciliation_date).toLocaleDateString('de-DE')}
              </p>
            </div>
            <div className="flex items-center gap-2">
              {getStatusIcon(recon.status)}
              <Badge
                variant={
                  recon.status === 'balanced'
                    ? 'success'
                    : recon.status === 'unbalanced'
                    ? 'destructive'
                    : 'warning'
                }
              >
                {recon.status === 'balanced'
                  ? 'Ausgeglichen'
                  : recon.status === 'unbalanced'
                  ? 'Unausgeglichen'
                  : 'Ausstehend'}
              </Badge>
            </div>
          </div>

          <div className="grid grid-cols-4 gap-6">
            {/* Transactions */}
            <div>
              <p className="text-sm text-muted-foreground mb-1">Transaktionen</p>
              <p className="text-2xl font-bold">{recon.total_transactions}</p>
              <p className="text-sm text-green-600">
                {recon.successful_transactions} erfolgreich
              </p>
            </div>

            {/* Charged */}
            <div>
              <p className="text-sm text-muted-foreground mb-1">Eingezahlt</p>
              <p className="text-2xl font-bold">{recon.total_charged.toFixed(2)} €</p>
            </div>

            {/* Refunded */}
            <div>
              <p className="text-sm text-muted-foreground mb-1">Rückerstattet</p>
              <p className="text-2xl font-bold text-red-600">
                -{recon.total_refunded.toFixed(2)} €
              </p>
            </div>

            {/* Net */}
            <div>
              <p className="text-sm text-muted-foreground mb-1">Netto</p>
              <p className="text-2xl font-bold text-green-600">
                {recon.net_amount.toFixed(2)} €
              </p>
            </div>
          </div>

          {/* Payout Info */}
          {recon.expected_payout && (
            <div className="mt-6 pt-6 border-t">
              <div className="grid grid-cols-3 gap-4">
                <div>
                  <p className="text-sm text-muted-foreground">Erwartete Auszahlung</p>
                  <p className="text-lg font-semibold">
                    {recon.expected_payout.toFixed(2)} €
                  </p>
                </div>
                {recon.actual_payout && (
                  <>
                    <div>
                      <p className="text-sm text-muted-foreground">Tatsächliche Auszahlung</p>
                      <p className="text-lg font-semibold">
                        {recon.actual_payout.toFixed(2)} €
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">Abweichung</p>
                      <p
                        className={`text-lg font-semibold ${
                          (recon.variance_amount || 0) >= 0
                            ? 'text-green-600'
                            : 'text-red-600'
                        }`}
                      >
                        {recon.variance_amount?.toFixed(2)} €
                      </p>
                    </div>
                  </>
                )}
              </div>
            </div>
          )}
        </Card>
      ))}
    </div>
  );
}
```

## Routing-Konfiguration

```tsx
// src/routes/paymentRoutes.tsx
import { Route } from 'react-router-dom';
import { PaymentProviderList } from '@/pages/plugins/payment/PaymentProviderList';
import { TransactionHistory } from '@/pages/plugins/payment/TransactionHistory';
import { TerminalManagement } from '@/pages/plugins/payment/TerminalManagement';
import { ReconciliationView } from '@/pages/plugins/payment/ReconciliationView';

export const paymentRoutes = (
  <Route path="/payments">
    <Route path="providers" element={<PaymentProviderList />} />
    <Route path="transactions" element={<TransactionHistory />} />
    <Route path="terminals" element={<TerminalManagement />} />
    <Route path="reconciliation" element={<ReconciliationView />} />
  </Route>
);
```

## Security Best Practices

```tsx
// src/utils/paymentSecurity.ts

// NEVER store sensitive card data in frontend
export const sanitizeCardData = (cardData: any) => {
  // Only keep last 4 digits
  return {
    last4: cardData.number?.slice(-4),
    brand: cardData.brand,
    exp_month: cardData.exp_month,
    exp_year: cardData.exp_year,
    // Remove full card number
  };
};

// Always use HTTPS
export const ensureSecureConnection = () => {
  if (window.location.protocol !== 'https:' && process.env.NODE_ENV === 'production') {
    console.error('HTTPS required for payment processing');
    window.location.href = `https:${window.location.href.substring(window.location.protocol.length)}`;
  }
};

// Token-based authentication
export const getSecureHeaders = () => {
  return {
    'Content-Type': 'application/json',
    Authorization: `Bearer ${localStorage.getItem('auth_token')}`,
  };
};
```

## Deployment Checklist

- [ ] Stripe/PayPal SDKs konfiguriert
- [ ] HTTPS in Produktion aktiviert
- [ ] PCI-DSS Compliance geprüft
- [ ] Payment Provider API Keys sicher gespeichert
- [ ] Webhook-Endpunkte konfiguriert
- [ ] Test-Modus funktioniert
- [ ] Refund-Prozess getestet
- [ ] Terminal-Integration getestet
- [ ] Reconciliation-Reports funktional
- [ ] Fehlerbehandlung implementiert
- [ ] Logging für Audit-Trail
- [ ] 3D Secure aktiviert (falls benötigt)
