import { useState, useEffect, ChangeEvent } from "react";
import ETFPopUp from "../components/ETFPopUp";
import ScrollBox from "../components/ScrollBox";
import { getCSRFToken } from "../utils/csrf";
import './ETFManage.css';

interface Instrument {
    id: number;
    symbol: string;
    name: string;
    type: string;
    exchange: string;
    currency: string;
    is_active: boolean;
}

function ETFNew() {
    const [name, setName] = useState("");
    const [description, setDescription] = useState("");
    const [holdings, setHoldings] = useState<{id: number, name: string, weight: number}[]>([]);
    const [isPopUpOpen, setIsPopUpOpen] = useState(false);
    const [search, setSearch] = useState("");
    const [content, setContent] = useState(<table>
        <thead><tr><th>Name</th><th>Weight</th></tr></thead>
    </table>);
    const [popContent, setPopContent] = useState(<div></div>);
    const [popList, setPopList] = useState<Instrument[]>([]);
    
    useEffect(() => {
        const handleWeightChange = (index: number, value: number) => {
            setHoldings(prev => prev.map((item, i) =>
                i === index ? { ...item, weight: Math.max(value, 1) } : item
            ));
        };

        setContent(<table>
        <thead><tr><th>Name</th><th>Weight</th></tr></thead>
        <tbody>
        <ScrollBox>
         {holdings.map((x, index) => (
            <tr key={x.id}>
                <td>{x.name}</td>
                <td><input value={x.weight} type="number" min={1} onChange={(e) => {
                    handleWeightChange(index, Number(e.target.value));
                }}></input></td>
                </tr>
                ))}
        </ScrollBox>
        </tbody>
        </table>)
    }, [holdings]);

    useEffect(() => {
        const res = popList.filter((x) => 
            x.name.toLowerCase().includes(search));
        setPopContent(<table className="popUpTable">
            <tbody>
            <ScrollBox>
            {res.map((x) => (
                <tr key={x.id} onDoubleClick={() => {
                    setHoldings(prev => [...prev, {id: x.id, name: x.name, weight: 1}]);
                    setIsPopUpOpen(false);
                }}><td>{x.name}</td></tr>
            ))}
            </ScrollBox>
            </tbody>
        </table>)
    }, [popList, search]);

    async function addHoldings() {
        await fetch("/api/trading/instruments/", {
            method: "GET",
            headers: { "Content-Type": "application/json" }})
            .then(async (res) => {
                if (!res.ok) throw new Error(`HTTP ${res.status}`);
                return res.json();
            })
            .then((data : Instrument[]) => {
                const res = data.filter((x) => !(holdings.some((h) => h.id === x.id)))
                setPopList(res);
                setIsPopUpOpen(true);
            })
    }

    const handleSearch = (e: ChangeEvent<HTMLInputElement>) => {
            const value = e.target.value.toLowerCase();
            setSearch(value);
    }

    async function handleSubmit(e: React.FormEvent) {
        e.preventDefault();
        if (name.length === 0) {
            alert("Name is required");
            return;
        }
        if (holdings.length === 0) {
            alert("At least one holding is required");
            return;
        }
        let n = 0;
        holdings.forEach((x) => { n += x.weight; });
        await fetch("/api/users/portofolio-details/", {
            method: "GET",
            headers: { "Content-Type": "application/json" },
            credentials: "include"
        })
        .then(async (res) => {
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            return res.json();
        })
        .then(async (data) => {
            const csrftoken = getCSRFToken();
            const portfolioId = Array.isArray(data) ? data[0].id : data.id;
            await fetch("/api/funds/funds/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrftoken || "",
                },
                credentials: "include",
                body: JSON.stringify({
                    name: name,
                    description: description,
                    creator_portfolio: portfolioId,
                    holdings: holdings.map((x) => ({
                        instrument: x.id,
                        weight_percent: (x.weight / n) * 100}))
                })
            })
            .then(async (res) => {
                if (!res.ok) throw new Error(`HTTP ${res.status}`);
                window.location.href = "/ETF/explore";
            });
        })
    }

    return(<div className="etf-container">
        <ETFPopUp showPop={isPopUpOpen} closePop={() => setIsPopUpOpen(false)} search={search} handleSearch={handleSearch}>
            {popContent}
        </ETFPopUp>
        <form onSubmit={handleSubmit} className="etf-form">
            <h3>Create New ETF</h3>
            <label htmlFor="name">Name: </label>
            <input id="name" name="name" type="text" value={name} onChange={(e) => setName(e.target.value)} required /><br/>
            <label htmlFor="description">Description: </label>
            <input id="description" name="description" type="text"
            value={description} onChange={(e) => setDescription(e.target.value)} /><br/>
            <label htmlFor="holdings">Holdings</label>
            {content}
            <button type="button" onClick={addHoldings}>Add Holdings</button><br/>
            <button type="submit">Create ETF</button>
        </form>
    </div>
    )
} export default ETFNew;