import { useParams } from "react-router-dom";
import { useState, useEffect } from "react";
import StockPanel from "../components/StockPanel";

interface Holding {
  id: number;
  instrument: string;
  current_value: string;
  profit_loss: string;
  quantity: string;
  average_price: string;
}

interface LatestQuote {
  instrument: string;
  bid_price: string;
  bid_size: number;
  ask_price: string;
  ask_size: number;
  last_price: string;
  currency: string;
  exchange: string;
  market_state: string;
  daily_change: string;
  daily_change_percent: string;
  timestamp: string;
}

interface Candle {
  instrument: string;
  start_time: string;
  end_time: string;
  open_price: string;
  high_price: string;
  low_price: string;
  close_price: string;
  volume: number | null;
  updated_at: string;
}

function QuotePage() {
  const { symbol } = useParams();
  const [holding, setHolding] = useState<Holding | null>(null);
  const [latestQuote, setLatestQuote] = useState<LatestQuote | null>(null);
  const [candle, setCandle] = useState<Candle | null>(null);

  // Fetch holding .> if in port
  useEffect(() => {
    if (!symbol) return;

    fetch("/api/trading/portfolio-holdings/", {
      credentials: "include",
    })
      .then((res) => res.json())
      .then((items) => {
        const found = items.find((i: Holding) =>
          i.instrument.toLowerCase().startsWith(symbol.toLowerCase())
        );
        setHolding(found || null);
      });
  }, [symbol]);

  // Fetch latest quote
  useEffect(() => {
    if (!symbol) return;

    fetch(`/api/trading/latest-instrument-quote/${symbol}/quote`, {
      credentials: "include",
    })
      .then((res) => res.json())
      .then((data) => setLatestQuote(data))
      .catch(() => setLatestQuote(null));
  }, [symbol]);

  // Fetch latest candle
  useEffect(() => {
    if (!symbol) return;

    fetch(`/api/trading/latest-instrument-data/?instrument=${symbol}`, {
      credentials: "include",
    })
      .then((res) => res.json())
      .then((data) => setCandle(data[0] || null))
      .catch(() => setCandle(null));
  }, [symbol]);

  // Build the instrument info for StockPanel
  const stock =
    symbol
      ? {
          symbol: symbol.toUpperCase(),

          name:
            holding?.instrument
              ?.split("(")[1]
              ?.replace(")", "")
              ?.trim() || symbol.toUpperCase(),
        }
      : null;

  return (
    <div className="portfolio-page">
      <StockPanel
        stock={stock}
        holding={holding}
        latest={{
          ...latestQuote,
          open_price: candle?.open_price,
          high_price: candle?.high_price,
          low_price: candle?.low_price,
          close_price: candle?.close_price,
        }}
      />
    </div>
  );
}

export default QuotePage;
