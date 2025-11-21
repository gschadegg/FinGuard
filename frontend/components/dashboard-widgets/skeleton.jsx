import { Skeleton } from '@/components/ui/skeleton'

export function DashboardSkeleton() {
  return (
    <div className="p-8 space-y-8 w-full" data-testid="dashboard-skeleton">
      <div className="flex items-center gap-4">
        <Skeleton className="h-8 w-48" />
        <Skeleton className="h-6 w-24" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* left col */}
        <div className="space-y-4">
          <div className="p-6 border rounded-lg space-y-4">
            <div className="flex items-center justify-between">
              <Skeleton className="h-5 w-32" />
              <Skeleton className="h-5 w-5 rounded-full" />
            </div>
            <Skeleton className="h-10 w-40" />
          </div>

          <div className="p-6 border rounded-lg space-y-4">
            <div className="flex items-center justify-between">
              <Skeleton className="h-5 w-40" />
              <Skeleton className="h-5 w-5 rounded-full" />
            </div>
            <Skeleton className="h-10 w-40" />
          </div>

          <div className="p-6 border rounded-lg space-y-4">
            <div className="flex items-center justify-between">
              <Skeleton className="h-5 w-44" />
              <Skeleton className="h-5 w-5 rounded-full" />
            </div>
            <div className="flex justify-between">
              <div className="space-y-2">
                <Skeleton className="h-3 w-16" />
                <Skeleton className="h-4 w-20" />
              </div>
              <div className="space-y-2">
                <Skeleton className="h-3 w-16" />
                <Skeleton className="h-4 w-20" />
              </div>
              <div className="space-y-2">
                <Skeleton className="h-3 w-16" />
                <Skeleton className="h-4 w-20" />
              </div>
            </div>
            <Skeleton className="h-3 w-full rounded-full" />
          </div>
        </div>

        {/* right col */}
        <div className="p-6 border rounded-lg space-y-4">
          <div className="flex items-center justify-between">
            <Skeleton className="h-5 w-48" />
          </div>

          <div className="flex items-center justify-center py-4">
            <Skeleton className="h-48 w-48 rounded-full" />
          </div>

          <div className="space-y-2">
            {[1, 2, 3, 4, 5].map((i) => (
              <div key={i} className="flex justify-between items-center">
                <div className="flex items-center gap-2">
                  <Skeleton className="h-3 w-3 rounded-full" />
                  <Skeleton className="h-4 w-32" />
                </div>
                <Skeleton className="h-4 w-16" />
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* accounts */}
      <div className="border rounded-lg p-6 space-y-4">
        <div className="flex justify-between items-center">
          <Skeleton className="h-5 w-32" />
          <Skeleton className="h-5 w-16" />
        </div>

        {[1, 2].map((i) => (
          <div key={i} className="flex justify-between items-center p-4 border rounded-lg">
            <div className="space-y-2">
              <Skeleton className="h-4 w-40" />
              <Skeleton className="h-3 w-24" />
            </div>
            <div className="space-y-2 text-right">
              <Skeleton className="h-4 w-24" />
              <Skeleton className="h-4 w-24" />
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
