import { useQuery } from "@tanstack/react-query";
import { fetchActivity } from "@/lib/api/activity";

export function useActivity(range: "1y" | "30d" | "90d" = "1y") {
  return useQuery({
    queryKey: ["activity", range],
    queryFn: () => fetchActivity(range),
    staleTime: 1000 * 60 * 10, // 10 minutes
    retry: 1,
  });
}
