import { useState, useEffect, SetStateAction, ChangeEvent } from "react";

function ETFPage() {
    const [content, setContent] = useState(<div></div>);
    const [loading, setLoading] = useState(true);
    const [funds, setFunds] = useState([]);
    const [page, setPage] = useState(0);
    const [search, setSearch] = useState("");

    const tabLinks = ["/api/funds/funds/", "/api/fund/subscriptions", "/api/funds/subscriptions/unsubscribed/"];

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
    }, [page])

    useEffect(() => {
        setLoading(true);

        const res = funds.filter((x: any) => 
            x.name.toLowerCase().includes(search) || 
            x.description.toLowerCase().includes(search))
        if (res.length === 0) {
            setContent(<div>No ETFs found</div>);
        }
        else {setContent(<table>
        <tr><th>Name</th><th>Description</th><th>NAV per unit</th></tr>
        {res.map((x: any) => (
            <a href={"/ETF/"+x.id}><tr>
                <td>{x.name}</td>
                <td style={{overflow: "hidden"}}>{x.description}</td>
                <td>{x.nav_per_unit}</td>
            </tr></a>
        ))}
        {page === 0? <tr><a href="/ETF/create"><button>Create new ETF</button></a></tr> : null}
        </table>)}

        setLoading(false);
    }, [funds, search]);

    function openTab(i: SetStateAction<number>) {
        setPage(i);
    }

    const handleSearch = (e: ChangeEvent<HTMLInputElement>) => {
        const value = e.target.value.toLowerCase();
        setSearch(value);
    }

    return(<div>
        <div className="tab">
            <button className="tablinks" onClick={() =>openTab(0)}>My ETFs</button>
            <button className="tablinks" onClick={() =>openTab(1)}>Subscribed</button>
            <button className="tablinks" onClick={() =>openTab(2)}>Explore</button>
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
        {loading ? <div>Loading...</div> : content}
    </div>)
} export default ETFPage;