import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Upload, Wand2, Calendar, Share2, Download } from "lucide-react"

export default function PosterGeneratorPage() {
  return (
    <div className="space-y-8">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-foreground">AI Poster Generator</h1>
            <p className="text-muted-foreground mt-1">
              Create stunning textile marketing posters with AI assistance.
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Upload Section */}
          <Card className="textile-hover textile-shadow">
            <CardHeader>
              <CardTitle>Upload & Configure</CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* File Upload */}
              <div className="space-y-2">
                <Label htmlFor="upload">Upload Images</Label>
                <div className="border-2 border-dashed border-border rounded-lg p-8 text-center hover:border-accent transition-colors">
                  <Upload className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
                  <p className="text-sm text-muted-foreground mb-2">
                    Drag and drop your textile images here, or click to browse
                  </p>
                  <Button variant="outline" size="sm">
                    Choose Files
                  </Button>
                </div>
              </div>

              {/* Prompt Input */}
              <div className="space-y-2">
                <Label htmlFor="prompt">AI Prompt</Label>
                <Textarea
                  id="prompt"
                  placeholder="Describe the style, colors, and mood for your poster..."
                  className="min-h-[100px]"
                />
              </div>

              {/* Style Options */}
              <div className="space-y-2">
                <Label>Style</Label>
                <div className="grid grid-cols-2 gap-2">
                  <Button variant="outline" size="sm">Festival</Button>
                  <Button variant="outline" size="sm">Modern</Button>
                  <Button variant="outline" size="sm">Traditional</Button>
                  <Button variant="outline" size="sm">Minimalist</Button>
                </div>
              </div>

              {/* Generate Button */}
              <Button className="w-full bg-textile-accent">
                <Wand2 className="mr-2 h-4 w-4" />
                Generate Poster
              </Button>
            </CardContent>
          </Card>

          {/* Preview Section */}
          <Card className="textile-hover textile-shadow">
            <CardHeader>
              <CardTitle>Preview</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="aspect-[4/5] bg-muted rounded-lg flex items-center justify-center mb-4">
                <div className="text-center">
                  <Upload className="mx-auto h-16 w-16 text-muted-foreground mb-4" />
                  <p className="text-muted-foreground">Generated poster will appear here</p>
                </div>
              </div>
              
              {/* Action Buttons */}
              <div className="grid grid-cols-2 gap-3">
                <Button variant="outline" className="w-full">
                  <Calendar className="mr-2 h-4 w-4" />
                  Schedule
                </Button>
                <Button variant="outline" className="w-full">
                  <Share2 className="mr-2 h-4 w-4" />
                  Post Now
                </Button>
              </div>
              
              <Button variant="outline" className="w-full mt-3">
                <Download className="mr-2 h-4 w-4" />
                Download
              </Button>
            </CardContent>
          </Card>
        </div>

        {/* Recent Generations */}
        <Card className="textile-hover textile-shadow">
          <CardHeader>
            <CardTitle>Recent Generations</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {[1, 2, 3, 4].map((i) => (
                <div key={i} className="aspect-square bg-muted rounded-lg flex items-center justify-center">
                  <Upload className="h-8 w-8 text-muted-foreground" />
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
  )
}
