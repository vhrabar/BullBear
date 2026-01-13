import React, { useEffect, useState } from "react";
import { useParams, useLocation, Link } from "react-router-dom";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import rehypeRaw from "rehype-raw";
// @ts-ignore
import "../styles/Docs.css";
import Footer from "../components/Footer.tsx";

const markdownPages = [
    "Home",
    "1.-Opis-Projektnoga-zadataka",
    "2.-Analiza-zahtjeva",
    "3.-Specifikacija-zahtjeva-sustava",
    "4.-Arhitektura-i-dizajn-sustava",
    "5.-Arhitektura-komponenata-i-razmještaja",
    "6.-Ispitivanje-programskog-rješenja",
    "7.-Tehnologije-za-implementaciju-aplikacije",
    "8.--Upute-za-puštanje-u-pogon",
    "9.-Zaključak-i-budući-rad",
    "A.--Popis-literature",
    "B.-Prikaz-aktivnosti-grupe",
    "C.-Uporaba-Alata-Umjetne-inteligencije"
];

const DocsLayout: React.FC = () => {
  const { page } = useParams<{ page: string }>();
  const location = useLocation();
  const [markdown, setMarkdown] = useState<string>("");

  const currentPage = page || "Home";

  useEffect(() => {
    fetch(`/wiki/${currentPage}.md`)
      .then((res) => {
        if (!res.ok) throw new Error("Markdown file not found");
        return res.text();
      })
      .then(setMarkdown)
      .catch((err) => setMarkdown(`# Error\n${err.message}`));
  }, [currentPage]);

    // @ts-ignore
    return (
        <>
            <div className="docs-container">
                <aside className="docs-sidebar">
                    {markdownPages.map((p) => (
                        <Link
                            key={p}
                            to={`/docs/${p}`}
                            className={location.pathname === `/docs/${p}` ? "active" : ""}
                        >
                            {p.replaceAll("-", " ")}
                        </Link>
                    ))}
                </aside>

                <main className="docs-main">
                    <div className="docs-panel">
                        <ReactMarkdown remarkPlugins={[remarkGfm]} rehypePlugins={[rehypeRaw]}>
                            {markdown}
                        </ReactMarkdown>
                    </div>
                </main>
            </div>
            <Footer/></>
  );
};

export default DocsLayout;
