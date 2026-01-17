import { useEffect, useMemo, useState } from "react";
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  LineChart,
  Line,
} from "recharts";

// serializer repr
export type PortfolioSnapshotPoint = {
  portfolio: number;
  ts: string;
  cash_balance: string;
  equity_value: string;
  total_value: string;
  unrealized_pl: string;
  unrealized_pl_pct: string;
  realized_pl: string;
  realized_pl_pct: string;
};

type RangeCode = "1D" | "1W" | "1M" | "3M" | "1Y";
type IntervalCode = "10m" | "1h" | "1d";

type Props = {
  portfolioId: number;
  token?: string;
  title?: string;
  subtitle?: string;
};

// parse number from string/number/null/undefined
function parseNum(v: string | number | null | undefined): number {
  if (typeof v === "number") return v;
  if (!v) return 0;
  const n = Number(v);
  return Number.isFinite(n) ? n : 0;
}

// format number as currency
function formatMoney(n: number, currency = "USD") {
  try {
    return new Intl.NumberFormat(undefined, {
      style: "currency",
      currency,
      maximumFractionDigits: 2,
    }).format(n);
  } catch {
    return `$${n.toFixed(2)}`;
  }
}

// format percentage with sign
function formatPct(n: number) {
  const sign = n > 0 ? "+" : "";
  return `${sign}${n.toFixed(2)}%`;
}

// subtract range from date
function subtractRange(now: Date, range: RangeCode): Date {
  const d = new Date(now);
  if (range === "1D") d.setDate(d.getDate() - 1);
  if (range === "1W") d.setDate(d.getDate() - 7);
  if (range === "1M") d.setDate(d.getDate() - 30);
  if (range === "3M") d.setDate(d.getDate() - 90);
  if (range === "1Y") d.setDate(d.getDate() - 365);
  return d;
}

// get bucket size in ms
function bucketMs(interval: IntervalCode): number {
  if (interval === "10m") return 10 * 60 * 1000;
  if (interval === "1h") return 60 * 60 * 1000;
  return 24 * 60 * 60 * 1000;
}

// floor timestamp to bucket
function floorToBucket(tsIso: string, bucketSizeMs: number): string {
  const t = new Date(tsIso).getTime();
  if (!Number.isFinite(t)) return tsIso;
  const floored = t - (t % bucketSizeMs);
  return new Date(floored).toISOString();
}

