import { getBoxscore } from "@/lib/api";
import type { BattingLine, PitchingLine } from "@/lib/api";

export default async function GamePage(props: PageProps<"/games/[gameId]">) {
  const { gameId } = await props.params;
  const boxscore = await getBoxscore(Number(gameId));

  return (
    <main className="min-h-screen bg-background text-foreground px-6 py-10">
      <h1 className="text-2xl font-semibold mb-1">
        {boxscore.away.team.name} @ {boxscore.home.team.name}
      </h1>
      <p className="text-foreground/60 mb-8">{boxscore.game.official_date}</p>

      <div className="grid md:grid-cols-2 gap-6">
        <TeamBox label={boxscore.away.team.name} team={boxscore.away} />
        <TeamBox label={boxscore.home.team.name} team={boxscore.home} />
      </div>
    </main>
  );
}

function TeamBox({
  label,
  team,
}: {
  label: string;
  team: { batting: BattingLine[]; pitching: PitchingLine[] };
}) {
  return (
    <div className="rounded-lg border border-card-border bg-card p-4">
      <h2 className="font-semibold mb-3">{label}</h2>
      <table className="w-full text-sm mb-6">
        <thead className="text-foreground/60">
          <tr>
            <th className="text-left font-normal">Batter</th>
            <th className="text-right font-normal">AB</th>
            <th className="text-right font-normal">R</th>
            <th className="text-right font-normal">H</th>
            <th className="text-right font-normal">RBI</th>
          </tr>
        </thead>
        <tbody>
          {team.batting.map((b) => (
            <tr key={b.player_id} className="border-t border-card-border">
              <td className="py-1">
                {b.player_name} <span className="text-foreground/50">{b.position}</span>
              </td>
              <td className="text-right">{b.at_bats}</td>
              <td className="text-right">{b.runs}</td>
              <td className="text-right">{b.hits}</td>
              <td className="text-right">{b.rbi}</td>
            </tr>
          ))}
        </tbody>
      </table>

      <h3 className="text-sm text-foreground/60 mb-2">Pitching</h3>
      <table className="w-full text-sm">
        <thead className="text-foreground/60">
          <tr>
            <th className="text-left font-normal">Pitcher</th>
            <th className="text-right font-normal">IP</th>
            <th className="text-right font-normal">H</th>
            <th className="text-right font-normal">ER</th>
            <th className="text-right font-normal">K</th>
          </tr>
        </thead>
        <tbody>
          {team.pitching.map((p) => (
            <tr key={p.player_id} className="border-t border-card-border">
              <td className="py-1">{p.player_name}</td>
              <td className="text-right">{p.innings_pitched}</td>
              <td className="text-right">{p.hits}</td>
              <td className="text-right">{p.earned_runs}</td>
              <td className="text-right">{p.strike_outs}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
