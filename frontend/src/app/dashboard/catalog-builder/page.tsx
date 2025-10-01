import { DashboardLayout } from "@/components/dashboard/dashboard-layout"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Plus, Palette, Download, Eye } from "lucide-react"

export default function CatalogBuilderPage() {
  const products = [
    { id: 1, name: "Silk Saree Collection", color: "Deep Navy", pattern: "Floral", price: "$299" },
    { id: 2, name: "Cotton Kurta Set", color: "Maroon", pattern: "Geometric", price: "$149" },
    { id: 3, name: "Linen Dress", color: "Beige", pattern: "Striped", price: "$199" },
    { id: 4, name: "Chiffon Scarf", color: "Pastel Blue", pattern: "Abstract", price: "$79" },
  ]

  return (
    <DashboardLayout>
      <div className="space-y-8">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-foreground">Catalog Builder</h1>
            <p className="text-muted-foreground mt-1">
              Create beautiful product catalogs with AI-powered color matching.
            </p>
          </div>
          <Button className="bg-textile-accent">
            <Plus className="mr-2 h-4 w-4" />
            New Catalog
          </Button>
        </div>

        {/* AI Suggestions */}
        <Card className="textile-hover textile-shadow">
          <CardHeader>
            <CardTitle className="flex items-center">
              <Palette className="mr-2 h-5 w-5 text-chart-2" />
              AI Color Suggestions
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-2">
              <Badge variant="secondary" className="bg-chart-1 text-white">Deep Navy + Gold</Badge>
              <Badge variant="secondary" className="bg-chart-2 text-white">Maroon + Cream</Badge>
              <Badge variant="secondary" className="bg-chart-3 text-white">Beige + Sage</Badge>
              <Badge variant="secondary" className="bg-chart-4 text-white">Pastel + Navy</Badge>
            </div>
          </CardContent>
        </Card>

        {/* Product Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {products.map((product) => (
            <Card key={product.id} className="textile-hover textile-shadow">
              <CardContent className="p-0">
                <div className="aspect-square bg-muted rounded-t-lg flex items-center justify-center">
                  <div className="text-center">
                    <div className="w-16 h-16 bg-chart-1 rounded-lg mx-auto mb-2"></div>
                    <p className="text-xs text-muted-foreground">Product Image</p>
                  </div>
                </div>
                <div className="p-4">
                  <h3 className="font-semibold text-foreground mb-2">{product.name}</h3>
                  <div className="space-y-1 text-sm text-muted-foreground">
                    <p>Color: {product.color}</p>
                    <p>Pattern: {product.pattern}</p>
                    <p className="font-medium text-foreground">{product.price}</p>
                  </div>
                  <div className="flex gap-2 mt-3">
                    <Button size="sm" variant="outline" className="flex-1">
                      <Eye className="mr-1 h-3 w-3" />
                      View
                    </Button>
                    <Button size="sm" variant="outline" className="flex-1">
                      <Download className="mr-1 h-3 w-3" />
                      Add
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Template Selection */}
        <Card className="textile-hover textile-shadow">
          <CardHeader>
            <CardTitle>Catalog Templates</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="aspect-[4/3] bg-muted rounded-lg flex items-center justify-center">
                <div className="text-center">
                  <div className="w-12 h-12 bg-chart-1 rounded-lg mx-auto mb-2"></div>
                  <p className="text-sm text-muted-foreground">Festival Collection</p>
                </div>
              </div>
              <div className="aspect-[4/3] bg-muted rounded-lg flex items-center justify-center">
                <div className="text-center">
                  <div className="w-12 h-12 bg-chart-2 rounded-lg mx-auto mb-2"></div>
                  <p className="text-sm text-muted-foreground">Wedding Collection</p>
                </div>
              </div>
              <div className="aspect-[4/3] bg-muted rounded-lg flex items-center justify-center">
                <div className="text-center">
                  <div className="w-12 h-12 bg-chart-3 rounded-lg mx-auto mb-2"></div>
                  <p className="text-sm text-muted-foreground">Casual Wear</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  )
}
