import {ReactNode, useState, useRef, useEffect} from "react";
import {Link, useLocation, useNavigate} from "react-router-dom";
import Footer from "./Footer.tsx";
import "../styles/Layout.css";
import { getCSRFToken } from "../utils/csrf";

interface LayoutProps {
    children: ReactNode;
}

function Layout({children}: LayoutProps) {
    const location = useLocation();
    const navigate = useNavigate();
    const [menuOpen, setMenuOpen] = useState(false);
    const menuRef = useRef<HTMLDivElement | null>(null);
    // avatarUrl: undefined = not loaded yet, null = no avatar, string = avatar URL
    const [avatarUrl, setAvatarUrl] = useState<string | null | undefined>(undefined);

    useEffect(() => {
        function onDocClick(ev: MouseEvent) {
            if (menuRef.current && !menuRef.current.contains(ev.target as Node)) {
                setMenuOpen(false);
            }
        }
        document.addEventListener('click', onDocClick);
        return () => document.removeEventListener('click', onDocClick);
    }, []);

    useEffect(() => {
        let mounted = true;
        (async () => {
            try {
                const res = await fetch('/api/users/user-profile/me/', { credentials: 'include' });
                if (!mounted) return;
                if (res.ok) {
                    const data = await res.json();
                    setAvatarUrl(data?.avatar_url ?? null);
                } else {
                    setAvatarUrl(null);
                }
            } catch (err) {
                if (mounted) setAvatarUrl(null);
            }
        })();
        return () => { mounted = false; };
    }, []);

    async function handleResetPortfolio() {
        const ok = window.confirm("Reset your portfolio to the default state? This will remove all holdings. Continue?");
        if (!ok) return;
        try {
            const listResp = await fetch('/api/users/portofolio-details/', { credentials: 'include' });
            if (!listResp.ok) throw new Error(`Failed to fetch portfolios: ${listResp.status}`);
            const list = await listResp.json();
            const portfolio = Array.isArray(list) ? list[0] : list;
            if (!portfolio || !portfolio.id) {
                alert('No portfolio found to reset.');
                return;
            }

            const csrftoken = getCSRFToken();
            const delResp = await fetch(`/api/users/portofolio-details/${portfolio.id}/`, {
                method: 'DELETE',
                credentials: 'include',
                headers: {
                    'Content-Type': 'application/json',
                    ...(csrftoken ? { 'X-CSRFToken': csrftoken } : {}),
                },
            });

            if (!delResp.ok) {
                const txt = await delResp.text().catch(() => null);
                throw new Error(txt || `HTTP ${delResp.status}`);
            }

            window.location.reload();
        } catch (err: any) {
            console.error('Portfolio reset failed', err);
            alert('Failed to reset portfolio: ' + (err?.message || err));
        } finally {
            setMenuOpen(false);
        }
    }

    async function handleLogout() {
        try {
            const csrftoken = getCSRFToken();
            await fetch('/api/auth/logout/', {
                method: 'POST',
                credentials: 'include',
                headers: {
                    'Content-Type': 'application/json',
                    ...(csrftoken ? { 'X-CSRFToken': csrftoken } : {}),
                },
            });
        } catch (err) {
            // ignore - best effort logout
            console.error('Logout failed', err);
        } finally {
            // redirect to login page
            navigate('/login');
        }
    }

    return (
        <div id="layout-root">
            <aside className="side-menu">
                <div className="side-logo">
                    <span className="logo-icon">📈</span>
                    <span className="logo-text">BullBear</span>
                </div>

                <nav className="side-nav">
                    <Link to="/profile" className="side-link">
                        Profile
                    </Link>
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

                    <Link
                        to="/leaderboard"
                        className={`side-link ${location.pathname === "/leaderboard" ? "active" : ""}`}
                    >
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

                    {/* Profile avatar / menu on the right */}
                    <div className="top-right" ref={menuRef}>
                        <button
                            className="profile-btn"
                            onClick={() => setMenuOpen(prev => !prev)}
                            aria-haspopup="true"
                            aria-expanded={menuOpen}
                        >
                            {avatarUrl ? (
                                <img
                                    src={avatarUrl}
                                    alt="Profile"
                                    className="profile-avatar"
                                    onError={(e) => { (e.target as HTMLImageElement).style.display = 'none'; }}
                                />
                            ) : (
                                // Stable placeholder (no image swap) to avoid blinking
                                <div className="profile-placeholder" aria-hidden>
                                    <span className="profile-placeholder-icon">👤</span>
                                </div>
                            )}
                        </button>

                        {menuOpen && (
                            <div className="profile-dropdown">
                                <Link to="/profile" className="dropdown-item" onClick={() => setMenuOpen(false)}>My profile</Link>
                                <button className="dropdown-item" onClick={handleResetPortfolio}>Reset portfolio</button>
                                <button className="dropdown-item logout" onClick={handleLogout}>Logout</button>
                            </div>
                        )}
                     </div>
                 </header>

                 <main className="main-content">{children}</main>

                 <Footer/>
             </div>
         </div>
     );
 }

 export default Layout;
