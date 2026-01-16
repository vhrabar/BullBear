import React from "react";
import {MICROSOFT_OAUTH_URL} from "../config.ts";

const MicrosftOAuthButton: React.FC = () => {
  const handleLogin = () => {
      window.location.href = MICROSOFT_OAUTH_URL
    };

  return (
    <button onClick={handleLogin} className="oauth-btn google-btn">
      <span className="oauth-icon">M</span>
      Sign in with Microsoft
    </button>
  );
};

export default MicrosftOAuthButton;
