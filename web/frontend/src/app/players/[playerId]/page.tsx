import {
  getPlayerBattingStats,
  getPlayerPitchingStats,
  getTeams,
} from "@/lib/api";
import type {
  SeasonBattingStats,
  SeasonPitchingStats,
  CareerBattingStats,
  CareerPitchingStats,
} from "@/lib/api";
import { Card } from "@/components/Card";
import { TeamBadge } from "@/components/TeamBadge";
import { StatTable, type StatColumn } from "@/components/StatTable";

function formatAvg(value: number | null): string {
  if (value === null) return "-";
  return value.toFixed(3).replace(/^0/, "");
}

function formatDecimal(value: number | null, digits = 2): string {
  if (value === null) return "-";
  return value.toFixed(digits);
}

export default async function PlayerPage(props: PageProps<"/players/[playerId]">) {
  const { playerId } = await props.params;
  const id = Number(playerId);

  const [battingStats, pitchingStats, teams] = await Promise.all([
    getPlayerBattingStats(id),
    getPlayerPitchingStats(id),
    getTeams(),
  ]);

  const teamAbbrev = new Map(teams.map((t) => [t.id, t.abbreviation]));
  const player = battingStats.player;
  const hasBatting = battingStats.seasons.length > 0 || battingStats.career !== null;
  const hasPitching = pitchingStats.seasons.length > 0 || pitchingStats.career !== null;

  const battingColumns: StatColumn<SeasonBattingStats>[] = [
    { key: "season", label: "Year", render: (s) => s.season },
    {
      key: "team",
      label: "Team",
      render: (s) =>
        s.team_id !== null ? (
          <TeamBadge teamId={s.team_id} abbreviation={teamAbbrev.get(s.team_id) ?? "?"} size="sm" />
        ) : (
          <span className="text-foreground/40 text-xs">Multiple</span>
        ),
    },
    { key: "g", label: "G", align: "right", render: (s) => s.games_played },
    { key: "ab", label: "AB", align: "right", render: (s) => s.at_bats },
    { key: "r", label: "R", align: "right", render: (s) => s.runs },
    { key: "h", label: "H", align: "right", render: (s) => s.hits },
    { key: "hr", label: "HR", align: "right", render: (s) => s.home_runs },
    { key: "rbi", label: "RBI", align: "right", render: (s) => s.rbi },
    { key: "sb", label: "SB", align: "right", render: (s) => s.stolen_bases },
    { key: "avg", label: "AVG", align: "right", render: (s) => formatAvg(s.avg) },
    { key: "obp", label: "OBP", align: "right", render: (s) => formatAvg(s.obp) },
    { key: "slg", label: "SLG", align: "right", render: (s) => formatAvg(s.slg) },
    { key: "ops", label: "OPS", align: "right", render: (s) => formatAvg(s.ops) },
  ];

  const pitchingColumns: StatColumn<SeasonPitchingStats>[] = [
    { key: "season", label: "Year", render: (s) => s.season },
    {
      key: "team",
      label: "Team",
      render: (s) =>
        s.team_id !== null ? (
          <TeamBadge teamId={s.team_id} abbreviation={teamAbbrev.get(s.team_id) ?? "?"} size="sm" />
        ) : (
          <span className="text-foreground/40 text-xs">Multiple</span>
        ),
    },
    { key: "g", label: "G", align: "right", render: (s) => s.games_played },
    { key: "gs", label: "GS", align: "right", render: (s) => s.games_started },
    { key: "wl", label: "W-L", align: "right", render: (s) => `${s.wins}-${s.losses}` },
    { key: "sv", label: "SV", align: "right", render: (s) => s.saves },
    { key: "ip", label: "IP", align: "right", render: (s) => s.innings_pitched },
    { key: "so", label: "SO", align: "right", render: (s) => s.strike_outs },
    { key: "era", label: "ERA", align: "right", render: (s) => formatDecimal(s.era) },
    { key: "whip", label: "WHIP", align: "right", render: (s) => formatDecimal(s.whip) },
  ];

  return (
    <main className="flex-1 max-w-5xl w-full mx-auto px-6 py-10">
      <h1 className="text-2xl font-semibold mb-8">{player.full_name}</h1>

      {hasBatting && (
        <section className="mb-8">
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-sm uppercase tracking-wide text-foreground/50">Batting</h2>
            {battingStats.career && (
              <CareerLine label="Career" stats={battingStats.career} />
            )}
          </div>
          <Card className="p-4 overflow-x-auto">
            <StatTable columns={battingColumns} rows={battingStats.seasons} rowKey={(s) => `${s.season}-${s.team_id}`} />
          </Card>
          {battingStats.postseason.length > 0 && (
            <>
              <h3 className="text-xs uppercase tracking-wide text-foreground/50 mt-4 mb-2">Postseason</h3>
              <Card className="p-4 overflow-x-auto">
                <StatTable
                  columns={battingColumns}
                  rows={battingStats.postseason}
                  rowKey={(s) => `post-${s.season}-${s.team_id}`}
                />
              </Card>
            </>
          )}
        </section>
      )}

      {hasPitching && (
        <section>
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-sm uppercase tracking-wide text-foreground/50">Pitching</h2>
            {pitchingStats.career && (
              <PitchingCareerLine label="Career" stats={pitchingStats.career} />
            )}
          </div>
          <Card className="p-4 overflow-x-auto">
            <StatTable columns={pitchingColumns} rows={pitchingStats.seasons} rowKey={(s) => `${s.season}-${s.team_id}`} />
          </Card>
          {pitchingStats.postseason.length > 0 && (
            <>
              <h3 className="text-xs uppercase tracking-wide text-foreground/50 mt-4 mb-2">Postseason</h3>
              <Card className="p-4 overflow-x-auto">
                <StatTable
                  columns={pitchingColumns}
                  rows={pitchingStats.postseason}
                  rowKey={(s) => `post-${s.season}-${s.team_id}`}
                />
              </Card>
            </>
          )}
        </section>
      )}
    </main>
  );
}

function CareerLine({ label, stats }: { label: string; stats: CareerBattingStats }) {
  return (
    <div className="text-sm text-foreground/70">
      {label}: <span className="font-mono font-semibold text-foreground">{formatAvg(stats.avg)}</span>
      {" / "}
      <span className="font-mono font-semibold text-foreground">{formatAvg(stats.obp)}</span>
      {" / "}
      <span className="font-mono font-semibold text-foreground">{formatAvg(stats.slg)}</span>
      {"  ·  "}
      <span className="font-mono font-semibold text-foreground">{stats.home_runs}</span> HR
      {"  ·  "}
      <span className="font-mono font-semibold text-foreground">{stats.rbi}</span> RBI
    </div>
  );
}

function PitchingCareerLine({ label, stats }: { label: string; stats: CareerPitchingStats }) {
  return (
    <div className="text-sm text-foreground/70">
      {label}: <span className="font-mono font-semibold text-foreground">{stats.wins}-{stats.losses}</span>
      {"  ·  "}
      <span className="font-mono font-semibold text-foreground">{formatDecimal(stats.era)}</span> ERA
      {"  ·  "}
      <span className="font-mono font-semibold text-foreground">{stats.strike_outs}</span> SO
      {"  ·  "}
      <span className="font-mono font-semibold text-foreground">{formatDecimal(stats.whip)}</span> WHIP
    </div>
  );
}
