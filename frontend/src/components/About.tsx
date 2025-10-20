import './About.css'

function About() {
  return (
    <section id="about" className="about">
      <div className="about-container">
        <div className="about-content">
          <h2 className="about-title">O projektu</h2>
          <div className="about-text">
            <p>
              BullBear je brokerska aplikacija za simulirano trgovanje dionicama i
              ETF-ovima uz tržišne podatke u stvarnom vremenu.
            </p>
            <p>
              Projekt je razvijen na <strong>Fakultetu elektrotehnike i računarstva (FER),
              Sveučilišta u Zagrebu</strong> u sklopu kolegija <strong>Programsko inženjerstvo</strong>.
            </p>
            <p>
              Cilj projekta je primjena principa timskog rada, dizajna sustava,
              dokumentiranja, ispitivanja i modernih metoda razvoja softvera.
            </p>
          </div>

          <div className="about-info">
            <div className="info-item">
              <h3>Fakultet</h3>
              <p>FER, UNIZG</p>
            </div>
            <div className="info-item">
              <h3>Kolegij</h3>
              <p>Programsko inženjerstvo</p>
            </div>
            <div className="info-item">
              <h3>Tip</h3>
              <p>Obrazovni projekt</p>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}

export default About
