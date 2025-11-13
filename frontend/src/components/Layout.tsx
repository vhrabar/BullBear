import { ReactNode } from "react";
import { Link } from "react-router-dom";
import Footer from "./Footer";
import "./Layout.css";

interface LayoutProps {
  children: ReactNode;
}

function Layout({ children }: LayoutProps) {
  return (
    <div id="layout-root">
      <aside className="side-menu">
        <div className="side-logo">
          <span className="logo-icon">📈</span>
          <span className="logo-text">BullBear</span>
        </div>

        <nav className="side-nav">
          <Link to="/" className="side-link">
            Portfolio
          </Link>
        </nav>
      </aside>

      <div className="main-area">
        <header className="top-bar">
          <div className="top-title">Trading Dashboard</div>
        </header>

        <main className="main-content">{children}</main>

        <Footer />
      </div>
    </div>
  );
}

export default Layout;
