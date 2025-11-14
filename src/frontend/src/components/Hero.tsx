import { Link } from 'react-router-dom'
import './Hero.css'

function Hero() {
  return (
    <section className="hero">
      <nav className="nav">
        <div className="nav-container">
          <div className="logo">
            <span className="logo-icon">📈</span>
            <span className="logo-text">BullBear</span>
          </div>
          <div className="nav-links">
            <a href="#features">Značajke</a>
            <a href="#about">O projektu</a>
            <Link to="/login" className="nav-btn">Prijava</Link>
          </div>
        </div>
      </nav>

      <div className="hero-content">
        <div className="hero-container">
          <h1 className="hero-title">
            Vaša simulacija trgovanja u stvarnom vremenu
          </h1>
          <p className="hero-subtitle">
            BullBear je brokerska aplikacija koja omogućava simulirano trgovanje dionicama i ETF-ovima.
            Testirajte strategije bez gubitka stvarnog kapitala uz pristup tržišnim podacima.
          </p>
          <div className="hero-buttons">
            <Link to="/positions" className="btn btn-primary">Započni s trgovanjem</Link>
            <a href="#features" className="btn btn-secondary">Saznaj više</a>
          </div>
        </div>
      </div>
    </section>
  )
}

export default Hero
