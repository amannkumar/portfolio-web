export type ActivityDay = {
  date: string; // YYYY-MM-DD
  total: number;
  leetcode?: number;
  github?: number;
};

export type ActivityResponse = {
  range: "1y" | "30d" | "90d";
  days: ActivityDay[];
};
