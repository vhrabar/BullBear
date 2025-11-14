import './About.css'

function About() {
  return (
    <section id="about" className="about">
      <div className="about-container">
        <div className="about-content">
          <h2 className="about-title">O projektu</h2>
          <div className="about-text">
            <p>
              BullBear je brokerska aplikacija koja korisnicima omogućava simulirano trgovanje (tzv. "paper trading")
              burzovnim instrumentima, poput dionica i ETF-ova. Korisnici imaju pristup tržišnim podacima uz vremenski
              odgođeno ažuriranje (10 do 15 minuta) putem Yahoo Finance API, Finnhub.io i Polygon.io.
            </p>
            <p>
              Primarni cilj platforme jest omogućiti korisnicima sigurno testiranje strategija trgovanja bez rizika
              gubitka stvarnog kapitala. Korisnici mogu kreirati javne ili privatne profile, dijeliti mini fondove,
              uvoziti transakcije u CSV formatu te pratiti uspješnost u usporedbi s tržišnim indeksima.
            </p>
            <p>
              Projekt je razvijen na <strong>Fakultetu elektrotehnike i računarstva (FER), Sveučilišta u Zagrebu</strong>
              u sklopu kolegija <strong>Programsko inženjerstvo</strong>, s ciljem primjene principa timskog rada, dizajna sustava,
              dokumentiranja, ispitivanja i modernih metoda razvoja. Platforma je hostana na DigitalOcean podu korištenjem
              GitHub Student Pack kredita.
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
