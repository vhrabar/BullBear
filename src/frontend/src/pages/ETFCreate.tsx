import { useState, useEffect, ChangeEvent } from "react";
import ETFPopUp from "../components/ETFPopUp";
import ScrollBox from "../components/ScrollBox";
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
        <tr><th>Name</th><th>Weight</th></tr>
    </table>);
    const [popContent, setPopContent] = useState(<div></div>);
    const [popList, setPopList] = useState<Instrument[]>([]);
    
    useEffect(() => {
        setContent(<table>
        <tr><th>Name</th><th>Weight</th></tr>
        <ScrollBox>
         {holdings.map((x, index) => (
            <tr key={x.id}>
                <td>{x.name}</td>
                <td><input value={x.weight} key={index} type="number" min={1} onChange={(e) =>{
                    holdings[index].weight = Math.max(Number(e.target.value), 1);
                }}></input></td>
                </tr>
                ))}
        </ScrollBox>
        </table>)
    }, [holdings]);

    useEffect(() => {
        const res = popList.filter((x) => 
            x.name.toLowerCase().includes(search));
        setPopContent(<table className="popUpTable">
            <ScrollBox>
            {res.map((x) => (
                <tr key={x.id} onDoubleClick={() => {
                    setHoldings([...holdings, {id: x.id, name: x.name, weight: 1}]);
                    setIsPopUpOpen(false);
                }}>{x.name}</tr>
            ))}
            </ScrollBox>
        </table>)
    }), [popList, search]

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
                setPopList(res)
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
            await fetch("/api/funds/funds/", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                credentials: "include",
                body: JSON.stringify({
                    name: name,
                    description: description,
                    creator_portfolio: data.id,
                    holdings: holdings.map((x) => ({
                        instrument: x.id,
                        weight_percent: x.weight / n}))
                })
            })
            .then(async (res) => {
                if (!res.ok) throw new Error(`HTTP ${res.status}`);
                window.location.href = "/ETF/explore";
            });
        })
    }

    return(<div>
        <h3>ETF Create Page</h3>
        <ETFPopUp showPop={isPopUpOpen} closePop={() => setIsPopUpOpen(false)} search={search} handleSearch={handleSearch}>
            {popContent}
        </ETFPopUp>
        <form onSubmit={handleSubmit} >
            <label htmlFor="name">Name: </label>
            <input id="name" name="name" type="text" value={name} onChange={(e) => setName(e.target.value)} required></input><br/>
            <label htmlFor="description">Description: </label>
            <input id="description" name="description" type="text"
            value={description} onChange={(e) => setDescription(e.target.value)}></input><br/>
            <label htmlFor="holdings">Holdings</label>
            {content}
            <button type="button" onClick={addHoldings}>Add Holdings</button><br/>
        </form>
    </div>
    )
} export default ETFNew;