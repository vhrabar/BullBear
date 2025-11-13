import { useParams } from "react-router-dom";
import { useState, useEffect } from "react";
import StockPanel from "../components/StockPanel";
import { Holding } from "../components/StockView";

interface LatestData {
    bid_price: number;
    ask_price: number;
    ask_size: number;
    bid_size: number;
}

function QuotePage() {
  const { symbol } = useParams();
  const [data, setData] = useState<Holding | null>(null);
  const [latest, setLatest] = useState<LatestData | null>(null);

  useEffect(() => {
    if (!symbol) return;

    fetch("/api/trading/portfolio-holdings/", {
      method: "GET",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
    })
      .then((res) => res.json())
      .then((items) => {
        const found = items.find((i: any) =>
          i.instrument.toLowerCase().startsWith(symbol.toLowerCase())
        );
        setData(found || null);

        if (found) {
          const tickerPart = found.instrument.split("(")[0].trim();
          console.log(tickerPart)
          fetch(`/api/trading/latest-instrument-quote/${tickerPart}/quote/`, {
            method: "GET",
            credentials: "include",
          })
            .then((res) => res.json())
            .then((info) => setLatest(info))
            .catch(() => setLatest(null));
        } else {
          setLatest(null);
        }
      })
      .catch(() => {
        setData(null);
        setLatest(null);
      });
  }, [symbol]);

  return (
    <div className="portfolio-page">
      <StockPanel selected={data} latest={latest} />
    </div>
  );
}

export default QuotePage;
