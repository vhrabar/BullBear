import { useEffect, useState } from "react";
import StockView from "../components/StockView";

function PortfolioPage() {
  const [balance, setBalance] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchPortfolio() {
      try {
        const response = await fetch("/api/users/portofolio-details", {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
            credentials: "include",
          }
        });

        if (!response.ok) {
          throw new Error("Unable to fetch portfolio information.");
        }

        const data = await response.json();
        console.log(data)

        if (Array.isArray(data) && data.length > 0) {
          setBalance(data[0].balance);
        } else {
          setBalance("No portfolio found.");
        }
      } catch (err) {
        setError(err.message);
      }
    }

    fetchPortfolio();
  }, []);

  return (
    <div className="portfolio-page">
      <div className="portfolio-upper">

        <div className="portfolio-inner">
          <div className="balance">

            {!error && balance === null && (
              <div className="loading-message">
                Loading balance...
              </div>
            )}

            {!error && balance !== null && (
              <div className="balance-value">
                Balance: {balance}
              </div>
            )}
          </div>
            <StockView />
        </div>


      </div>
    </div>
  );
}

export default PortfolioPage;
