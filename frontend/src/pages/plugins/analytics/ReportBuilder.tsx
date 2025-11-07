import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { LoadingState } from '@/components/shared/LoadingState'
import { ErrorState } from '@/components/shared/ErrorState'
import { Plus, FileText, Download, Play } from 'lucide-react'
import { useReports } from '@/hooks/useAnalytics'

export function ReportBuilder() {
  const { data: reports, isLoading, error, refetch } = useReports()

  if (isLoading) return <LoadingState message="Lade Berichte..." />
  if (error) return <ErrorState message="Fehler beim Laden" onRetry={() => refetch()} />

  const getReportTypeLabel = (type: string) => {
    const labels: Record<string, string> = {
      sales: 'Umsatz',
      inventory: 'Bestand',
      employee: 'Mitarbeiter',
      customer: 'Kunden',
      financial: 'Finanzen',
      custom: 'Benutzerdefiniert',
    }
    return labels[type] || type
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Berichts-Generator</h1>
        <Button>
          <Plus className="mr-2 h-4 w-4" />
          Neuer Bericht
        </Button>
      </div>

      <div className="space-y-3">
        {reports?.map((report) => (
          <Card key={report.id} className="p-4">
            <div className="flex flex-col md:flex-row justify-between gap-4">
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-3">
                  <FileText className="h-5 w-5 text-muted-foreground" />
                  <div>
                    <h3 className="font-semibold">{report.report_name}</h3>
                    <div className="flex items-center gap-2 mt-1">
                      <Badge variant="outline">{getReportTypeLabel(report.report_type)}</Badge>
                      <span className="text-sm text-muted-foreground">
                        {report.columns.length} Spalten
                      </span>
                    </div>
                  </div>
                </div>

                {report.description && (
                  <p className="text-sm text-muted-foreground mb-3">{report.description}</p>
                )}

                <div className="flex flex-wrap gap-2">
                  {report.columns.slice(0, 5).map((col, idx) => (
                    <Badge key={idx} variant="secondary" className="text-xs">
                      {col.label}
                    </Badge>
                  ))}
                  {report.columns.length > 5 && (
                    <Badge variant="secondary" className="text-xs">
                      +{report.columns.length - 5} weitere
                    </Badge>
                  )}
                </div>
              </div>

              <div className="flex flex-col gap-2 min-w-[160px]">
                <Button variant="default" size="sm">
                  <Play className="mr-2 h-4 w-4" />
                  Ausführen
                </Button>
                <Button variant="outline" size="sm">
                  <Download className="mr-2 h-4 w-4" />
                  Exportieren
                </Button>
                <Button variant="ghost" size="sm">
                  Bearbeiten
                </Button>
              </div>
            </div>
          </Card>
        ))}
      </div>

      {!reports || reports.length === 0 && (
        <Card className="p-8 text-center text-muted-foreground">
          <FileText className="h-12 w-12 mx-auto mb-4 opacity-50" />
          <p>Keine Berichte vorhanden</p>
          <Button variant="link" className="mt-2">
            Ersten Bericht erstellen
          </Button>
        </Card>
      )}
    </div>
  )
}
