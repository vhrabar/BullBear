import React from "react";

const MicrosftOAuthButton: React.FC = () => {
  const handleLogin = () => {
      window.location.href = "http://localhost:8000/auth/microsoft/login/?process=login";
    };

  return (
    <button onClick={handleLogin} className="oauth-btn google-btn">
      <span className="oauth-icon">M</span>
      Sign in with Microsoft
    </button>
  );
};

export default MicrosftOAuthButton;
