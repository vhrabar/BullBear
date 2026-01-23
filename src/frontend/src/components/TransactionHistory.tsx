import { useEffect, useMemo, useState } from "react";
import "../styles/TransactionHistory.css";

type OrderSide = "BUY" | "SELL";
type OrderType = "MARKET" | "LIMIT" | "STOP" | "STOP_LIMIT";
type OrderStatus = "OPEN" | "PARTIALLY_FILLED" | "FILLED" | "CANCELLED" | "REJECTED";

interface OrderFill {
  id: number;
  quantity: string;
  price: string;
  executed_at: string;
  fee?: string;
}

export interface Order {
  id: number;
  instrument: number;
  instrument_display: string;
  side: OrderSide;
  order_type: OrderType;
  time_in_force: string;
  quantity: string;
  filled_quantity: string;
  avg_fill_price: string | null;
  status: OrderStatus;
  placed_at: string;
  fills: OrderFill[];
  reject_reason?: string;
}

function parseSymbol(display: string): string {
  return display?.split(" ")[0]?.trim()?.toUpperCase() ?? "";
}

function fmtNum(x: string | number | null | undefined, decimals = 2): string {
  if (x === null || x === undefined) return "—";
  const n = typeof x === "number" ? x : Number(x);
  if (!Number.isFinite(n)) return String(x);
  return n.toFixed(decimals);
}

function fmtMoney(x: number): string {
  if (!Number.isFinite(x)) return "—";
  return x.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

function fmtDate(iso: string): string {
  try {
    return new Date(iso).toLocaleString();
  } catch {
    return iso;
  }
}

interface Props {
  symbol: string;
  refreshKey?: number;
}

export default function TransactionHistory({ symbol, refreshKey = 0 }: Props) {
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!symbol) return;

    const load = async () => {
      setLoading(true);
      setError(null);

      try {
        const res = await fetch("/api/orders/orders/", { credentials: "include" });

        if (!res.ok) {
          const txt = await res.text().catch(() => "");
          throw new Error(txt || `HTTP ${res.status}`);
        }

        const data = await res.json();

        // DRF pagination support
        const items: Order[] = Array.isArray(data) ? data : data?.results ?? [];

        const filtered = items
          .filter((o) => parseSymbol(o.instrument_display) === symbol.toUpperCase())
          .sort((a, b) => new Date(b.placed_at).getTime() - new Date(a.placed_at).getTime());

        setOrders(filtered);
      } catch (e: any) {
        setOrders([]);
        setError(e?.message || "Failed to load history.");
      } finally {
        setLoading(false);
      }
    };

    load();
  }, [symbol, refreshKey]);

  const rows = useMemo(() => {
    return orders.map((o) => {
      const qty = Number(o.filled_quantity || o.quantity);
      const px = Number(o.avg_fill_price || (o.fills?.[0]?.price ?? 0));
      const value = qty && px ? qty * px : 0;

      return {
        ...o,
        qty,
        px,
        value,
        date: fmtDate(o.placed_at),
      };
    });
  }, [orders]);

  return (
    <div className="tx-history">
      <div className="tx-header">
        <div className="tx-title">Transaction History</div>
        {loading && <div className="tx-sub">Loading…</div>}
      </div>

      {error && <div className="tx-error">{error}</div>}

      {!loading && !error && rows.length === 0 && (
        <div className="tx-empty">No transactions for {symbol} yet.</div>
      )}

      {!loading && rows.length > 0 && (
        <div className="tx-table">
          <div className="tx-row tx-head">
            <div>Date</div>
            <div>Side</div>
            <div>Type</div>
            <div className="right">Qty</div>
            <div className="right">Price</div>
            <div className="right">Value</div>
            <div>Status</div>
          </div>

          {rows.map((o) => (
            <div key={o.id} className="tx-row">
              <div className="muted">{o.date}</div>

              <div className={o.side === "BUY" ? "side buy" : "side sell"}>
                {o.side}
              </div>

              <div className="muted">{o.order_type}</div>

              <div className="right">{fmtNum(o.qty, 6)}</div>

              <div className="right">
                {o.avg_fill_price ? fmtNum(o.avg_fill_price, 4) : "—"}
              </div>

              <div className="right">{o.avg_fill_price ? fmtMoney(o.value) : "—"}</div>

              <div
                className={`status ${o.status.toLowerCase()}`}
                title={o.status === "REJECTED" && o.reject_reason ? o.reject_reason : undefined}
              >
                {o.status}
                {o.status === "REJECTED" && o.reject_reason && (
                  <span className="reject-reason" title={o.reject_reason}> ⚠</span>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
