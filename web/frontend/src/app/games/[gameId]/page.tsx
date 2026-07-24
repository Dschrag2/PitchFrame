import Link from "next/link";
import { getBoxscore } from "@/lib/api";
import type { BattingLine, PitchingLine, TeamSummary } from "@/lib/api";
import { Card } from "@/components/Card";
import { TeamBadge } from "@/components/TeamBadge";
import { StatTable, type StatColumn } from "@/components/StatTable";

export default async function GamePage(props: PageProps<"/games/[gameId]">) {
  const { gameId } = await props.params;
  const boxscore = await getBoxscore(Number(gameId));

  return (
    <main className="flex-1 max-w-5xl w-full mx-auto px-6 py-10">
      <div className="flex items-center gap-3 mb-1">
        <TeamBadge teamId={boxscore.away.team.id} abbreviation={boxscore.away.team.abbreviation} size="sm" />
        <h1 className="text-2xl font-semibold">
          {boxscore.away.team.name} @ {boxscore.home.team.name}
        </h1>
        <TeamBadge teamId={boxscore.home.team.id} abbreviation={boxscore.home.team.abbreviation} size="sm" />
      </div>
      <p className="text-foreground/50 text-sm mb-8">{boxscore.game.official_date}</p>

      <div className="grid lg:grid-cols-2 gap-6">
        <TeamBox team={boxscore.away.team} batting={boxscore.away.batting} pitching={boxscore.away.pitching} />
        <TeamBox team={boxscore.home.team} batting={boxscore.home.batting} pitching={boxscore.home.pitching} />
      </div>
    </main>
  );
}

const battingColumns: StatColumn<BattingLine>[] = [
  {
    key: "player",
    label: "Batter",
    render: (b) => (
      <Link href={`/players/${b.player_id}`} className="hover:text-primary transition-colors">
        {b.player_name} <span className="text-foreground/40">{b.position}</span>
      </Link>
    ),
  },
  { key: "ab", label: "AB", align: "right", render: (b) => b.at_bats },
  { key: "r", label: "R", align: "right", render: (b) => b.runs },
  { key: "h", label: "H", align: "right", render: (b) => b.hits },
  { key: "rbi", label: "RBI", align: "right", render: (b) => b.rbi },
  { key: "bb", label: "BB", align: "right", render: (b) => b.base_on_balls },
  { key: "so", label: "SO", align: "right", render: (b) => b.strike_outs },
];

const pitchingColumns: StatColumn<PitchingLine>[] = [
  {
    key: "player",
    label: "Pitcher",
    render: (p) => (
      <Link href={`/players/${p.player_id}`} className="hover:text-primary transition-colors">
        {p.player_name}
      </Link>
    ),
  },
  { key: "ip", label: "IP", align: "right", render: (p) => p.innings_pitched },
  { key: "h", label: "H", align: "right", render: (p) => p.hits },
  { key: "er", label: "ER", align: "right", render: (p) => p.earned_runs },
  { key: "bb", label: "BB", align: "right", render: (p) => p.base_on_balls },
  { key: "so", label: "SO", align: "right", render: (p) => p.strike_outs },
];

function TeamBox({
  team,
  batting,
  pitching,
}: {
  team: TeamSummary;
  batting: BattingLine[];
  pitching: PitchingLine[];
}) {
  return (
    <Card className="p-5">
      <div className="flex items-center gap-2 mb-4">
        <TeamBadge teamId={team.id} abbreviation={team.abbreviation} size="sm" />
        <h2 className="font-semibold">{team.name}</h2>
      </div>

      <StatTable columns={battingColumns} rows={batting} rowKey={(b) => b.player_id} />

      <h3 className="text-xs uppercase tracking-wide text-foreground/50 mt-6 mb-1">Pitching</h3>
      <StatTable columns={pitchingColumns} rows={pitching} rowKey={(p) => p.player_id} />
    </Card>
  );
}
