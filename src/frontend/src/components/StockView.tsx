import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import "./StockView.css";

export interface Holding {
  id: number;
  instrument: string;
  current_value: string;
  profit_loss: string;
  quantity: string;
  average_price: string;
  added_at?: string;
  portofolio?: number;
}

function StockView() {
  const [holdings, setHoldings] = useState<Holding[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  const API_URL = "/api/trading/portfolio-holdings/";

  useEffect(() => {
    fetch(API_URL, {
      method: "GET",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
    })
      .then(async (res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then((data) => {
        setHoldings(Array.isArray(data) ? data : []);
        setLoading(false);
      })
      .catch((err: Error) => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  if (loading) return <div id="loading">Loading...</div>;
  if (error) return <div id="error">Error: {error}</div>;
  if (!holdings.length) return <div id="empty">No holdings found.</div>;

  return (
    <div id="container-root">
      <table id="container">
        <thead>
          <tr>
            <th>Instrument</th>
            <th>Current Value</th>
            <th>Profit/Loss</th>
            <th>Quantity</th>
            <th>Average Price</th>
          </tr>
        </thead>
        <tbody>
          {holdings.map((x) => {
            const [ticker, rest] = x.instrument.split("(");
            const corpo = rest ? rest.split(")")[0] : "";

            return (
              <tr
                key={x.id}
                className="stock-item"
                onClick={() => navigate(`/quote/${ticker.trim()}`)}
              >
                <td>
                  <p>{ticker}</p>
                  <p className="corpo">{corpo}</p>
                </td>
                <td>{x.current_value}</td>
                <td
                  style={
                    x.profit_loss.startsWith("-")
                      ? { color: "red" }
                      : { color: "green" }
                  }
                >
                  {x.profit_loss}
                </td>
                <td>{x.quantity}</td>
                <td>{x.average_price}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

export default StockView;


/*
let test = JSON.parse('['+
    '{'+
        '"id": 1,'+
        '"instrument": "AMD (AMD)",'+
        '"current_value": "31014.000",'+
        '"profit_loss": "294.000",'+
        '"quantity": "120.000",'+
        '"average_price": "256.000",'+
        '"added_at": "2025-11-03T16:50:25.5999",'+
        '"portofolio": 1'+
    '},'+
    '{'+
        '"id": 2,'+
        '"instrument": "NVDA(Nvidia Corporation)",'+
        '"current_value": "25721.760",'+
        '"profit_loss": "137.760",'+
        '"quantity": "123.000",'+
        '"average_price": "208.000",'+
        '"added_at": "2025-11-03T16:57:07.7827",'+
        '"portofolio": 1'+
    '}'+
']')
;*/


//TEST VERZIJA- DO NOT DELETE!!! --- lakšse za testiranje
// useEffect(() => {
//     const list = test.map((x: {
//             id: number;
//             instrument: string;
//             current_value: string;
//             profit_loss: string;
//             quantity: string;
//             average_price: string;
//         }) => (
//             <tr key={x.id} className="stock-item">
//                 <td>
//                     <p>{x.instrument.split('(')[0]}</p>
//                     <p className='corpo'>{x.instrument.split('(')[1].split(')')[0]}</p>
//                 </td>
//                 <td>{x.current_value}</td>
//                 <td style={(x.profit_loss[0]=='-')? {color: 'red'}:{color: 'green'}}>{x.profit_loss}</td>
//                 <td>{x.quantity}</td>
//                 <td>{x.average_price}</td>
//             </tr>
//         ));
//         setContent(
//         <div id='container-root'>
//             <table id='container'>
//                 <tr>
//                     <th>Instrument</th>
//                     <th>Current Value</th>
//                     <th>Profit/Loss</th>
//                     <th>Quantity</th>
//                     <th>Average Price</th>
//                 </tr>
//                 {list}
//             </table>
//         </div>);
// }, []);