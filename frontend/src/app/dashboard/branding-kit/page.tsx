import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Download, RefreshCw, Palette, Type, Image } from "lucide-react"

export default function BrandingKitPage() {
  const colorPalettes = [
    { name: "Primary Palette", colors: ["#1B2951", "#8B2635", "#F5F1EB", "#B8D4E3"] },
    { name: "Festival Collection", colors: ["#8B2635", "#FFD700", "#F4E4D6", "#1B2951"] },
    { name: "Wedding Collection", colors: ["#F5F1EB", "#D4C4B0", "#8B2635", "#E6D7F0"] },
  ]

  const logos = [
    { name: "Main Logo", type: "Primary", format: "PNG" },
    { name: "Icon Only", type: "Icon", format: "SVG" },
    { name: "Text Logo", type: "Text", format: "PNG" },
  ]

  const banners = [
    { name: "Shop Banner", size: "1200x300", platform: "Website" },
    { name: "Social Cover", size: "1200x630", platform: "Facebook" },
    { name: "Story Template", size: "1080x1920", platform: "Instagram" },
  ]

  return (
    <div className="space-y-8">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-foreground">Branding Kit</h1>
            <p className="text-muted-foreground mt-1">
              Auto-generated logos, color palettes, and shop banners for your textile brand.
            </p>
          </div>
          <Button className="bg-textile-accent">
            <RefreshCw className="mr-2 h-4 w-4" />
            Regenerate All
          </Button>
        </div>

        {/* Color Palettes */}
        <Card className="textile-hover textile-shadow">
          <CardHeader>
            <CardTitle className="flex items-center">
              <Palette className="mr-2 h-5 w-5 text-chart-1" />
              Color Palettes
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {colorPalettes.map((palette, index) => (
                <div key={index} className="space-y-3">
                  <h4 className="font-semibold text-foreground">{palette.name}</h4>
                  <div className="flex space-x-2">
                    {palette.colors.map((color, colorIndex) => (
                      <div
                        key={colorIndex}
                        className="w-12 h-12 rounded-lg border border-border"
                        style={{ backgroundColor: color }}
                      ></div>
                    ))}
                  </div>
                  <div className="flex gap-2">
                    <Button size="sm" variant="outline" className="flex-1">
                      <Download className="mr-1 h-3 w-3" />
                      Download
                    </Button>
                    <Button size="sm" variant="outline" className="flex-1">
                      <RefreshCw className="mr-1 h-3 w-3" />
                      Regenerate
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Logos */}
        <Card className="textile-hover textile-shadow">
          <CardHeader>
            <CardTitle className="flex items-center">
              <Type className="mr-2 h-5 w-5 text-chart-2" />
              Logo Variations
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {logos.map((logo, index) => (
                <div key={index} className="space-y-3">
                  <div className="aspect-square bg-muted rounded-lg flex items-center justify-center">
                    <div className="text-center">
                      <div className="w-16 h-16 bg-chart-1 rounded-lg mx-auto mb-2 flex items-center justify-center">
                        <span className="text-white font-bold text-lg">F</span>
                      </div>
                      <p className="text-xs text-muted-foreground">Logo Preview</p>
                    </div>
                  </div>
                  <div>
                    <h4 className="font-semibold text-foreground">{logo.name}</h4>
                    <p className="text-sm text-muted-foreground">{logo.type} • {logo.format}</p>
                  </div>
                  <div className="flex gap-2">
                    <Button size="sm" variant="outline" className="flex-1">
                      <Download className="mr-1 h-3 w-3" />
                      Download
                    </Button>
                    <Button size="sm" variant="outline" className="flex-1">
                      <RefreshCw className="mr-1 h-3 w-3" />
                      Regenerate
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Banners */}
        <Card className="textile-hover textile-shadow">
          <CardHeader>
            <CardTitle className="flex items-center">
              <Image className="mr-2 h-5 w-5 text-chart-3" />
              Shop Banners
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {banners.map((banner, index) => (
                <div key={index} className="space-y-3">
                  <div className="aspect-video bg-muted rounded-lg flex items-center justify-center">
                    <div className="text-center">
                      <div className="w-20 h-8 bg-chart-1 rounded mx-auto mb-2"></div>
                      <p className="text-xs text-muted-foreground">Banner Preview</p>
                    </div>
                  </div>
                  <div>
                    <h4 className="font-semibold text-foreground">{banner.name}</h4>
                    <p className="text-sm text-muted-foreground">{banner.size} • {banner.platform}</p>
                  </div>
                  <div className="flex gap-2">
                    <Button size="sm" variant="outline" className="flex-1">
                      <Download className="mr-1 h-3 w-3" />
                      Download
                    </Button>
                    <Button size="sm" variant="outline" className="flex-1">
                      <RefreshCw className="mr-1 h-3 w-3" />
                      Regenerate
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Brand Guidelines */}
        <Card className="textile-hover textile-shadow">
          <CardHeader>
            <CardTitle>Brand Guidelines</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-4">
                <h4 className="font-semibold text-foreground">Typography</h4>
                <div className="space-y-2">
                  <p className="text-lg font-bold text-foreground">Heading Font: Inter Bold</p>
                  <p className="text-base font-medium text-foreground">Subheading: Inter Medium</p>
                  <p className="text-sm text-muted-foreground">Body: Inter Regular</p>
                </div>
              </div>
              <div className="space-y-4">
                <h4 className="font-semibold text-foreground">Usage Guidelines</h4>
                <div className="space-y-2 text-sm text-muted-foreground">
                  <p>• Maintain minimum clear space around logos</p>
                  <p>• Use primary colors for main elements</p>
                  <p>• Keep consistent spacing and alignment</p>
                  <p>• Ensure accessibility compliance</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
  )
}
