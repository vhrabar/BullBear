import { useParams } from "react-router-dom";
import { useState, useEffect } from "react";
import StockPanel from "../components/StockPanel.tsx";
import { toggleFavorite, checkFavorite } from "../api/favorites";

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

interface NewsItem {
  id: number;
  headline: string;
  published_at: string;
  url?: string;
}

interface EarningsReport {
  id: number;
  company: string;
  report_date: string;
  fiscal_quarter: string;
  fiscal_year: number;
  estimate_eps: string | null;
  actual_eps: string | null;
}

interface Dividend {
  id: number;
  company: string;
  ex_date: string;
  payment_date: string;
  dividend_amount: string;
  currency: string;
}


function QuotePage() {
  const { symbol } = useParams();
  const [holding, setHolding] = useState<Holding | null>(null);
  const [latestQuote, setLatestQuote] = useState<LatestQuote | null>(null);
  const [candle, setCandle] = useState<Candle | null>(null);
  const [news, setNews] = useState<NewsItem[]>([]);
  const [earnings, setEarnings] = useState<EarningsReport[]>([]);
  const [dividends, setDividends] = useState<Dividend[]>([]);
  const [isFavorite, setIsFavorite] = useState(false);
  const [instrumentId, setInstrumentId] = useState<number | null>(null);

  // Fetch instrument ID and check if favorited
  useEffect(() => {
    if (!symbol) return;

    fetch(`/api/trading/instruments/${symbol}/`, {
      credentials: "include",
    })
      .then((res) => res.json())
      .then((data) => {
        if (data.id) {
          setInstrumentId(data.id);
          checkFavorite(data.id).then(setIsFavorite).catch(() => setIsFavorite(false));
        }
      })
      .catch(() => setInstrumentId(null));
  }, [symbol]);

  // Fetch holding if in portfolio
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
      })
      .catch(() => setHolding(null));
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

  // Fetch latest company news (latest 3)
 useEffect(() => {
  if (!symbol) return;

  fetch(`/api/trading/news/?companies__ticker=${symbol}&ordering=-published_at&limit=3`, {
    credentials: "include",
  })
    .then((res) => res.json())
    .then((data) => setNews(data.results || []))
    .catch(() => setNews([]));
}, [symbol]);


  useEffect(() => {
  if (!symbol) return;

  // Earnings
  fetch(`/api/trading/earnings-reports/?company__ticker=${symbol}&ordering=report_date`, {
    credentials: "include",
  })
    .then((res) => res.json())
    .then((data) => setEarnings(data || []))
    .catch(() => setEarnings([]));

  // Dividends
  fetch(`/api/trading/dividends/?company__ticker=${symbol}&ordering=ex_date`, {
    credentials: "include",
  })
    .then((res) => res.json())
    .then((data) => setDividends(data || []))
    .catch(() => setDividends([]));
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

  const handleToggleFavorite = async () => {
    if (!instrumentId) return;
    try {
      const result = await toggleFavorite(instrumentId);
      setIsFavorite(result.is_favorite);
    } catch (err) {
      console.error("Failed to toggle favorite:", err);
    }
  };

  return (
    <div className="portfolio-page">
      <div className="quote-header-actions">
        <button
          className={`quote-fav-btn ${isFavorite ? "is-favorite" : ""}`}
          onClick={handleToggleFavorite}
          disabled={!instrumentId}
          title={isFavorite ? "Remove from favorites" : "Add to favorites"}
        >
          {isFavorite ? "★ Favorited" : "☆ Add to Favorites"}
        </button>
      </div>
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
        news={news}
         earnings={earnings}
        dividends={dividends}
      />
    </div>
  );
}

export default QuotePage;
