import { Link } from 'react-router-dom'
import './Login.css'

function Register() {
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
  }

  return (
    <div className="auth-page">
      <nav className="auth-nav">
        <Link to="/" className="auth-logo">
          <span className="logo-icon">📈</span>
          <span className="logo-text">BullBear</span>
        </Link>
      </nav>

      <div className="auth-container">
        <div className="auth-card">
          <h1 className="auth-title">Kreirajte račun</h1>
          <p className="auth-subtitle">Započnite s paper tradingom danas</p>

          <div className="oauth-buttons">
            <button className="oauth-btn google-btn">
              <span className="oauth-icon">G</span>
              Registracija s Google računom
            </button>
            <button className="oauth-btn microsoft-btn">
              <span className="oauth-icon">M</span>
              Registracija s Microsoft računom
            </button>
          </div>

          <div className="divider">
            <span>ili</span>
          </div>

          <form onSubmit={handleSubmit} className="auth-form">
            <div className="form-group">
              <label htmlFor="name">Ime i prezime</label>
              <input
                type="text"
                id="name"
                placeholder="Ime Prezime"
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="email">Email adresa</label>
              <input
                type="email"
                id="email"
                placeholder="vas.email@primjer.com"
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="password">Lozinka</label>
              <input
                type="password"
                id="password"
                placeholder="Minimalno 8 znakova"
                required
                minLength={8}
              />
            </div>

            <div className="form-group">
              <label htmlFor="confirmPassword">Potvrdite lozinku</label>
              <input
                type="password"
                id="confirmPassword"
                placeholder="Ponovite lozinku"
                required
                minLength={8}
              />
            </div>

            <label className="checkbox-label">
              <input type="checkbox" required />
              <span>Prihvaćam uvjete korištenja i politiku privatnosti</span>
            </label>

            <button type="submit" className="submit-btn">
              Registriraj se
            </button>
          </form>

          <p className="auth-switch">
            Već imate račun? <Link to="/login">Prijavite se</Link>
          </p>
        </div>
      </div>
    </div>
  )
}

export default Register
