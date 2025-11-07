import { AlertCircle } from 'lucide-react'
import { Button } from '@/components/ui/button'

interface ErrorStateProps {
  message?: string
  details?: string
  onRetry?: () => void
}

export function ErrorState({
  message = 'Ein Fehler ist aufgetreten',
  details,
  onRetry,
}: ErrorStateProps) {
  return (
    <div className="flex flex-col items-center justify-center h-64">
      <AlertCircle className="h-12 w-12 text-red-500 mb-4" />
      <p className="text-gray-700 font-medium mb-2">{message}</p>
      {details && (
        <p className="text-sm text-gray-500 mb-4 max-w-md text-center">{details}</p>
      )}
      {onRetry && (
        <Button onClick={onRetry} variant="outline">
          Erneut versuchen
        </Button>
      )}
    </div>
  )
}
