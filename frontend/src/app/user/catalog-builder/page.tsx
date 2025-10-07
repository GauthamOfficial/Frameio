import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"

export default function CatalogBuilderPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Catalog Builder</h1>
        <p className="text-muted-foreground">
          Build and manage your product catalogs.
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Catalog Builder</CardTitle>
          <CardDescription>
            Create and manage your product catalogs
          </CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground">
            This feature is coming soon. You&apos;ll be able to build and manage catalogs here.
          </p>
        </CardContent>
      </Card>
    </div>
  )
}
