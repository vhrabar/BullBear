import { useEffect, useState } from "react";
import StockView from "../components/StockView.tsx";

function PortfolioPage() {
  const [balance, setBalance] = useState(null);

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
        }
      } catch (err) {
        console.log("error", err);
      }
    }

    fetchPortfolio();
  }, []);

  return (
    <div className="portfolio-page">
      <div className="portfolio-upper">

        <div className="portfolio-inner">
          <div className="balance">

            {balance === null && (
              <div className="loading-message">
                Loading balance...
              </div>
            )}

            { balance !== null && (
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
