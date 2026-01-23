
import React from "react";

function ScrollBox({children}: {children: React.ReactNode}) {
    return(
        <div style ={{maxHeight: "100%", overflowY: "auto"}}>
            {children}
        </div>
    )
} export default ScrollBox;