import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

export function DashboardCard({
  title,
  iconTitle: IconTitle,
  iconRight: IconRight,
  TopRightComponent = null,
  children,
  ...props
}) {
  return (
    <Card className="shadow-sm gap-2" {...props}>
      <CardHeader className="flex flex-row items-center justify-between space-y-0">
        <CardTitle className="text-lg font-medium flex items-center gap-2">
          {IconTitle && <IconTitle className="h-5 w-5 text-red-700" />}
          {title}
        </CardTitle>
        {IconRight && <IconRight className="h-5 w-5 text-gray-500" />}
        {TopRightComponent}
      </CardHeader>
      <CardContent>{children}</CardContent>
    </Card>
  )
}
