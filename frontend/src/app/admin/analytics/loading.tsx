import { Loader2 } from 'lucide-react';

export default function AnalyticsLoading() {
  return (
    <div className="flex h-64 items-center justify-center">
      <div className="text-center">
        <Loader2 className="mx-auto h-8 w-8 animate-spin text-primary" />
        <p className="mt-2 text-sm text-muted-foreground">Loading analytics...</p>
      </div>
    </div>
  );
}








