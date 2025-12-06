import * as React from 'react'
import { cva, type VariantProps } from 'class-variance-authority'
import { cn } from '@/lib/utils'

const badgeVariants = cva(
  'inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-accent focus:ring-offset-2',
  {
    variants: {
      variant: {
        default: 'bg-accent bg-opacity-10 text-accent border-transparent',
        success: 'bg-success bg-opacity-10 text-success border-transparent',
        warning: 'bg-warning bg-opacity-10 text-warning border-transparent',
        critical: 'bg-critical bg-opacity-10 text-critical border-transparent',
        purple: 'bg-purple-500 bg-opacity-10 text-purple-500 border-transparent',
        gray: 'bg-text-muted bg-opacity-10 text-text-muted border-transparent',
        outline: 'border border-border bg-transparent text-text-primary',
      },
    },
    defaultVariants: {
      variant: 'default',
    },
  }
)

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, ...props }: BadgeProps) {
  return <div className={cn(badgeVariants({ variant }), className)} {...props} />
}

export { Badge, badgeVariants }
