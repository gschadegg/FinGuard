'use client'
const PageLayout = ({ children, pageTitle, action: Action }) => {
  return (
    <main className="flex-1 p-6">
      <div className="max-w-7xl mx-auto space-y-4">
        <div className="flex items-center justify-between mb-15">
          <h1 className="text-2xl font-semibold tracking-tight">{pageTitle ?? ''}</h1>
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
