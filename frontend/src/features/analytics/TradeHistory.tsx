import { type ColumnDef } from '@tanstack/react-table'
import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Button } from '@/components/ui/button'
import { useTrades } from '@/hooks/useTrades'
import type { Trade } from '@/types'
import { cn } from '@/lib/utils'

interface TradeHistoryProps {
  teamId: number
}

export function TradeHistory({ teamId }: TradeHistoryProps) {
  const [page, setPage] = useState(1)
  const [statusFilter, setStatusFilter] = useState<'open' | 'closed' | undefined>()
  const pageSize = 20

  const { trades, total, isLoading, error } = useTrades(teamId, {
    page,
    pageSize,
    status: statusFilter,
  })

  const columns: ColumnDef<Trade>[] = [
    {
      accessorKey: 'opened_at',
      header: 'Zeit',
      enableSorting: true,
      cell: ({ row }) => {
        const date = new Date(row.original.opened_at)
        return (
          <div className="text-sm">
            <div>{date.toLocaleDateString('de-DE')}</div>
            <div className="text-text-muted text-xs">
              {date.toLocaleTimeString('de-DE')}
            </div>
          </div>
        )
      },
    },
    {
      accessorKey: 'symbol',
      header: 'Symbol',
      enableSorting: true,
      cell: ({ row }) => (
        <span className="font-medium">{row.original.symbol}</span>
      ),
    },
    {
      accessorKey: 'side',
      header: 'Typ',
      enableSorting: true,
      cell: ({ row }) => (
        <span
          className={cn(
            'px-2 py-1 rounded text-xs font-medium',
            row.original.side === 'BUY'
              ? 'bg-green-500/20 text-green-400'
              : 'bg-red-500/20 text-red-400'
          )}
        >
          {row.original.side}
        </span>
      ),
    },
    {
      accessorKey: 'size',
      header: 'Größe',
      cell: ({ row }) => row.original.size.toFixed(2),
    },
    {
      accessorKey: 'entry_price',
      header: 'Entry',
      cell: ({ row }) => row.original.entry_price.toFixed(5),
    },
    {
      accessorKey: 'exit_price',
      header: 'Exit',
      cell: ({ row }) =>
        row.original.exit_price ? row.original.exit_price.toFixed(5) : '-',
    },
    {
      accessorKey: 'pnl',
      header: 'P/L',
      enableSorting: true,
      cell: ({ row }) => {
        const pnl = row.original.pnl
        if (pnl === null || pnl === undefined) return '-'

        const isPositive = pnl >= 0
        return (
          <span
            className={cn(
              'font-medium',
              isPositive ? 'text-green-400' : 'text-red-400'
            )}
          >
            {isPositive ? '+' : ''}
            {pnl.toFixed(2)} €
          </span>
        )
      },
    },
    {
      accessorKey: 'status',
      header: 'Status',
      enableSorting: true,
      cell: ({ row }) => (
        <span
          className={cn(
            'px-2 py-1 rounded text-xs font-medium',
            row.original.status === 'open'
              ? 'bg-blue-500/20 text-blue-400'
              : 'bg-gray-500/20 text-gray-400'
          )}
        >
          {row.original.status === 'open' ? 'Offen' : 'Geschlossen'}
        </span>
      ),
    },
  ]

  const totalPages = Math.ceil(total / pageSize)

  const handleExportCSV = () => {
    // Prepare CSV data
    const headers = ['Zeit', 'Symbol', 'Typ', 'Größe', 'Entry', 'Exit', 'P/L', 'Status']
    const rows = trades.map((trade) => [
      new Date(trade.opened_at).toLocaleString('de-DE'),
      trade.symbol,
      trade.side,
      trade.size.toFixed(2),
      trade.entry_price.toFixed(5),
      trade.exit_price ? trade.exit_price.toFixed(5) : '-',
      trade.pnl !== null ? trade.pnl.toFixed(2) : '-',
      trade.status,
    ])

    const csvContent = [
      headers.join(','),
      ...rows.map((row) => row.join(',')),
    ].join('\n')

    // Download CSV
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
    const link = document.createElement('a')
    const url = URL.createObjectURL(blob)
    link.setAttribute('href', url)
    link.setAttribute('download', `trades-team-${teamId}-${Date.now()}.csv`)
    link.style.visibility = 'hidden'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }

  if (error) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Trade History</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8 text-critical">
            Error loading trades: {error.message}
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>Trade History</CardTitle>
          <div className="flex items-center gap-2">
            <div className="flex gap-1">
              <Button
                variant={statusFilter === undefined ? 'default' : 'outline'}
                size="sm"
                onClick={() => setStatusFilter(undefined)}
              >
                Alle
              </Button>
              <Button
                variant={statusFilter === 'open' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setStatusFilter('open')}
              >
                Offen
              </Button>
              <Button
                variant={statusFilter === 'closed' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setStatusFilter('closed')}
              >
                Geschlossen
              </Button>
            </div>
            <Button variant="outline" size="sm" onClick={handleExportCSV}>
              Export CSV
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div className="text-center py-8 text-text-secondary">
            Loading trades...
          </div>
        ) : (
          <>
            <DataTable columns={columns} data={trades} />
            {totalPages > 1 && (
              <div className="flex items-center justify-between mt-4">
                <div className="text-sm text-text-secondary">
                  Seite {page} von {totalPages} ({total} Trades gesamt)
                </div>
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setPage((p) => Math.max(1, p - 1))}
                    disabled={page === 1}
                  >
                    Zurück
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                    disabled={page === totalPages}
                  >
                    Weiter
                  </Button>
                </div>
              </div>
            )}
          </>
        )}
      </CardContent>
    </Card>
  )
}
