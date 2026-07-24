import type { ReactNode } from "react";

export interface StatColumn<T> {
  key: string;
  label: string;
  align?: "left" | "right";
  render: (row: T) => ReactNode;
}

export function StatTable<T>({
  columns,
  rows,
  rowKey,
}: {
  columns: StatColumn<T>[];
  rows: T[];
  rowKey: (row: T) => string | number;
}) {
  return (
    <table className="w-full text-sm">
      <thead>
        <tr className="text-foreground/50 text-xs uppercase tracking-wide">
          {columns.map((col) => (
            <th
              key={col.key}
              className={`font-medium py-2 ${col.align === "right" ? "text-right" : "text-left"}`}
            >
              {col.label}
            </th>
          ))}
        </tr>
      </thead>
      <tbody>
        {rows.map((row) => (
          <tr key={rowKey(row)} className="border-t border-card-border">
            {columns.map((col) => (
              <td
                key={col.key}
                className={`py-2 ${col.align === "right" ? "text-right font-mono tabular-nums" : "text-left"}`}
              >
                {col.render(row)}
              </td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  );
}
