import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"

export default function PosterGeneratorPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">AI Poster Generator</h1>
        <p className="text-muted-foreground">
          Create stunning posters with AI-powered design tools.
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Poster Generator</CardTitle>
          <CardDescription>
            Generate beautiful posters using AI technology
          </CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground">
            This feature is coming soon. You'll be able to create AI-generated posters here.
          </p>
        </CardContent>
      </Card>
    </div>
  )
}
