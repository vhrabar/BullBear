import React from "react";
import AppRouter from "./routes/AppRouter.tsx";
import { AuthProvider } from "./auth/Auth.tsx";

const App: React.FC = () => {
  return (
      <AuthProvider>
        <AppRouter />
    </AuthProvider>

  );
};

export default App;
