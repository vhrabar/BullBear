import { useState, useEffect, SetStateAction, ChangeEvent } from "react";
import { useNavigate } from "react-router-dom";
import './ETFManage.css';

function ETFPage() {
    const navigate = useNavigate();
    const [content, setContent] = useState(<div></div>);
    const [loading, setLoading] = useState(true);
    const [funds, setFunds] = useState([]);
    const [page, setPage] = useState(0);
    const [search, setSearch] = useState("");

    const tabLinks = ["/api/funds/funds/", "/api/funds/subscriptions/", "/api/funds/subscriptions/unsubscribed/"];

    useEffect(() => {
        setLoading(true);
        
        fetch(tabLinks[page], {
            method: "GET",
            headers: { "Content-Type": "application/json" },
            credentials: "include",
        })
        .then(async (res) => {
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            return res.json();
        })
        .then((data) => {
            setFunds(data);
        })
        .catch((err) => {
            console.error("Error fetching funds:", err);
            setFunds([]);
        })
        .finally(() => {
            setLoading(false);
        });
    }, [page])

    useEffect(() => {
        if (loading) return;

        const res = funds.filter((x: any) =>
            (x.name || '').toLowerCase().includes(search) ||
            (x.description || '').toLowerCase().includes(search))
        if (res.length === 0) {
            setContent(<div className="empty">No ETFs found</div>);
        }
        else {setContent(<table>
        <thead>
            <tr><th>Name</th><th>Description</th><th>NAV per unit</th></tr>
        </thead>
        <tbody>
        {res.map((x: any) => (
            <tr key={x.fund_id || x.id} onClick={() => navigate("/ETF/"+(x.fund_id || x.id))} style={{cursor: "pointer"}}>
                <td>{x.name}</td>
                <td style={{overflow: "hidden"}}>{x.description}</td>
                <td>{x.nav_per_unit}</td>
            </tr>
        ))}
        {page === 0? <tr key="create-btn"><td colSpan={3}><button onClick={() => navigate("/ETF/create")}>Create new ETF</button></td></tr> : null}
        </tbody>
        </table>)}
    }, [funds, search, page, loading]);

    function openTab(i: SetStateAction<number>) {
        setPage(i);
    }

    const handleSearch = (e: ChangeEvent<HTMLInputElement>) => {
        const value = e.target.value.toLowerCase();
        setSearch(value);
    }

    return(<div className="etf-container">
        <div className="tab">
            <button className={`tablinks ${page === 0 ? 'active' : ''}`} onClick={() =>openTab(0)}>My ETFs</button>
            <button className={`tablinks ${page === 1 ? 'active' : ''}`} onClick={() =>openTab(1)}>Subscribed</button>
            <button className={`tablinks ${page === 2 ? 'active' : ''}`} onClick={() =>openTab(2)}>Explore</button>
        </div>
        <div>
            <div className="search-bar">
                <input
                    type="text"
                    value={search}
                    onChange={handleSearch}
                    placeholder="Search ETFs..."
                />
            </div>
        </div>
        {loading ? <div className="loading">Loading...</div> : content}
    </div>)
} export default ETFPage;