// format timestamp label based on interval
function formatTsLabel(iso: string, interval: IntervalCode) {
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return iso;

  if (interval === "1d") {
    return d.toLocaleDateString(undefined, { month: "short", day: "2-digit" });
  }

  // 10m / 1h
  return d.toLocaleString(undefined, {
    month: "short",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
}

type ChartPoint = {
  ts: string;
  label: string;
  cash: number;
  equity: number;
  total: number;
  unrealized: number;
};

// aggregate points into larger intervals
function aggregatePoints(points: ChartPoint[], interval: IntervalCode): ChartPoint[] {
  if (interval === "10m") return points;
  if (!points.length) return [];

  const ms = bucketMs(interval);
  const buckets = new Map<string, ChartPoint[]>();

  for (const p of points) {
    const key = floorToBucket(p.ts, ms);
    const arr = buckets.get(key) ?? [];
    arr.push(p);
    buckets.set(key, arr);
  }

  const out: ChartPoint[] = [];

  const sortedKeys = [...buckets.keys()].sort(
    (a, b) => new Date(a).getTime() - new Date(b).getTime()
  );

  for (const key of sortedKeys) {
    const arr = buckets.get(key)!;
    arr.sort((a, b) => new Date(a.ts).getTime() - new Date(b.ts).getTime());

    const last = arr[arr.length - 1];

    out.push({
      ts: key,
      label: formatTsLabel(key, interval),
      cash: last.cash,
      equity: last.equity,
      total: last.total,
      unrealized: last.unrealized,
    });
  }

  return out;
}

// tooltip component
const ChartTooltip = ({ active, payload, label }: any) => {
  if (!active || !payload?.length) return null;

  return (
    <div
      style={{
        background: "rgba(2, 6, 23, 0.95)",
        border: "1px solid #1f2937",
        padding: "0.6rem 0.75rem",
        borderRadius: "0.6rem",
        color: "#f9fafb",
        minWidth: 220,
      }}
    >
      <div style={{ fontSize: "0.9rem", color: "#e5e7eb", marginBottom: 6 }}>
        {label}
      </div>
      {payload.map((p: any) => (
        <div
          key={p.dataKey}
          style={{
            display: "flex",
            justifyContent: "space-between",
            gap: 12,
            fontSize: "0.9rem",
            color: "#d1d5db",
            marginTop: 2,
          }}
        >
          <span>{p.name}</span>
          <span style={{ fontWeight: 700, color: "#f9fafb" }}>
            {typeof p.value === "number" ? formatMoney(p.value) : String(p.value)}
          </span>
        </div>
      ))}
    </div>
  );
};


export default function PortfolioPerformancePanel({
  portfolioId,
  token,
  title = "Portfolio Performance",
  subtitle = "Total value, allocation and unrealized P/L",
}: Props) {
  const [range, setRange] = useState<RangeCode>("1W");
  const [interval, setInterval] = useState<IntervalCode>("10m");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [raw, setRaw] = useState<PortfolioSnapshotPoint[]>([]);

  // Fetch snapshots
  useEffect(() => {
    if (!portfolioId) return;

    const controller = new AbortController();

    async function load() {
      setLoading(true);
      setError(null);

      try {
        const now = new Date();
        const from = subtractRange(now, range);

        const url =
          `api/users/snapshots/?portfolio=${portfolioId}` +
          `&from=${encodeURIComponent(from.toISOString())}` +
          `&to=${encodeURIComponent(now.toISOString())}` +
          `&order=asc&limit=5000`;

        const res = await fetch(url, {
          method: "GET",
          signal: controller.signal,
          headers: {
            "Content-Type": "application/json",
            ...(token ? { Authorization: `Bearer ${token}` } : {}),
          },
          credentials: "include",
        });

        if (!res.ok) {
          const txt = await res.text();
          throw new Error(`HTTP ${res.status} ${txt}`);
        }

        const points: PortfolioSnapshotPoint[] = await res.json();
        setRaw(Array.isArray(points) ? points : []);
      } catch (e: any) {
        if (e?.name !== "AbortError") {
          setError(e?.message || "Failed to load portfolio data.");
        }
      } finally {
        setLoading(false);
      }
    }

    load();
    return () => controller.abort();
  }, [portfolioId, token, range]);

  // Base points sorted by timestamp
  const basePoints: ChartPoint[] = useMemo(() => {
    return raw
      .slice()
      .sort((a, b) => new Date(a.ts).getTime() - new Date(b.ts).getTime())
      .map((p) => ({
        ts: p.ts,
        label: formatTsLabel(p.ts, "10m"),
        cash: parseNum(p.cash_balance),
        equity: parseNum(p.equity_value),
        total: parseNum(p.total_value),
        unrealized: parseNum(p.unrealized_pl),
      }));
  }, [raw]);

  // Aggregate based on selected interval
  const data: ChartPoint[] = useMemo(() => {
    const aggregated = aggregatePoints(basePoints, interval);
    return aggregated.map((p) => ({
      ...p,
      label: formatTsLabel(p.ts, interval),
    }));
  }, [basePoints, interval]);

  const latest = data.length ? data[data.length - 1] : null;

  // Compute metrics
  const metrics = useMemo(() => {
    if (!data.length) return null;

    const first = data[0].total;
    const last = data[data.length - 1].total;

    let peak = first;
    let maxDrawdownPct = 0;

    for (const pt of data) {
      if (pt.total > peak) peak = pt.total;
      const dd = peak > 0 ? ((pt.total - peak) / peak) * 100 : 0;
      if (dd < maxDrawdownPct) maxDrawdownPct = dd;
    }

    const retPct = first > 0 ? ((last - first) / first) * 100 : 0;

    return {
      start: first,
      end: last,
      returnPct: retPct,
      maxDrawdownPct,
    };
  }, [data]);

  return (
    <div className={`stock-panel ${!data.length && !loading ? "empty" : ""}`}>
      <div className="stock-panel-header">
        <div>
          <div className="stock-name">{title}</div>
          <div className="stock-sub">{subtitle}</div>
        </div>

        <div className="stock-actions">
          <select
            className="btn"
            style={{ background: "#0f172a", color: "#f9fafb" }}
            value={range}
            onChange={(e) => setRange(e.target.value as RangeCode)}
            aria-label="Range"
          >
            <option value="1D">1D</option>
            <option value="1W">1W</option>
            <option value="1M">1M</option>
            <option value="3M">3M</option>
            <option value="1Y">1Y</option>
          </select>

          <select
            className="btn"
            style={{ background: "#0f172a", color: "#f9fafb" }}
            value={interval}
            onChange={(e) => setInterval(e.target.value as IntervalCode)}
            aria-label="Interval"
          >
            <option value="10m">10m</option>
            <option value="1h">1h</option>
            <option value="1d">1d</option>
          </select>
        </div>
      </div>

      {loading ? (
        <div className="chart-placeholder">
          <div className="chart-title">Loading...</div>
          <div className="chart-body" />
        </div>
      ) : error ? (
        <div className="stock-panel empty">
          <div>
            <div style={{ fontWeight: 700, marginBottom: 6 }}>Error</div>
            <div style={{ color: "#9ca3af", fontSize: "0.95rem" }}>{error}</div>
          </div>
        </div>
      ) : !data.length ? (
        <div className="stock-panel empty">No portfolio snapshots for this range.</div>
      ) : (
        <div className="stock-panel-main">
          {/* LEFT: Charts */}
          <div className="stock-main-left">
            {/* Equity curve */}
            <div className="chart-placeholder">
              <div className="chart-title">Total Value</div>
              <div className="chart-body">
                <ResponsiveContainer width="100%" height={280}>
                  <LineChart data={data}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
                    <XAxis dataKey="label" tick={{ fill: "#9ca3af", fontSize: 12 }} minTickGap={18} />
                    <YAxis tick={{ fill: "#9ca3af", fontSize: 12 }} tickFormatter={(v) => formatMoney(v)} width={90} />
                    <Tooltip content={<ChartTooltip />} />
                    <Legend />
                    <Line
                      type="monotone"
                      dataKey="total"
                      name="Total"
                      stroke="#60a5fa"
                      strokeWidth={2}
                      dot={false}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Allocation */}
            <div className="chart-placeholder">
              <div className="chart-title">Allocation (Cash vs Equity)</div>
              <div className="chart-body">
                <ResponsiveContainer width="100%" height={280}>
                  <AreaChart data={data}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
                    <XAxis dataKey="label" tick={{ fill: "#9ca3af", fontSize: 12 }} minTickGap={18} />
                    <YAxis tick={{ fill: "#9ca3af", fontSize: 12 }} tickFormatter={(v) => formatMoney(v)} width={90} />
                    <Tooltip content={<ChartTooltip />} />
                    <Legend />
                    <Area
                      type="monotone"
                      dataKey="cash"
                      name="Cash"
                      stackId="1"
                      stroke="#22c55e"
                      fill="#22c55e"
                      fillOpacity={0.18}
                    />
                    <Area
                      type="monotone"
                      dataKey="equity"
                      name="Equity"
                      stackId="1"
                      stroke="#3b82f6"
                      fill="#3b82f6"
                      fillOpacity={0.18}
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Unrealized P/L */}
            <div className="chart-placeholder">
              <div className="chart-title">Unrealized P/L</div>
              <div className="chart-body">
                <ResponsiveContainer width="100%" height={260}>
                  <LineChart data={data}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
                    <XAxis dataKey="label" tick={{ fill: "#9ca3af", fontSize: 12 }} minTickGap={18} />
                    <YAxis tick={{ fill: "#9ca3af", fontSize: 12 }} tickFormatter={(v) => formatMoney(v)} width={90} />
                    <Tooltip content={<ChartTooltip />} />
                    <Legend />
                    <Line
                      type="monotone"
                      dataKey="unrealized"
                      name="Unrealized P/L"
                      stroke="#eab308"
                      strokeWidth={2}
                      dot={false}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>

          {/* RIGHT: Metrics */}
          <div className="stock-main-right">
            <div className="panel-section">
              <h3>Latest</h3>
              <ul className="simple-list">
                <li>
                  Total Value: <strong>{formatMoney(latest?.total ?? 0)}</strong>
                </li>
                <li>
                  Cash: <strong>{formatMoney(latest?.cash ?? 0)}</strong>
                </li>
                <li>
                  Equity: <strong>{formatMoney(latest?.equity ?? 0)}</strong>
                </li>
                <li>
                  Unrealized P/L: <strong>{formatMoney(latest?.unrealized ?? 0)}</strong>
                </li>
              </ul>
            </div>

            <div className="panel-section">
              <h3>Performance</h3>
              <ul className="simple-list">
                <li>
                  Start: <strong>{formatMoney(metrics?.start ?? 0)}</strong>
                </li>
                <li>
                  End: <strong>{formatMoney(metrics?.end ?? 0)}</strong>
                </li>
                <li>
                  Return: <strong>{formatPct(metrics?.returnPct ?? 0)}</strong>
                </li>
                <li>
                  Max Drawdown: <strong>{formatPct(metrics?.maxDrawdownPct ?? 0)}</strong>
                </li>
              </ul>
            </div>

            <div className="panel-section">
              <h3>Data</h3>
              <ul className="simple-list">
                <li>
                  Range: <strong>{range}</strong>
                </li>
                <li>
                  Interval: <strong>{interval}</strong>
                </li>
                <li>
                  Points: <strong>{data.length}</strong>
                </li>
              </ul>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
