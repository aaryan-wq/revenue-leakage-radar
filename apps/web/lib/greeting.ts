export type TimeOfDay = "morning" | "afternoon" | "evening";

export function getTimeOfDay(hour: number = new Date().getHours()): TimeOfDay {
  if (hour >= 5 && hour < 12) return "morning";
  if (hour >= 12 && hour < 17) return "afternoon";
  return "evening";
}

export function formatGreeting(name: string, hour?: number): string {
  const timeOfDay = getTimeOfDay(hour);
  const label = timeOfDay.charAt(0).toUpperCase() + timeOfDay.slice(1);
  return `Good ${label}, ${name}`;
}
