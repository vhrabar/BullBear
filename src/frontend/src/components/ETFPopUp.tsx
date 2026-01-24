import React from "react";
import "./ETFPopUp.css";

function ETFPopUp({showPop, closePop, search, handleSearch, children}: {showPop: boolean, closePop: () => void, children: React.ReactNode
, search: string, handleSearch: (e: React.ChangeEvent<HTMLInputElement>) => void
}) {

    if (!showPop) {
        return null;
    }
    return(<div className="popup-bg" onDoubleClick={closePop}> 
        <div className="popup-content">
            <h3>Select instrument to add</h3>
            <div className="search-bar">
                <input
                    type="text"
                    value={search}
                    onChange={handleSearch}
                    placeholder="Search Instruments..."
                />
            </div>
            {children}
            </div>
    </div>)

} export default ETFPopUp;