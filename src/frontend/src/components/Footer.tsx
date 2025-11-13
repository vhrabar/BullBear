import './Footer.css'

function Footer() {
  const currentYear = new Date().getFullYear()

  return (
    <footer id="contact" className="footer">
      <div className="footer-container">
        <div className="footer-content">
          <div className="footer-brand">
            <div className="footer-logo">
              <span className="logo-icon">📈</span>
              <span className="logo-text">BullBear</span>
            </div>
            <p className="footer-description">
              Simulacija trgovanja dionicama i ETF-ovima
            </p>
          </div>

          <div className="footer-links">
            <div className="footer-section">
              <h4>Navigacija</h4>
              <a href="#features">Značajke</a>
              <a href="#about">O projektu</a>
            </div>

            <div className="footer-section">
              <h4>Projekt</h4>
              <a href="https://www.fer.unizg.hr" target="_blank" rel="noopener noreferrer">
                FER, UNIZG
              </a>
              <a href="#">Dokumentacija</a>
            </div>
          </div>
        </div>

        <div className="footer-bottom">
          <p>&copy; {currentYear} BullBear. Sva prava pridržana.</p>
          <p>Razvojni projekt - FER, Programsko inženjerstvo</p>
        </div>
      </div>
    </footer>
  )
}

export default Footer
