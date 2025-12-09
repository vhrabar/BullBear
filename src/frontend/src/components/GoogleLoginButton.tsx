import React from "react";

const GoogleOAuthButton: React.FC = () => {
  const handleLogin = () => {
    window.location.href = "https://api.bull-bear.app/auth/google/login";
    };


  return (
    <button onClick={handleLogin} className="oauth-btn google-btn">
      <span className="oauth-icon">G</span>
      Sign in with Google
    </button>
  );
};

export default GoogleOAuthButton;
