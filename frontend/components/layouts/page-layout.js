'use client'
const PageLayout = ({ children, pageTitle, subTitle, action: Action, ...props }) => {
  return (
    <main className="flex-1 p-6" {...props}>
      <div className="max-w-7xl mx-auto space-y-4">
        <div className="flex items-center justify-between mb-15">
          <h1 className="text-2xl font-semibold tracking-tight">
            {pageTitle ?? ''}
            {subTitle && <span className="text-muted-foreground ml-2">{`: ${subTitle}`}</span>}
          </h1>
          {!!Action && Action}
        </div>

        <div className="grid grid-cols-1 gap-6 ">
          <div>{children}</div>
        </div>
      </div>
    </main>
  )
}

export default PageLayout
