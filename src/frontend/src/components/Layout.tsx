import { ReactNode } from "react";
import { Link } from "react-router-dom";
import Footer from "./Footer.tsx";
import "../styles/Layout.css";

interface LayoutProps {
  children: ReactNode;
}

function Layout({ children }: LayoutProps) {
      const location = useLocation();
  return (
    <div id="layout-root">
      <aside className="side-menu">
        <div className="side-logo">
          <span className="logo-icon">📈</span>
          <span className="logo-text">BullBear</span>
        </div>

        <nav className="side-nav">
          <Link to="/positions" className="side-link">
            Portfolio
          </Link>
            <Link to="/explore" className="side-link">
            Explore
          </Link>
            <Link
            to="/favorites"
            className={`side-link ${location.pathname === "/favorites" ? "active" : ""}`}
          >
            Favorites
          </Link>

          <Link to="/csv" className="side-link">
            Import / Export
          </Link>
          <Link to="/leaderboard" className={`side-link ${location.pathname === '/leaderboard' ? 'active' : ''}`}>
            Leaderboard
          </Link>
          <Link to="/etf/explore" className="side-link">
            Funds
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
