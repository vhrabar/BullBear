import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Home from "../pages/Home";
import Login from "../pages/Login";
import PortfolioPage from "../pages/PortofolioPage.tsx";
import Layout from "../components/Layout.tsx";
import QuotePage from "../pages/QuotePage.tsx";
import ExchangePage from "../pages/ExplorePage.tsx";

const AppRouter: React.FC = () => {
  return (
    <Router>
      <Routes>

        <Route path="/" element={<Home />} />
        <Route path="/login" element={<Login />} />

        <Route
          path="/positions"
          element={
            <Layout>
              <PortfolioPage />
            </Layout>
          }
        />

        <Route
          path="/quote/:symbol"
          element={
            <Layout>
              <QuotePage />
            </Layout>
          }
        />

        <Route
          path="/explore"
          element={
            <Layout>
              <ExchangePage />
            </Layout>
          }
        />

      </Routes>
    </Router>
  );
};

export default AppRouter;
