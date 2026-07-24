"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useRef, useState } from "react";

interface PlayerSummary {
  id: number;
  full_name: string;
  boxscore_name: string | null;
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export function Header() {
  const router = useRouter();
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<PlayerSummary[]>([]);
  const [open, setOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (query.trim().length < 2) {
      setResults([]);
      return;
    }
    const controller = new AbortController();
    const timeout = setTimeout(() => {
      fetch(`${API_BASE_URL}/players?q=${encodeURIComponent(query)}&limit=8`, {
        signal: controller.signal,
      })
        .then((res) => (res.ok ? res.json() : []))
        .then((data: PlayerSummary[]) => {
          setResults(data);
          setOpen(true);
        })
        .catch(() => {});
    }, 200);
    return () => {
      clearTimeout(timeout);
      controller.abort();
    };
  }, [query]);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  function goToPlayer(playerId: number) {
    setOpen(false);
    setQuery("");
    router.push(`/players/${playerId}`);
  }

  return (
    <header className="border-b border-card-border bg-card">
      <div className="max-w-5xl mx-auto px-6 py-4 flex items-center gap-8">
        <Link href="/" className="text-lg font-bold tracking-tight text-foreground shrink-0">
          Pitch<span className="text-primary">Frame</span>
        </Link>

        <nav className="flex items-center gap-5 text-sm text-foreground/70 shrink-0">
          <Link href="/" className="hover:text-foreground transition-colors">
            Games
          </Link>
          <Link href="/leaderboards" className="hover:text-foreground transition-colors">
            Leaderboards
          </Link>
        </nav>

        <div ref={containerRef} className="relative ml-auto w-full max-w-xs">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onFocus={() => results.length > 0 && setOpen(true)}
            placeholder="Search players..."
            className="w-full rounded-md border border-card-border bg-background px-3 py-1.5 text-sm text-foreground placeholder:text-foreground/40 focus:outline-none focus:border-primary transition-colors"
          />
          {open && results.length > 0 && (
            <div className="absolute right-0 mt-1 w-full rounded-md border border-card-border bg-card shadow-lg overflow-hidden z-10">
              {results.map((player) => (
                <button
                  key={player.id}
                  onClick={() => goToPlayer(player.id)}
                  className="w-full text-left px-3 py-2 text-sm hover:bg-primary/10 transition-colors"
                >
                  {player.full_name}
                </button>
              ))}
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
