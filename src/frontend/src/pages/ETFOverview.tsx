import { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import {PieChart} from "@mui/x-charts/PieChart";

interface ETF {
    id: number;
    creator_portfolio: number;
    name: string;
    description: string;
    is_active: boolean;
    total_units: number;
    nav_per_unit: number;
    holdings: any[];
}

function ETFView() {
    const params = useParams();
    const [content, setContent] = useState(<div></div>);
    const [holdingList, setHoldingList] = useState<string[]>([]);
    const [loading, setLoading] = useState(true);
    const [state, setState] = useState(0); // 0: undefined, 1: owner, 2: subscribed, 3: unsubscribed
    const [etf, setEtf] = useState<ETF | null>(null);
    const [val, setVal] = useState(0);
    const [portfolioId, setPortfolioId] = useState<number | null>(null);

    useEffect(() => {
        setLoading(true);
        fetch("api/users/portofolio-details/", {
            method: "GET",
            headers: { "Content-Type": "application/json" }})
            .then(async (res) => {
                if (!res.ok) throw new Error(`HTTP ${res.status}`);
                return res.json();
            })
            .then((data) => {
                setPortfolioId(data.id);
            })
            .then(() => {
        
        fetch("/api/funds/funds/"+params.id, {
            method: "GET",
            headers: { "Content-Type": "application/json" },
            credentials: "include",
        })
        .then(async (res) => {
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            return res.json();
        })
        .then((data) => {
            setEtf(data);
            fetch("/api/users/portofolio-details/", {
                method: "GET",
                headers: { "Content-Type": "application/json" },
                credentials: "include",
            })
            .then(async (res) => {
                if (!res.ok) throw new Error(`HTTP ${res.status}`);
                return res.json();
            })
            .then((data2) => {
                if (data.creator_portfolio === data2.id) {
                    setState(1);
                } else {
                    fetch("/api/fund/subscriptions/"+params.id, {
                        method: "GET",
                        headers: { "Content-Type": "application/json" },
                        credentials: "include",
                    })
                    .then(async (res) => {
                        if (!res.ok) throw new Error(`HTTP ${res.status}`);
                        return res.json();
                    })
                    .then((data3) => {
                        if (data3.fund === data.id && data3.subscriber_portfolio === data.creator_portfolio) {
                            setVal(data3.invested_amount / data.nav_per_unit);
                            setState(2);
                        }
                        else { setState(3); }
                    })
                    .catch(() => { setState(3); })
                    .finally(() => { render();});
                }
            })})
        })
    }, [])

    async function render() {
        if (etf === null) {
            setContent(<div>ETF not found</div>);
            setLoading(false);
            return;
        }
        else {
            etf.holdings.map(async (x) => {
                await fetch("/api/trading/instruments/" + x.instrument, {
                    method: "GET",
                    headers: { "Content-Type": "application/json" },
                    credentials: "include",
                })
                    .then(async (res) => {
                        if (!res.ok) throw new Error(`HTTP ${res.status}`);
                        return res.json();
                    })
                    .then((data) => {
                        setHoldingList([...holdingList, data.name]);
                    });
            });
            let i = 0;

            setContent(<div>
                <h2>{etf.name}</h2>
                <p>{etf.description}</p>
                <h3>Holdings:</h3>
                {etf.holdings.length === 0 ? <div>No holdings</div> : <PieChart 
                    series={[{
                        data: etf.holdings.map((x) => ({id: i, value: x.wight_percent, label: holdingList[i++]})),
                    }]}
                    width={200}
                    height={200}
                />}
                <div>
                    {state === 1 ? <div><a href={"/ETF/edit/"+params.id}><button>Edit ETF</button></a><button onClick={del}>Delete</button></div> : 
                    state === 2 ? <div><input id="amount" name="amount" type="number" min={0} value={val} step={1} onChange={(e) => {
                        setVal(Number(e.target.value));}}></input>
                        <button onClick={reSub}>Change investment</button>
                        <button onClick={unSub}>Unsubscribe</button></div> : 
                    state === 3 ? <div><label htmlFor="amount">Broj udjela: </label>
                    <input id="amount" name="amount" type="number" min={0} value={val} step={1} onChange={(e) => {
                        setVal(Number(e.target.value));}}></input>
                    <button onClick={sub}>Invest</button></div> : <div></div>}
                </div>
            </div>);
        }
    }

    async function del() {
        await fetch("/api/funds/funds/"+params.id, {
            method: "DELETE",
            headers: { "Content-Type": "application/json" },})
            .then(async (res) => {
                if (!res.ok) throw new Error(`HTTP ${res.status}`);
                window.location.href = "/ETF/explore/";
            });
    }

    async function unSub() {
        await fetch("/api/fund/subscriptions/"+params.id, {
            method: "DELETE",
            headers: { "Content-Type": "application/json" }})
            .then(async (res) => {
                if (!res.ok) throw new Error(`HTTP ${res.status}`);
                window.location.reload();
            });
    }

    async function sub() {
        setVal(Math.max(Math.round(val), 0));
        if (val === 0) return;
        await fetch("/api/fund/subscriptions/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({"subsriber_portfolio": portfolioId, "fund": Number(params.id), "invested_amount": val*((etf === null)? 0 : etf.nav_per_unit)})})
            .then(async (res) => {
                if (!res.ok) throw new Error(`HTTP ${res.status}`);
                window.location.reload();
            });
        }
    async function reSub() {
        setVal(Math.max(Math.round(val), 0));
        if (val === 0) return;
        await fetch("/api/fund/subscriptions/"+params.id, {
            method: "PATCH",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({"subsriber_portfolio": portfolioId, "fund": Number(params.id), "invested_amount": val*((etf === null)? 0 : etf.nav_per_unit)})})
            .then(async (res) => {
                if (!res.ok) throw new Error(`HTTP ${res.status}`);
                window.location.reload();
            });
        }
    return(<div>
        {loading ? <div>Loading...</div> : content}
    </div>)

} export default ETFView;
