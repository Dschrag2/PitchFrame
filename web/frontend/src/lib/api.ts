const API_BASE_URL = process.env.API_BASE_URL ?? "http://localhost:8000";

export interface TeamSummary {
  id: number;
  name: string;
  abbreviation: string;
}

export interface GameSummary {
  id: number;
  season: number;
  game_type: string;
  official_date: string;
  detailed_state: string;
  home_team: TeamSummary;
  away_team: TeamSummary;
  home_score: number | null;
  away_score: number | null;
}

export interface BattingLine {
  player_id: number;
  player_name: string;
  position: string;
  at_bats: number;
  runs: number;
  hits: number;
  doubles: number;
  triples: number;
  home_runs: number;
  rbi: number;
  base_on_balls: number;
  strike_outs: number;
  stolen_bases: number;
  summary: string | null;
}

export interface PitchingLine {
  player_id: number;
  player_name: string;
  innings_pitched: string;
  hits: number;
  runs: number;
  earned_runs: number;
  base_on_balls: number;
  strike_outs: number;
  home_runs: number;
  summary: string | null;
}

export interface TeamBoxscore {
  team: TeamSummary;
  batting: BattingLine[];
  pitching: PitchingLine[];
}

export interface GameBoxscore {
  game: GameSummary;
  home: TeamBoxscore;
  away: TeamBoxscore;
}

async function apiFetch<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE_URL}${path}`, { cache: "no-store" });
  if (!res.ok) {
    throw new Error(`API request failed: ${path} (${res.status})`);
  }
  return res.json() as Promise<T>;
}

export function getGames(
  params: { season?: number; teamId?: number; limit?: number } = {}
): Promise<GameSummary[]> {
  const query = new URLSearchParams();
  if (params.season) query.set("season", String(params.season));
  if (params.teamId) query.set("team_id", String(params.teamId));
  if (params.limit) query.set("limit", String(params.limit));
  return apiFetch(`/games?${query.toString()}`);
}

export function getBoxscore(gameId: number): Promise<GameBoxscore> {
  return apiFetch(`/games/${gameId}/boxscore`);
}
