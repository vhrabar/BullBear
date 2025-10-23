import { Link } from 'react-router-dom'
import './Login.css'

function Login() {
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
          <h1 className="auth-title">Dobrodošli natrag</h1>
          <p className="auth-subtitle">Prijavite se u svoj BullBear račun</p>

          <div className="oauth-buttons">
            <button className="oauth-btn google-btn">
              <span className="oauth-icon">G</span>
              Prijava s Google računom
            </button>
            <button className="oauth-btn microsoft-btn">
              <span className="oauth-icon">M</span>
              Prijava s Microsoft računom
            </button>
          </div>

          <div className="divider">
            <span>ili</span>
          </div>

          <form onSubmit={handleSubmit} className="auth-form">
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
                placeholder="Unesite lozinku"
                required
              />
            </div>

            <div className="form-footer">
              <label className="checkbox-label">
                <input type="checkbox" />
                <span>Zapamti me</span>
              </label>
              <a href="#" className="forgot-link">Zaboravili ste lozinku?</a>
            </div>

            <button type="submit" className="submit-btn">
              Prijavi se
            </button>
          </form>

          <p className="auth-switch">
            Nemate račun? <Link to="/register">Registrirajte se</Link>
          </p>
        </div>
      </div>
    </div>
  )
}

export default Login
