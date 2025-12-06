import * as React from 'react'
import { cn } from '@/lib/utils'
import type { DecisionType } from '@/types'

const Timeline = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn('relative space-y-4', className)}
    {...props}
  />
))
Timeline.displayName = 'Timeline'

const TimelineItem = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn('relative flex gap-4 pb-4', className)}
    {...props}
  />
))
TimelineItem.displayName = 'TimelineItem'

interface TimelineIconProps extends React.HTMLAttributes<HTMLDivElement> {
  type?: DecisionType | string
}

const getIconColor = (type?: DecisionType | string): string => {
  if (!type) return 'bg-text-muted'

  const upperType = type.toUpperCase()

  // Signal (BUY/SELL/HOLD): Blue
  if (upperType === 'SIGNAL' || upperType.includes('BUY') || upperType.includes('SELL') || upperType.includes('HOLD')) {
    return 'bg-accent'
  }
  // Warning: Orange
  if (upperType === 'WARNING') {
    return 'bg-warning'
  }
  // Rejection: Red
  if (upperType === 'REJECTION') {
    return 'bg-critical'
  }
  // Override: Purple
  if (upperType === 'OVERRIDE') {
    return 'bg-purple-500'
  }

  return 'bg-text-muted'
}

const TimelineIcon = React.forwardRef<
  HTMLDivElement,
  TimelineIconProps
>(({ className, type, ...props }, ref) => (
  <div className="relative flex h-full flex-col items-center">
    <div
      ref={ref}
      className={cn(
        'flex h-8 w-8 shrink-0 items-center justify-center rounded-full',
        getIconColor(type),
        'ring-4 ring-background',
        className
      )}
      {...props}
    >
      <div className="h-2 w-2 rounded-full bg-white" />
    </div>
    <div className="mt-2 h-full w-px bg-border" />
  </div>
))
TimelineIcon.displayName = 'TimelineIcon'

const TimelineContent = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn('flex-1 space-y-1', className)}
    {...props}
  />
))
TimelineContent.displayName = 'TimelineContent'

const TimelineTitle = React.forwardRef<
  HTMLParagraphElement,
  React.HTMLAttributes<HTMLHeadingElement>
>(({ className, ...props }, ref) => (
  <h4
    ref={ref}
    className={cn('font-semibold text-sm text-text-primary', className)}
    {...props}
  />
))
TimelineTitle.displayName = 'TimelineTitle'

const TimelineDescription = React.forwardRef<
  HTMLParagraphElement,
  React.HTMLAttributes<HTMLParagraphElement>
>(({ className, ...props }, ref) => (
  <p
    ref={ref}
    className={cn('text-sm text-text-secondary', className)}
    {...props}
  />
))
TimelineDescription.displayName = 'TimelineDescription'

const TimelineTime = React.forwardRef<
  HTMLParagraphElement,
  React.HTMLAttributes<HTMLParagraphElement>
>(({ className, ...props }, ref) => (
  <p
    ref={ref}
    className={cn('text-xs text-text-muted', className)}
    {...props}
  />
))
TimelineTime.displayName = 'TimelineTime'

export {
  Timeline,
  TimelineItem,
  TimelineIcon,
  TimelineContent,
  TimelineTitle,
  TimelineDescription,
  TimelineTime,
}
