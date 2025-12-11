'use client';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { BarChart3 } from 'lucide-react';

interface DataPoint {
  label: string;
  value: number;
}

interface AnalyticsChartProps {
  title: string;
  description?: string;
  data: DataPoint[];
  type?: 'bar' | 'line';
}

export function AnalyticsChart({ 
  title, 
  description, 
  data,
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  type = 'bar' 
}: AnalyticsChartProps) {
  const maxValue = Math.max(...data.map(d => d.value));

  return (
    <Card>
      <CardHeader className="px-4 sm:px-6 pt-6">
        <div className="flex items-center justify-between">
          <div className="flex-1 min-w-0">
            <CardTitle className="text-lg sm:text-xl truncate">{title}</CardTitle>
            {description && <CardDescription className="text-sm truncate">{description}</CardDescription>}
          </div>
          <BarChart3 className="h-4 w-4 sm:h-5 sm:w-5 text-muted-foreground flex-shrink-0 ml-2" />
        </div>
      </CardHeader>
      <CardContent className="px-4 sm:px-6 pb-6">
        <div className="space-y-4">
          {data.map((point, index) => (
            <div key={index} className="space-y-2">
              <div className="flex items-center justify-between text-xs sm:text-sm gap-2">
                <span className="font-medium truncate flex-1 min-w-0">{point.label}</span>
                <span className="text-muted-foreground whitespace-nowrap flex-shrink-0">{point.value}</span>
              </div>
              <div className="h-2 w-full overflow-hidden rounded-full bg-gray-100">
                <div
                  className="h-full bg-primary transition-all"
                  style={{ width: `${(point.value / maxValue) * 100}%` }}
                />
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}









