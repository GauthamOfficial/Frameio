import { DashboardLayout } from "@/components/dashboard/dashboard-layout"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Search, Filter, Edit, Download, Eye } from "lucide-react"
import { Input } from "@/components/ui/input"

export default function TemplatesPage() {
  const templates = [
    { id: 1, name: "Diwali Festival", category: "Festival", color: "Deep Navy & Gold", preview: "bg-chart-1" },
    { id: 2, name: "Wedding Collection", category: "Wedding", color: "Maroon & Cream", preview: "bg-chart-2" },
    { id: 3, name: "Summer Collection", category: "Seasonal", color: "Pastel Blue", preview: "bg-chart-3" },
    { id: 4, name: "Traditional Saree", category: "Traditional", color: "Beige & Sage", preview: "bg-chart-4" },
    { id: 5, name: "Modern Kurta", category: "Modern", color: "Navy & White", preview: "bg-chart-1" },
    { id: 6, name: "Festival Sale", category: "Sale", color: "Red & Gold", preview: "bg-chart-2" },
  ]

  const categories = ["All", "Festival", "Wedding", "Seasonal", "Traditional", "Modern", "Sale"]

  return (
    <DashboardLayout>
      <div className="space-y-8">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-foreground">Templates Library</h1>
            <p className="text-muted-foreground mt-1">
              Choose from pre-designed textile festival and event templates.
            </p>
          </div>
        </div>

        {/* Search and Filters */}
        <Card className="textile-hover textile-shadow">
          <CardContent className="p-6">
            <div className="flex flex-col md:flex-row gap-4">
              <div className="flex-1">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                  <Input
                    placeholder="Search templates..."
                    className="pl-10"
                  />
                </div>
              </div>
              <div className="flex gap-2">
                {categories.map((category) => (
                  <Button
                    key={category}
                    variant={category === "All" ? "default" : "outline"}
                    size="sm"
                  >
                    {category}
                  </Button>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Templates Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {templates.map((template) => (
            <Card key={template.id} className="textile-hover textile-shadow">
              <CardContent className="p-0">
                <div className="aspect-[4/3] bg-muted rounded-t-lg flex items-center justify-center">
                  <div className="text-center">
                    <div className={`w-16 h-16 ${template.preview} rounded-lg mx-auto mb-2`}></div>
                    <p className="text-xs text-muted-foreground">Template Preview</p>
                  </div>
                </div>
                <div className="p-4">
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="font-semibold text-foreground">{template.name}</h3>
                    <Badge variant="outline" className="text-xs">
                      {template.category}
                    </Badge>
                  </div>
                  <p className="text-sm text-muted-foreground mb-4">{template.color}</p>
                  <div className="flex gap-2">
                    <Button size="sm" variant="outline" className="flex-1">
                      <Eye className="mr-1 h-3 w-3" />
                      Preview
                    </Button>
                    <Button size="sm" variant="outline" className="flex-1">
                      <Edit className="mr-1 h-3 w-3" />
                      Edit
                    </Button>
                    <Button size="sm" variant="outline" className="flex-1">
                      <Download className="mr-1 h-3 w-3" />
                      Use
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Featured Templates */}
        <Card className="textile-hover textile-shadow">
          <CardHeader>
            <CardTitle>Featured Templates</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="flex items-center space-x-4 p-4 border border-border rounded-lg">
                <div className="w-16 h-16 bg-chart-1 rounded-lg flex items-center justify-center">
                  <div className="text-center">
                    <div className="w-8 h-8 bg-white rounded"></div>
                  </div>
                </div>
                <div className="flex-1">
                  <h4 className="font-semibold text-foreground">Festival Collection 2024</h4>
                  <p className="text-sm text-muted-foreground">Complete set of Diwali templates</p>
                  <Badge variant="secondary" className="mt-1">Popular</Badge>
                </div>
                <Button size="sm">Use Template</Button>
              </div>
              <div className="flex items-center space-x-4 p-4 border border-border rounded-lg">
                <div className="w-16 h-16 bg-chart-2 rounded-lg flex items-center justify-center">
                  <div className="text-center">
                    <div className="w-8 h-8 bg-white rounded"></div>
                  </div>
                </div>
                <div className="flex-1">
                  <h4 className="font-semibold text-foreground">Wedding Season</h4>
                  <p className="text-sm text-muted-foreground">Elegant bridal collection templates</p>
                  <Badge variant="secondary" className="mt-1">New</Badge>
                </div>
                <Button size="sm">Use Template</Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  )
}

