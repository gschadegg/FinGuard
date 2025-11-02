import { Card, CardAction, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'

const RollupCardRow = ({ cardData = [] }) => {
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
      {cardData?.map((card) => {
        const { icon: Icon } = card
        return (
          <Card className="h-full" key={card.title}>
            <CardHeader>
              <CardDescription>{card.title}</CardDescription>
              <CardTitle className="text-2xl font-semibold tabular-nums @[250px]/card:text-3xl">
                {card.detail}
              </CardTitle>
              <CardAction>
                <Icon className="h-5 w-5 text-gray-500" />
              </CardAction>
            </CardHeader>
          </Card>
        )
      })}
    </div>
  )
}

export default RollupCardRow
