export function Loading() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-background">
      <div className="text-center">
        <div className="w-8 h-8 bg-primary rounded-lg mx-auto mb-4 animate-pulse"></div>
        <p className="text-muted-foreground">Loading...</p>
      </div>
    </div>
  )
}
