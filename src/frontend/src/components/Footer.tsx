import '../styles/Footer.css'

function Footer() {
    const currentYear = new Date().getFullYear()

    return (
        <footer id="contact" className="footer">
            <div className="footer-container">
                <div className="footer-content">
                    <div className="footer-brand">
                        <a href="/">
                            <div className="footer-logo">
                                <span className="logo-icon">📈</span>
                                <span className="logo-text">BullBear</span>
                            </div>
                        </a>

                        <p className="footer-description">
                            Simulacija trgovanja dionicama i ETF-ovima
                        </p>
                    </div>

                    <div className="footer-links">
                        <div className="footer-section">
                            <h4>Navigacija</h4>
                            <a href="/features">Značajke</a>
                            <a href="/about">O projektu</a>
                            <a href="/contact">Kontakt</a>
                            <a href="/faq">FAQ</a>
                            <a href="/pricing">Plaćanje</a>
                        </div>

                        <div className="footer-section">
                            <h4>Projekt</h4>
                            <a href="https://www.fer.unizg.hr" target="_blank" rel="noopener noreferrer">
                                FER, UNIZG
                            </a>
                            <a href="https://github.com/vhrabar/BullBear" target="_blank" rel="noopener noreferrer">
                                Izvorni kod
                            </a>
                            <a href="/docs/Home">Dokumentacija</a>
                        </div>
                    </div>
                </div>

                <div className="footer-bottom">
                    <a href="/licence">
                        &copy; {currentYear} BullBear. Licencirano pod GNU GPL v2.
                    </a>
                    <p>Razvojni projekt - FER, Programsko inženjerstvo</p>
                </div>
            </div>
        </footer>
    )
}

export default Footer
