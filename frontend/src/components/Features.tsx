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
      title: 'Simulirano trgovanje',
      description: 'Vježbajte strategije trgovanja bez rizika sa virtualnim novcem.'
    },
    {
      icon: '📈',
      title: 'Praćenje portfelja',
      description: 'Pratite performanse svog portfelja i analizirajte rezultate.'
    },
    {
      icon: '🎓',
      title: 'Edukativni projekt',
      description: 'Razvijeno na FER-u, UNIZG u sklopu kolegija Programsko inženjerstvo.'
    },
    {
      icon: '🔒',
      title: 'Sigurno okruženje',
      description: 'Učite i eksperimentirajte u sigurnom, izoliranom okruženju.'
    },
    {
      icon: '📱',
      title: 'Responzivan dizajn',
      description: 'Pristupite aplikaciji s bilo kojeg uređaja - desktop, tablet ili mobitel.'
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
