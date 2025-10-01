import { DashboardLayout } from "@/components/dashboard/dashboard-layout"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Calendar, Clock, TrendingUp, Plus } from "lucide-react"

export default function SchedulerPage() {
  const scheduledPosts = [
    { id: 1, title: "Diwali Collection Launch", time: "2:00 PM", platform: "Instagram", status: "scheduled" },
    { id: 2, title: "Festival Sale Announcement", time: "6:00 PM", platform: "Facebook", status: "scheduled" },
    { id: 3, title: "New Arrivals Showcase", time: "10:00 AM", platform: "Twitter", status: "published" },
  ]

  const trendingTimes = [
    { time: "9:00 AM", engagement: "High", color: "bg-chart-1" },
    { time: "2:00 PM", engagement: "Medium", color: "bg-chart-2" },
    { time: "6:00 PM", engagement: "High", color: "bg-chart-1" },
    { time: "8:00 PM", engagement: "Peak", color: "bg-chart-3" },
  ]

  return (
    <DashboardLayout>
      <div className="space-y-8">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-foreground">Social Media Scheduler</h1>
            <p className="text-muted-foreground mt-1">
              Plan and schedule your textile marketing posts across platforms.
            </p>
          </div>
          <Button className="bg-textile-accent">
            <Plus className="mr-2 h-4 w-4" />
            Schedule Post
          </Button>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Calendar View */}
          <Card className="lg:col-span-2 textile-hover textile-shadow">
            <CardHeader>
              <CardTitle className="flex items-center">
                <Calendar className="mr-2 h-5 w-5 text-chart-1" />
                This Week's Schedule
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {scheduledPosts.map((post) => (
                  <div key={post.id} className="flex items-center justify-between p-4 border border-border rounded-lg">
                    <div className="flex items-center space-x-4">
                      <div className="w-10 h-10 bg-chart-1 rounded-lg flex items-center justify-center">
                        <Calendar className="h-5 w-5 text-white" />
                      </div>
                      <div>
                        <p className="font-medium text-foreground">{post.title}</p>
                        <p className="text-sm text-muted-foreground">{post.time} • {post.platform}</p>
                      </div>
                    </div>
                    <Badge variant={post.status === "published" ? "default" : "secondary"}>
                      {post.status}
                    </Badge>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Trending Times */}
          <Card className="textile-hover textile-shadow">
            <CardHeader>
              <CardTitle className="flex items-center">
                <TrendingUp className="mr-2 h-5 w-5 text-chart-2" />
                Best Times to Post
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {trendingTimes.map((item, index) => (
                  <div key={index} className="flex items-center justify-between p-3 rounded-lg bg-muted/50">
                    <div className="flex items-center space-x-3">
                      <div className={`w-3 h-3 rounded-full ${item.color}`}></div>
                      <span className="font-medium text-foreground">{item.time}</span>
                    </div>
                    <Badge variant="outline" className="text-xs">
                      {item.engagement}
                    </Badge>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Quick Schedule */}
        <Card className="textile-hover textile-shadow">
          <CardHeader>
            <CardTitle>Quick Schedule</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="aspect-square bg-muted rounded-lg flex items-center justify-center">
                <div className="text-center">
                  <div className="w-12 h-12 bg-chart-1 rounded-lg mx-auto mb-2"></div>
                  <p className="text-sm text-muted-foreground">Instagram Post</p>
                </div>
              </div>
              <div className="aspect-square bg-muted rounded-lg flex items-center justify-center">
                <div className="text-center">
                  <div className="w-12 h-12 bg-chart-2 rounded-lg mx-auto mb-2"></div>
                  <p className="text-sm text-muted-foreground">Facebook Story</p>
                </div>
              </div>
              <div className="aspect-square bg-muted rounded-lg flex items-center justify-center">
                <div className="text-center">
                  <div className="w-12 h-12 bg-chart-3 rounded-lg mx-auto mb-2"></div>
                  <p className="text-sm text-muted-foreground">Twitter Thread</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  )
}
