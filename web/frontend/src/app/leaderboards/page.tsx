import Link from "next/link";
import { getBattingLeaderboard, getPitchingLeaderboard } from "@/lib/api";
import { Card } from "@/components/Card";

const SEASON = 2025;

const BATTING_STATS = [
  { key: "home_runs", label: "Home Runs" },
  { key: "avg", label: "Batting Avg" },
  { key: "ops", label: "OPS" },
  { key: "rbi", label: "RBI" },
  { key: "hits", label: "Hits" },
  { key: "stolen_bases", label: "Stolen Bases" },
];

const PITCHING_STATS = [
  { key: "era", label: "ERA" },
  { key: "strike_outs", label: "Strikeouts" },
  { key: "wins", label: "Wins" },
  { key: "saves", label: "Saves" },
  { key: "whip", label: "WHIP" },
];

const DECIMAL_STATS = new Set(["avg", "ops", "era", "whip"]);

function formatValue(stat: string, value: number): string {
  if (!DECIMAL_STATS.has(stat)) return String(Math.round(value));
  if (stat === "avg") return value.toFixed(3).replace(/^0/, "");
  return value.toFixed(2);
}

export default async function LeaderboardsPage(props: PageProps<"/leaderboards">) {
  const searchParams = await props.searchParams;
  const type = searchParams.type === "pitching" ? "pitching" : "batting";
  const statOptions = type === "batting" ? BATTING_STATS : PITCHING_STATS;
  const requestedStat = typeof searchParams.stat === "string" ? searchParams.stat : undefined;
  const stat = statOptions.some((s) => s.key === requestedStat) ? requestedStat! : statOptions[0].key;

  const entries =
    type === "batting"
      ? await getBattingLeaderboard({ season: SEASON, stat, limit: 15 })
      : await getPitchingLeaderboard({ season: SEASON, stat, limit: 15 });

  return (
    <main className="flex-1 max-w-3xl w-full mx-auto px-6 py-10">
      <h1 className="text-2xl font-semibold mb-1">Leaderboards</h1>
      <p className="text-foreground/50 text-sm mb-6">{SEASON} season</p>

      <div className="flex gap-2 mb-4">
        {(["batting", "pitching"] as const).map((t) => (
          <Link
            key={t}
            href={`/leaderboards?type=${t}`}
            className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
              type === t
                ? "bg-primary text-white"
                : "bg-card border border-card-border text-foreground/70 hover:text-foreground"
            }`}
          >
            {t === "batting" ? "Batting" : "Pitching"}
          </Link>
        ))}
      </div>

      <div className="flex flex-wrap gap-2 mb-6">
        {statOptions.map((s) => (
          <Link
            key={s.key}
            href={`/leaderboards?type=${type}&stat=${s.key}`}
            className={`px-2.5 py-1 rounded text-xs font-medium transition-colors ${
              stat === s.key
                ? "bg-primary/20 text-primary border border-primary/40"
                : "text-foreground/60 border border-card-border hover:text-foreground"
            }`}
          >
            {s.label}
          </Link>
        ))}
      </div>

      <Card className="p-2">
        {entries.map((entry) => (
          <Link
            key={entry.player.id}
            href={`/players/${entry.player.id}`}
            className="flex items-center justify-between px-3 py-2.5 rounded-md hover:bg-primary/10 transition-colors"
          >
            <div className="flex items-center gap-3">
              <span className="text-foreground/40 font-mono text-sm w-5 text-right">{entry.rank}</span>
              <span className="text-sm">{entry.player.full_name}</span>
            </div>
            <span className="font-mono font-semibold tabular-nums">{formatValue(stat, entry.value)}</span>
          </Link>
        ))}
      </Card>
    </main>
  );
}
