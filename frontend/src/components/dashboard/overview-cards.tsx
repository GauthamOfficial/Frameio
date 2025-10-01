import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { TrendingUp, Calendar, Heart, BookOpen } from "lucide-react"
import { cn } from "@/lib/utils"

const overviewData = [
  {
    title: "Generated Posts",
    value: "24",
    change: "+12%",
    trend: "up",
    icon: TrendingUp,
    color: "text-chart-1"
  },
  {
    title: "Scheduled Posts",
    value: "8",
    change: "+3",
    trend: "up",
    icon: Calendar,
    color: "text-chart-2"
  },
  {
    title: "Engagement Rate",
    value: "4.2%",
    change: "+0.8%",
    trend: "up",
    icon: Heart,
    color: "text-chart-3"
  },
  {
    title: "Catalogs Created",
    value: "12",
    change: "+5",
    trend: "up",
    icon: BookOpen,
    color: "text-chart-4"
  }
]

export function OverviewCards() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      {overviewData.map((item) => {
        const Icon = item.icon
        return (
          <Card key={item.title} className="textile-hover textile-shadow">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                {item.title}
              </CardTitle>
              <Icon className={`h-4 w-4 ${item.color}`} />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-foreground">{item.value}</div>
              <p className="text-xs text-muted-foreground mt-1">
                <span className="text-green-600">{item.change}</span> from last month
              </p>
            </CardContent>
          </Card>
        )
      })}
    </div>
  )
}

