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
  type = 'bar' 
}: AnalyticsChartProps) {
  const maxValue = Math.max(...data.map(d => d.value));

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>{title}</CardTitle>
            {description && <CardDescription>{description}</CardDescription>}
          </div>
          <BarChart3 className="h-5 w-5 text-muted-foreground" />
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {data.map((point, index) => (
            <div key={index} className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span className="font-medium">{point.label}</span>
                <span className="text-muted-foreground">{point.value}</span>
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

