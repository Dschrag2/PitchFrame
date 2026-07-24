// Primary MLB team colors, keyed by the real team ids from our database
// (see `teams` table). Used as accent fills for badges/headers — chosen for
// visual distinctiveness against the app's dark background, not a strict
// 1:1 match to every team's full brand guideline.
export const TEAM_COLORS: Record<number, string> = {
  108: "#BA0021", // LAA Angels
  109: "#A71930", // AZ Diamondbacks
  110: "#DF4601", // BAL Orioles
  111: "#BD3039", // BOS Red Sox
  112: "#0E3386", // CHC Cubs
  113: "#C6011F", // CIN Reds
  114: "#00385D", // CLE Guardians
  115: "#33006F", // COL Rockies
  116: "#0C2340", // DET Tigers
  117: "#002D62", // HOU Astros
  118: "#004687", // KC Royals
  119: "#005A9C", // LAD Dodgers
  120: "#AB0003", // WSH Nationals
  121: "#002D72", // NYM Mets
  133: "#003831", // ATH Athletics
  134: "#FDB827", // PIT Pirates
  135: "#2F241D", // SD Padres
  136: "#0C2C56", // SEA Mariners
  137: "#FD5A1E", // SF Giants
  138: "#C41E3A", // STL Cardinals
  139: "#092C5C", // TB Rays
  140: "#003278", // TEX Rangers
  141: "#134A8E", // TOR Blue Jays
  142: "#002B5C", // MIN Twins
  143: "#E81828", // PHI Phillies
  144: "#CE1141", // ATL Braves
  145: "#C4CED4", // CWS White Sox
  146: "#00A3E0", // MIA Marlins
  147: "#003087", // NYY Yankees
  158: "#FFC52F", // MIL Brewers
};

const DEFAULT_COLOR = "#6b7280";

export function getTeamColor(teamId: number): string {
  return TEAM_COLORS[teamId] ?? DEFAULT_COLOR;
}
