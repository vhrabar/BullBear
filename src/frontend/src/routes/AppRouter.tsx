import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Home from "../pages/Home.tsx";
import Licence from "../pages/Licence.tsx";
import Login from "../pages/Login.tsx";
import PageNotFound from "../pages/PageNotFound.tsx";
import PortfolioPage from "../pages/PortofolioPage.tsx";
import Pricing from "../pages/Pricing.tsx";
import QuotePage from "../pages/QuotePage.tsx";
import ExchangePage from "../pages/ExplorePage.tsx";
import ETFCreate from "../pages/ETFCreate.tsx";
import ETFOverview from "../pages/ETFOverview.tsx";
import ETFEdit from "../pages/ETFEdit.tsx";
import ETFExplore from "../pages/ETFExplore.tsx";

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
        <Route
          path="/ETF"
          element={
            <ProtectedRoute>
              <Layout>
                <Routes>
                  <Route path="/explore" element={<ETFExplore />} />
                  <Route path="/create" element={<ETFCreate />} />
                  <Route path="/edit/:id" element={<ETFEdit />} />
                  <Route path="/:id" element={<ETFOverview />} />
                </Routes>
              </Layout>
            </ProtectedRoute>
          }
          />
      </Routes>
    </Router>
  );
};

export default AppRouter;
