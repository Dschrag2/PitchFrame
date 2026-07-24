const API_BASE_URL = process.env.API_BASE_URL ?? "http://localhost:8000";

export interface TeamSummary {
  id: number;
  name: string;
  abbreviation: string;
}

export interface PlayerSummary {
  id: number;
  full_name: string;
  boxscore_name: string | null;
}

export interface TeamDetail {
  id: number;
  name: string;
  team_name: string;
  location_name: string | null;
  abbreviation: string;
  league_name: string | null;
  division_name: string | null;
  first_year_of_play: string | null;
  active: boolean;
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

export interface SeasonBattingStats {
  season: number;
  team_id: number | null;
  games_played: number;
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
  avg: number | null;
  obp: number | null;
  slg: number | null;
  ops: number | null;
}

export interface CareerBattingStats {
  games_played: number;
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
  avg: number | null;
  obp: number | null;
  slg: number | null;
  ops: number | null;
}

export interface BattingStatsResponse {
  player: PlayerSummary;
  seasons: SeasonBattingStats[];
  postseason: SeasonBattingStats[];
  career: CareerBattingStats | null;
}

export interface SeasonPitchingStats {
  season: number;
  team_id: number | null;
  games_played: number;
  games_started: number;
  wins: number;
  losses: number;
  saves: number;
  innings_pitched: string;
  hits: number;
  earned_runs: number;
  base_on_balls: number;
  strike_outs: number;
  era: number | null;
  whip: number | null;
  k_per_9: number | null;
  bb_per_9: number | null;
}

export interface CareerPitchingStats {
  games_played: number;
  games_started: number;
  wins: number;
  losses: number;
  saves: number;
  innings_pitched: string;
  hits: number;
  earned_runs: number;
  base_on_balls: number;
  strike_outs: number;
  era: number | null;
  whip: number | null;
  k_per_9: number | null;
  bb_per_9: number | null;
}

export interface PitchingStatsResponse {
  player: PlayerSummary;
  seasons: SeasonPitchingStats[];
  postseason: SeasonPitchingStats[];
  career: CareerPitchingStats | null;
}

export interface LeaderboardEntry {
  rank: number;
  player: PlayerSummary;
  value: number;
  games_played: number;
}

export interface RosterBatter {
  player: PlayerSummary;
  games_played: number;
  at_bats: number;
  hits: number;
  home_runs: number;
  rbi: number;
  avg: number | null;
  ops: number | null;
}

export interface RosterPitcher {
  player: PlayerSummary;
  games_played: number;
  games_started: number;
  wins: number;
  losses: number;
  saves: number;
  strike_outs: number;
  era: number | null;
  whip: number | null;
}

export interface TeamRoster {
  team: TeamDetail;
  season: number;
  batters: RosterBatter[];
  pitchers: RosterPitcher[];
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

export function searchPlayers(q: string, limit = 10): Promise<PlayerSummary[]> {
  const query = new URLSearchParams({ q, limit: String(limit) });
  return apiFetch(`/players?${query.toString()}`);
}

export function getPlayer(playerId: number): Promise<PlayerSummary> {
  return apiFetch(`/players/${playerId}`);
}

export function getPlayerBattingStats(playerId: number): Promise<BattingStatsResponse> {
  return apiFetch(`/players/${playerId}/batting-stats`);
}

export function getPlayerPitchingStats(playerId: number): Promise<PitchingStatsResponse> {
  return apiFetch(`/players/${playerId}/pitching-stats`);
}

export function getTeams(): Promise<TeamDetail[]> {
  return apiFetch(`/teams`);
}

export function getTeam(teamId: number): Promise<TeamDetail> {
  return apiFetch(`/teams/${teamId}`);
}

export function getTeamRoster(teamId: number, season: number): Promise<TeamRoster> {
  const query = new URLSearchParams({ season: String(season) });
  return apiFetch(`/teams/${teamId}/roster?${query.toString()}`);
}

export function getBattingLeaderboard(params: {
  season: number;
  stat: string;
  limit?: number;
  minAtBats?: number;
}): Promise<LeaderboardEntry[]> {
  const query = new URLSearchParams({ season: String(params.season), stat: params.stat });
  if (params.limit) query.set("limit", String(params.limit));
  if (params.minAtBats) query.set("min_at_bats", String(params.minAtBats));
  return apiFetch(`/leaderboards/batting?${query.toString()}`);
}

export function getPitchingLeaderboard(params: {
  season: number;
  stat: string;
  limit?: number;
  minOuts?: number;
}): Promise<LeaderboardEntry[]> {
  const query = new URLSearchParams({ season: String(params.season), stat: params.stat });
  if (params.limit) query.set("limit", String(params.limit));
  if (params.minOuts) query.set("min_outs", String(params.minOuts));
  return apiFetch(`/leaderboards/pitching?${query.toString()}`);
}
