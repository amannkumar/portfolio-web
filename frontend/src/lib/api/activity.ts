import { apiGet } from "./client";
import type { ActivityResponse } from "@/types/activity";

export function fetchActivity(range: "1y" | "30d" | "90d" = "1y") {
  return apiGet<ActivityResponse>(`/api/activity?range=${range}`);
}
