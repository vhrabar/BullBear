import React from "react";

const MicrosftOAuthButton: React.FC = () => {
  const handleLogin = () => {
      window.location.href = "https://api.bull-bear.app/auth/microsoft/login/";
    };

  return (
    <button onClick={handleLogin} className="oauth-btn google-btn">
      <span className="oauth-icon">M</span>
      Sign in with Microsoft
    </button>
  );
};

export default MicrosftOAuthButton;
