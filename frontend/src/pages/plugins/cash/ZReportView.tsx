import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Download, Printer, FileText, TrendingUp, TrendingDown } from 'lucide-react'

export function ZReportView() {
  // Mock data - in real app, this would come from the API
  const reportData = {
    session_id: 123,
    date: new Date().toISOString(),
    register_name: 'Kasse 1',
    opened_by: 'Max Mustermann',
    closed_by: 'Erika Muster',
    opening_balance: 200.0,
    cash_sales: 1453.5,
    card_sales: 2345.75,
    total_sales: 3799.25,
    cash_in: 50.0,
    cash_out: 100.0,
    expected_cash: 1603.5,
    actual_cash: 1598.0,
    variance: -5.5,
    transaction_count: 87,
    average_transaction: 43.67,
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold">Z-Bericht</h1>
          <p className="text-muted-foreground">
            {new Date(reportData.date).toLocaleDateString('de-DE')} - {reportData.register_name}
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline">
            <Printer className="mr-2 h-4 w-4" />
            Drucken
          </Button>
          <Button variant="outline">
            <Download className="mr-2 h-4 w-4" />
            PDF Export
          </Button>
        </div>
      </div>

      {/* Report Header */}
      <Card className="p-6">
        <div className="flex items-center gap-3 mb-6">
          <div className="p-3 bg-blue-100 rounded-full">
            <FileText className="h-6 w-6 text-blue-600" />
          </div>
          <div>
            <h2 className="text-xl font-bold">Tagesabschluss-Bericht</h2>
            <p className="text-sm text-muted-foreground">Sitzung #{reportData.session_id}</p>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-6">
          <div>
            <p className="text-sm text-muted-foreground mb-1">Geöffnet von</p>
            <p className="font-medium">{reportData.opened_by}</p>
          </div>
          <div>
            <p className="text-sm text-muted-foreground mb-1">Geschlossen von</p>
            <p className="font-medium">{reportData.closed_by}</p>
          </div>
        </div>
      </Card>

      {/* Financial Summary */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="p-4">
          <p className="text-sm text-muted-foreground mb-1">Gesamtumsatz</p>
          <p className="text-2xl font-bold text-green-600">{reportData.total_sales.toFixed(2)} €</p>
          <div className="flex items-center gap-1 mt-2 text-sm text-green-600">
            <TrendingUp className="h-4 w-4" />
            <span>{reportData.transaction_count} Transaktionen</span>
          </div>
        </Card>

        <Card className="p-4">
          <p className="text-sm text-muted-foreground mb-1">Barverkäufe</p>
          <p className="text-2xl font-bold">{reportData.cash_sales.toFixed(2)} €</p>
          <p className="text-sm text-muted-foreground mt-2">
            {((reportData.cash_sales / reportData.total_sales) * 100).toFixed(1)}% vom Umsatz
          </p>
        </Card>

        <Card className="p-4">
          <p className="text-sm text-muted-foreground mb-1">Kartenverkäufe</p>
          <p className="text-2xl font-bold">{reportData.card_sales.toFixed(2)} €</p>
          <p className="text-sm text-muted-foreground mt-2">
            {((reportData.card_sales / reportData.total_sales) * 100).toFixed(1)}% vom Umsatz
          </p>
        </Card>

        <Card className="p-4">
          <p className="text-sm text-muted-foreground mb-1">Ø Transaktion</p>
          <p className="text-2xl font-bold">{reportData.average_transaction.toFixed(2)} €</p>
        </Card>
      </div>

      {/* Cash Reconciliation */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold mb-4">Bargeld-Abgleich</h3>
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-6">
            <div className="space-y-3">
              <div className="flex justify-between p-3 bg-muted/50 rounded-lg">
                <span className="text-muted-foreground">Anfangsbestand</span>
                <span className="font-semibold">{reportData.opening_balance.toFixed(2)} €</span>
              </div>
              <div className="flex justify-between p-3 bg-muted/50 rounded-lg">
                <span className="text-muted-foreground">Barverkäufe</span>
                <span className="font-semibold text-green-600">
                  +{reportData.cash_sales.toFixed(2)} €
                </span>
              </div>
              <div className="flex justify-between p-3 bg-muted/50 rounded-lg">
                <span className="text-muted-foreground">Bareinzahlungen</span>
                <span className="font-semibold text-green-600">+{reportData.cash_in.toFixed(2)} €</span>
              </div>
              <div className="flex justify-between p-3 bg-muted/50 rounded-lg">
                <span className="text-muted-foreground">Barauszahlungen</span>
                <span className="font-semibold text-red-600">-{reportData.cash_out.toFixed(2)} €</span>
              </div>
            </div>

            <div className="space-y-3">
              <div className="p-4 bg-blue-50 rounded-lg border-2 border-blue-200">
                <p className="text-sm text-muted-foreground mb-1">Erwarteter Bestand</p>
                <p className="text-3xl font-bold text-blue-600">
                  {reportData.expected_cash.toFixed(2)} €
                </p>
              </div>

              <div className="p-4 bg-green-50 rounded-lg border-2 border-green-200">
                <p className="text-sm text-muted-foreground mb-1">Tatsächlicher Bestand</p>
                <p className="text-3xl font-bold text-green-600">
                  {reportData.actual_cash.toFixed(2)} €
                </p>
              </div>

              <div
                className={`p-4 rounded-lg border-2 ${
                  reportData.variance === 0
                    ? 'bg-green-50 border-green-200'
                    : reportData.variance > 0
                    ? 'bg-yellow-50 border-yellow-200'
                    : 'bg-red-50 border-red-200'
                }`}
              >
                <div className="flex items-center gap-2 mb-1">
                  {reportData.variance !== 0 && (
                    reportData.variance > 0 ? (
                      <TrendingUp className="h-5 w-5 text-yellow-600" />
                    ) : (
                      <TrendingDown className="h-5 w-5 text-red-600" />
                    )
                  )}
                  <p className="text-sm text-muted-foreground">Abweichung</p>
                </div>
                <p
                  className={`text-3xl font-bold ${
                    reportData.variance === 0
                      ? 'text-green-600'
                      : reportData.variance > 0
                      ? 'text-yellow-600'
                      : 'text-red-600'
                  }`}
                >
                  {reportData.variance > 0 ? '+' : ''}
                  {reportData.variance.toFixed(2)} €
                </p>
              </div>
            </div>
          </div>

          {reportData.variance !== 0 && (
            <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
              <p className="text-sm font-medium text-yellow-900">
                ⚠️ Achtung: Es gibt eine Abweichung zwischen erwartetem und tatsächlichem Bestand.
                Bitte überprüfen Sie die Zählung.
              </p>
            </div>
          )}
        </div>
      </Card>

      {/* Actions */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold mb-4">Aktionen</h3>
        <div className="flex gap-3">
          <Button variant="outline" className="flex-1">
            <Printer className="mr-2 h-4 w-4" />
            Kassenbon drucken
          </Button>
          <Button variant="outline" className="flex-1">
            <Download className="mr-2 h-4 w-4" />
            Als PDF speichern
          </Button>
          <Button variant="outline" className="flex-1">
            <FileText className="mr-2 h-4 w-4" />
            An Buchhaltung senden
          </Button>
        </div>
      </Card>
    </div>
  )
}
