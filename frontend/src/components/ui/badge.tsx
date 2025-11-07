import { HTMLAttributes, forwardRef } from 'react'
import { clsx } from 'clsx'

export interface BadgeProps extends HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'success' | 'warning' | 'error' | 'secondary'
}

export const Badge = forwardRef<HTMLDivElement, BadgeProps>(
  ({ className, variant = 'default', ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={clsx(
          'inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold',
          {
            'bg-blue-100 text-blue-700': variant === 'default',
            'bg-green-100 text-green-700': variant === 'success',
            'bg-yellow-100 text-yellow-700': variant === 'warning',
            'bg-red-100 text-red-700': variant === 'error',
            'bg-gray-100 text-gray-700': variant === 'secondary',
          },
          className
        )}
        {...props}
      />
    )
  }
)

Badge.displayName = 'Badge'
