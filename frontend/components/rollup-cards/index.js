import { DollarSign, ShieldAlert, Loader } from 'lucide-react'

import { Card, CardAction, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'

const RollupCardRow = () => {
  return (
    <div
      className="grid gap-4
      [grid-template-columns:repeat(auto-fit,minmax(16rem,1fr))]
      *:data-[slot=card]:from-primary/5
      *:data-[slot=card]:to-card
      *:data-[slot=card]:shadow-xs
      dark:*:data-[slot=card]:bg-card
      items-stretch mb-10"
    >
      <Card className="h-full">
        <CardHeader>
          <CardDescription>Total Balance</CardDescription>
          <CardTitle className="text-2xl font-semibold tabular-nums @[250px]/card:text-3xl">
            $1,250.00
          </CardTitle>
          <CardAction>
            <DollarSign className="h-5 w-5 text-gray-500" />
          </CardAction>
        </CardHeader>
      </Card>
      <Card className="h-full">
        <CardHeader>
          <CardDescription>Pending Transations</CardDescription>
          <CardTitle className="text-2xl font-semibold tabular-nums @[250px]/card:text-3xl">
            -$1,250.00
          </CardTitle>
          <CardAction>
            <Loader className="h-5 w-5 text-gray-500" />
          </CardAction>
        </CardHeader>
      </Card>
      <Card className="h-full">
        <CardHeader>
          <CardDescription>Potential Risks</CardDescription>
          <CardTitle className="text-2xl font-semibold tabular-nums @[250px]/card:text-3xl">
            6
          </CardTitle>
          <CardAction>
            <ShieldAlert className="h-5 w-5 text-gray-500" />
          </CardAction>
        </CardHeader>
      </Card>
    </div>
  )
}

export default RollupCardRow
