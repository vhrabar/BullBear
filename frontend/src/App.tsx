import React from "react";
import AppRouter from "./routes/AppRouter";
import { AuthProvider } from "./auth/Auth";

const App: React.FC = () => {
  return (
      <AuthProvider>
        <AppRouter />
    </AuthProvider>

  );
};

export default App;
