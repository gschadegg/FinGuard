'use client'
const PageLayout = ({ children, pageTitle }) => {
  return (
    <main className="flex-1 p-6">
      <div className="max-w-7xl mx-auto space-y-4">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-semibold tracking-tight">{pageTitle ?? ''}</h1>
          <div className="flex items-center gap-2" />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-[1fr_300px] gap-6">
          <div>{children}</div>
          {/* <aside className="hidden lg:block border-l pl-6">
            <div className="text-sm text-muted-foreground">
              Right gutter — add filters, notes, tips, or secondary content here.
            </div>
          </aside> */}
        </div>
      </div>
    </main>
  )
}

export default PageLayout
