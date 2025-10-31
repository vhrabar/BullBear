import './Features.css'

function Features() {
  const features = [
    {
      icon: '📊',
      title: 'Tržišni podaci u stvarnom vremenu',
      description: 'Pristup aktualnim tržišnim podacima i cijenama za dionice i ETF-ove.'
    },
    {
      icon: '💰',
      title: 'Paper Trading',
      description: 'Simulirajte trgovanje bez rizika gubitka stvarnog kapitala. Uvezite prethodne transakcije u CSV formatu.'
    },
    {
      icon: '📈',
      title: 'Analiza portfelja',
      description: 'Pratite performanse svog portfelja i analizirajte rezultate.'
    },
    {
      icon: '🏆',
      title: 'Ljestvice i natjecanje',
      description: 'Javni profili s vidljivim transakcijama na ukupnoj ljestvici. Usporedite se s drugim korisnicima.'
    },
    {
      icon: '📂',
      title: 'Mini fondovi',
      description: 'Kreirajte popise omiljenih instrumenata i dijelite ih s drugim korisnicima platforme.'
    },
    {
      icon: '⭐',
      title: 'Premium paket',
      description: 'Napredne funkcije za premium korisnike - push notifikacije, dodatne analize i više.'
    }
  ]

  return (
    <section id="features" className="features">
      <div className="features-container">
        <h2 className="features-title">Značajke</h2>
        <p className="features-subtitle">
          Sve što trebate za učenje i simulaciju trgovanja na tržištu
        </p>

        <div className="features-grid">
          {features.map((feature, index) => (
            <div key={index} className="feature-card">
              <div className="feature-icon">{feature.icon}</div>
              <h3 className="feature-title">{feature.title}</h3>
              <p className="feature-description">{feature.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}

export default Features
