import Link from "next/link";
import { getGames } from "@/lib/api";
import { Card } from "@/components/Card";
import { TeamBadge } from "@/components/TeamBadge";

export default async function HomePage() {
  const games = await getGames({ season: 2025, limit: 20 });

  return (
    <main className="flex-1 max-w-5xl w-full mx-auto px-6 py-10">
      <h1 className="text-2xl font-semibold mb-1">2025 Season</h1>
      <p className="text-foreground/50 text-sm mb-6">Recent games</p>

      <div className="grid gap-3">
        {games.map((game) => (
          <Link key={game.id} href={`/games/${game.id}`}>
            <Card className="flex items-center justify-between px-5 py-4 hover:border-primary transition-colors">
              <div className="flex items-center gap-4">
                <span className="text-xs text-foreground/50 font-mono w-24 shrink-0">
                  {game.official_date}
                </span>
                <div className="flex items-center gap-2">
                  <TeamBadge teamId={game.away_team.id} abbreviation={game.away_team.abbreviation} />
                  <span className="text-foreground/40 text-sm">@</span>
                  <TeamBadge teamId={game.home_team.id} abbreviation={game.home_team.abbreviation} />
                </div>
              </div>
              <div className="font-mono text-lg font-semibold tabular-nums">
                {game.away_score ?? "-"}
                <span className="text-foreground/30 mx-1.5">:</span>
                {game.home_score ?? "-"}
              </div>
            </Card>
          </Link>
        ))}
      </div>
    </main>
  );
}
