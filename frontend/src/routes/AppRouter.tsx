import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Home from "../pages/Home";
import Login from "../pages/Login";
import PortfolioPage from "../pages/PortofolioPage.tsx";
import Layout from "../components/Layout.tsx";
import QuotePage from "../pages/QuotePage.tsx";
import ExchangePage from "../pages/ExplorePage.tsx";

import ProtectedRoute from "../auth/AuthProtection.tsx";

const AppRouter: React.FC = () => {
  return (
    <Router>
      <Routes>

        <Route path="/" element={<Home />} />
        <Route path="/login" element={<Login />} />

        <Route
          path="/positions"
          element={
            <ProtectedRoute>
              <Layout>
                <PortfolioPage />
              </Layout>
            </ProtectedRoute>
          }
        />

        <Route
          path="/quote/:symbol"
          element={
            <ProtectedRoute>
              <Layout>
                <QuotePage />
              </Layout>
            </ProtectedRoute>
          }
        />

        <Route
          path="/explore"
          element={
            <ProtectedRoute>
              <Layout>
                <ExchangePage />
              </Layout>
            </ProtectedRoute>
          }
        />

      </Routes>
    </Router>
  );
};

export default AppRouter;
