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
            <a href="#contact">Kontakt</a>
          </div>
        </div>
      </nav>

      <div className="hero-content">
        <div className="hero-container">
          <h1 className="hero-title">
            Vaša simulacija trgovanja u stvarnom vremenu
          </h1>
          <p className="hero-subtitle">
            BullBear je brokerska aplikacija za simulirano trgovanje dionicama i ETF-ovima
            uz tržišne podatke u stvarnom vremenu. Učite i vježbajte trgovanje bez rizika.
          </p>
          <div className="hero-buttons">
            <button className="btn btn-primary">Započni trgovanje</button>
            <button className="btn btn-secondary">Saznaj više</button>
          </div>
        </div>
      </div>
    </section>
  )
}

export default Hero
