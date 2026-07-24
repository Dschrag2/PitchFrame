import { getTeamColor } from "@/lib/team-colors";

export function TeamBadge({
  teamId,
  abbreviation,
  size = "md",
}: {
  teamId: number;
  abbreviation: string;
  size?: "sm" | "md";
}) {
  const color = getTeamColor(teamId);
  const sizeClasses = size === "sm" ? "text-xs px-1.5 py-0.5" : "text-sm px-2 py-1";

  return (
    <span
      className={`inline-flex items-center justify-center rounded font-mono font-semibold text-white ${sizeClasses}`}
      style={{ backgroundColor: color }}
    >
      {abbreviation}
    </span>
  );
}
