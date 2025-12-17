import React from "react";
import {GOOGLE_OAUTH_URL} from "../config.ts";

const GoogleOAuthButton: React.FC = () => {
  const handleLogin = () => {
      window.location.href = GOOGLE_OAUTH_URL;
    };


  return (
    <button onClick={handleLogin} className="oauth-btn google-btn">
      <span className="oauth-icon">G</span>
      Sign in with Google
    </button>
  );
};

export default GoogleOAuthButton;
