import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { 
  Image, 
  BookOpen, 
  Palette, 
  Share2, 
  Calendar,
  BarChart3,
  Library
} from "lucide-react"
import Link from "next/link"

export function UserOverview() {
  const userFeatures = [
    {
      title: "AI Poster Generator",
      description: "Create stunning posters with AI-powered design tools",
      icon: Image,
      href: "/user/poster-generator",
      color: "bg-blue-500"
    },
    {
      title: "Catalog Builder",
      description: "Build and manage your product catalogs",
      icon: BookOpen,
      href: "/user/catalog-builder",
      color: "bg-green-500"
    },
    {
      title: "Branding Kit",
      description: "Create and manage your brand identity",
      icon: Palette,
      href: "/user/branding-kit",
      color: "bg-purple-500"
    },
    {
      title: "Social Media Posts",
      description: "Generate and schedule social media content",
      icon: Share2,
      href: "/user/social-media",
      color: "bg-pink-500"
    },
    {
      title: "Scheduler",
      description: "Schedule your posts and campaigns",
      icon: Calendar,
      href: "/user/scheduler",
      color: "bg-orange-500"
    },
    {
      title: "Templates Library",
      description: "Access pre-designed templates",
      icon: Library,
      href: "/user/templates",
      color: "bg-indigo-500"
    },
    {
      title: "Analytics",
      description: "Track your performance and insights",
      icon: BarChart3,
      href: "/user/analytics",
      color: "bg-teal-500"
    }
  ]

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">User Dashboard</h1>
        <p className="text-muted-foreground">
          Welcome to your personal workspace. Create, manage, and track your content.
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {userFeatures.map((feature) => {
          const Icon = feature.icon
          return (
            <Card key={feature.title} className="hover:shadow-lg transition-shadow">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">
                  {feature.title}
                </CardTitle>
                <div className={`p-2 rounded-lg ${feature.color}`}>
                  <Icon className="h-4 w-4 text-white" />
                </div>
              </CardHeader>
              <CardContent>
                <CardDescription className="mb-4">
                  {feature.description}
                </CardDescription>
                <Button asChild className="w-full">
                  <Link href={feature.href}>
                    Open {feature.title}
                  </Link>
                </Button>
              </CardContent>
            </Card>
          )
        })}
      </div>
    </div>
  )
}
