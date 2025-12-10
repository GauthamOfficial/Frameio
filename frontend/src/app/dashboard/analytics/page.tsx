import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { TrendingUp, Users, Heart, Share2, Download, Calendar } from "lucide-react"

export default function AnalyticsPage() {
  const metrics = [
    { title: "Total Reach", value: "12.4K", change: "+8.2%", icon: Users, color: "text-chart-1" },
    { title: "Engagement Rate", value: "4.2%", change: "+1.1%", icon: Heart, color: "text-chart-2" },
    { title: "Shares", value: "342", change: "+23%", icon: Share2, color: "text-chart-3" },
    { title: "Downloads", value: "1.2K", change: "+15%", icon: Download, color: "text-chart-4" },
  ]

  const topPosts = [
    { title: "Diwali Collection Launch", reach: "2.4K", engagement: "8.2%", platform: "Instagram" },
    { title: "Festival Sale Announcement", reach: "1.8K", engagement: "6.1%", platform: "Facebook" },
    { title: "New Arrivals Showcase", reach: "1.2K", engagement: "5.3%", platform: "Twitter" },
  ]

  return (
    <div className="space-y-8">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-foreground">Analytics</h1>
            <p className="text-muted-foreground mt-1">
              Track your social media performance and engagement metrics.
            </p>
          </div>
          <div className="flex gap-2">
            <Button variant="outline">
              <Calendar className="mr-2 h-4 w-4" />
              Last 30 Days
            </Button>
            <Button className="bg-textile-accent">
              <Download className="mr-2 h-4 w-4" />
              Export Report
            </Button>
          </div>
        </div>

        {/* Metrics Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {metrics.map((metric) => {
            const Icon = metric.icon
            return (
              <Card key={metric.title} className="textile-hover textile-shadow">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground">
                    {metric.title}
                  </CardTitle>
                  <Icon className={`h-4 w-4 ${metric.color}`} />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-foreground">{metric.value}</div>
                  <p className="text-xs text-muted-foreground mt-1">
                    <span className="text-green-600">{metric.change}</span> from last month
                  </p>
                </CardContent>
              </Card>
            )
          })}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Engagement Chart */}
          <Card className="textile-hover textile-shadow">
            <CardHeader>
              <CardTitle className="flex items-center">
                <TrendingUp className="mr-2 h-5 w-5 text-chart-1" />
                Engagement Over Time
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-64 bg-muted/50 rounded-lg flex items-center justify-center">
                <div className="text-center">
                  <TrendingUp className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
                  <p className="text-muted-foreground">Chart visualization would go here</p>
                  <p className="text-sm text-muted-foreground">Integration with Chart.js or Recharts</p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Platform Performance */}
          <Card className="textile-hover textile-shadow">
            <CardHeader>
              <CardTitle>Platform Performance</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center justify-between p-3 rounded-lg bg-muted/50">
                  <div className="flex items-center space-x-3">
                    <div className="w-8 h-8 bg-chart-1 rounded-lg flex items-center justify-center">
                      <span className="text-white text-xs font-bold">IG</span>
                    </div>
                    <div>
                      <p className="font-medium text-foreground">Instagram</p>
                      <p className="text-sm text-muted-foreground">8.2K reach</p>
                    </div>
                  </div>
                  <Badge variant="secondary">Best</Badge>
                </div>
                <div className="flex items-center justify-between p-3 rounded-lg bg-muted/50">
                  <div className="flex items-center space-x-3">
                    <div className="w-8 h-8 bg-chart-2 rounded-lg flex items-center justify-center">
                      <span className="text-white text-xs font-bold">FB</span>
                    </div>
                    <div>
                      <p className="font-medium text-foreground">Facebook</p>
                      <p className="text-sm text-muted-foreground">3.1K reach</p>
                    </div>
                  </div>
                  <Badge variant="outline">Good</Badge>
                </div>
                <div className="flex items-center justify-between p-3 rounded-lg bg-muted/50">
                  <div className="flex items-center space-x-3">
                    <div className="w-8 h-8 bg-chart-3 rounded-lg flex items-center justify-center">
                      <span className="text-white text-xs font-bold">TW</span>
                    </div>
                    <div>
                      <p className="font-medium text-foreground">Twitter</p>
                      <p className="text-sm text-muted-foreground">1.1K reach</p>
                    </div>
                  </div>
                  <Badge variant="outline">Growing</Badge>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Top Performing Posts */}
        <Card className="textile-hover textile-shadow">
          <CardHeader>
            <CardTitle>Top Performing Posts</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {topPosts.map((post, index) => (
                <div key={index} className="flex items-center justify-between p-4 border border-border rounded-lg">
                  <div className="flex items-center space-x-4">
                    <div className="w-10 h-10 bg-chart-1 rounded-lg flex items-center justify-center">
                      <span className="text-white font-bold">{index + 1}</span>
                    </div>
                    <div>
                      <p className="font-medium text-foreground">{post.title}</p>
                      <p className="text-sm text-muted-foreground">{post.platform}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="font-medium text-foreground">{post.reach}</p>
                    <p className="text-sm text-muted-foreground">{post.engagement} engagement</p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
  )
}
