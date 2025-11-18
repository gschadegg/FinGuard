import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { RefreshCcw, RefreshCwOff } from 'lucide-react'

const formatCurrency = (n) =>
  new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    maximumFractionDigits: 0,
  }).format(n)

export function AccountsCard({ accounts, title = 'Accounts' }) {
  return (
    <Card className="shadow-sm w-full">
      <div className="flex items-center justify-between px-6 py-1 ">
        <div className="flex flex-col gap-1">
          <h2 className="text-lg font-medium flex items-center gap-2">{title}</h2>
        </div>

        <Badge variant="secondary" className="rounded-full text-xs font-medium">
          {accounts?.length ?? 0} Connected
        </Badge>
      </div>

      <div className="divide-y px-6 space-y-2">
        {accounts?.map((account) => (
          <AccountRow key={account.id} account={account} />
        ))}
      </div>
    </Card>
  )
}

export function AccountRow({ account }) {
  const { name, mask, balance, available, selected, institution_name } = account
  const isSynced = selected === true

  return (
    <Card className={'shadow-none flex-row px-5 py-4 flex items-center justify-between border'}>
      <div className="flex flex-col gap-1 min-w-0">
        <span className="text-sm font-medium truncate">{`${institution_name}: ${name}`}</span>
        <span className="text-xs text-muted-foreground">••••••••{mask}</span>
      </div>

      <div className="flex items-center gap-16 text-xs">
        <div className="flex items-center gap-10">
          <div className="flex flex-col items-end gap-1">
            <span className="text-[11px] uppercase tracking-wide text-muted-foreground">
              Balance
            </span>
            <span className="text-sm font-semibold">{formatCurrency(balance)}</span>
          </div>

          <div className="flex flex-col items-end gap-1">
            <span className="text-[11px] uppercase tracking-wide text-muted-foreground">
              Available
            </span>
            <span className="text-sm font-semibold text-emerald-600">
              {formatCurrency(available)}
            </span>
          </div>
        </div>
        <div className="flex items-center gap-1 text-xs">
          {isSynced ? (
            <RefreshCcw className="inline-flex h-4 w-4 rounded-full text-emerald-500" />
          ) : (
            <RefreshCwOff className="inline-flex h-4 w-4 rounded-full text-muted-foreground/40" />
          )}
          <span className="text-muted-foreground">{isSynced ? 'Synced' : 'Not Synced'}</span>
        </div>
      </div>
    </Card>
  )
}
