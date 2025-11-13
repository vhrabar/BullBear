import React from "react";

const GoogleOAuthButton: React.FC = () => {
  const handleLogin = () => {
    window.location.href = "http://localhost:8000/auth/google/login/?process=login";
    };


  return (
    <button onClick={handleLogin} className="oauth-btn google-btn">
      <span className="oauth-icon">G</span>
      Sign in with Google
    </button>
  );
};

export default GoogleOAuthButton;
