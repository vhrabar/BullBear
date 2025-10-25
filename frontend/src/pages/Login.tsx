import { Link } from "react-router-dom";
import "./Login.css";
import GoogleOAuthButton from "../components/GoogleLoginButton";

function Login() {

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
          <GoogleOAuthButton />
        </div>


            <button className="oauth-btn microsoft-btn">
              <span className="oauth-icon">M</span>
              Prijava s Microsoft računom
            </button>
          </div>
        </div>
      </div>
  );
}

export default Login;
