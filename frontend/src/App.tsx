import React from "react";
import { GoogleOAuthProvider } from "@react-oauth/google";
import AppRouter from "./routes/AppRouter";

const App: React.FC = () => {
  return (
    <GoogleOAuthProvider clientId="480645365103-27iedfv3hvtg5i30e158op7kgmmobu7e.apps.googleusercontent.com">
      <AppRouter /> {}
    </GoogleOAuthProvider>
  );
};

export default App;
