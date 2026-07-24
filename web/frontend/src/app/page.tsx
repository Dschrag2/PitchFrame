import Link from "next/link";
import { getGames } from "@/lib/api";

export default async function HomePage() {
  const games = await getGames({ season: 2025, limit: 20 });

  return (
    <main className="min-h-screen bg-background text-foreground px-6 py-10">
      <h1 className="text-2xl font-semibold mb-6">PitchFrame</h1>
      <div className="grid gap-3 max-w-2xl">
        {games.map((game) => (
          <Link
            key={game.id}
            href={`/games/${game.id}`}
            className="flex items-center justify-between rounded-lg border border-card-border bg-card px-4 py-3 hover:border-primary transition-colors"
          >
            <div className="flex items-center gap-3">
              <span className="text-sm text-foreground/60">{game.official_date}</span>
              <span>
                {game.away_team.abbreviation} @ {game.home_team.abbreviation}
              </span>
            </div>
            <div className="font-mono text-sm">
              {game.away_score ?? "-"} : {game.home_score ?? "-"}
            </div>
          </Link>
        ))}
      </div>
    </main>
  );
}
