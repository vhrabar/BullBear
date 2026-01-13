import { Link } from "react-router-dom";
import "../styles/Login.css";
import GoogleOAuthButton from "../components/GoogleLoginButton.tsx";
import MicrosftAuthButton from "../components/MicrosoftLoginButton.tsx";

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
          <GoogleOAuthButton /> <MicrosftAuthButton />

        </div>
          </div>
        </div>
      </div>
  );
}

export default Login;
