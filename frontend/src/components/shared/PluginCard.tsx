import { ReactNode } from 'react'
import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'

interface PluginCardProps {
  title: string
  description: string
  icon: ReactNode
  status: 'active' | 'inactive'
  version: string
  category?: string
  onToggle: () => void
  onConfigure?: () => void
}

export function PluginCard({
  title,
  description,
  icon,
  status,
  version,
  category,
  onToggle,
  onConfigure,
}: PluginCardProps) {
  return (
    <Card className="p-6 hover:shadow-md transition-shadow">
      <div className="flex items-start gap-4">
        <div className="text-4xl flex-shrink-0">{icon}</div>
        <div className="flex-1 min-w-0">
          <div className="flex justify-between items-start mb-2 gap-2">
            <div>
              <h3 className="text-lg font-semibold truncate">{title}</h3>
              {category && (
                <span className="text-xs text-gray-500">{category}</span>
              )}
            </div>
            <Badge variant={status === 'active' ? 'success' : 'secondary'}>
              {status === 'active' ? 'Aktiv' : 'Inaktiv'}
            </Badge>
          </div>
          <p className="text-sm text-gray-600 mb-3 line-clamp-2">{description}</p>
          <div className="flex justify-between items-center gap-2">
            <span className="text-xs text-gray-500">Version {version}</span>
            <div className="flex gap-2">
              {onConfigure && status === 'active' && (
                <Button size="sm" variant="outline" onClick={onConfigure}>
                  Einstellungen
                </Button>
              )}
              <Button
                size="sm"
                variant={status === 'active' ? 'outline' : 'default'}
                onClick={onToggle}
              >
                {status === 'active' ? 'Deaktivieren' : 'Aktivieren'}
              </Button>
            </div>
          </div>
        </div>
      </div>
    </Card>
  )
}
