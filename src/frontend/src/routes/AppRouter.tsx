import React from "react";
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";

import About from "../components/About.tsx";
import Features from "../components/Features.tsx";
import Footer from "../components/Footer.tsx";
import Layout from "../components/Layout.tsx";

import ProtectedRoute from "../auth/AuthProtection.tsx";

import CSVTade from "../pages/CSVTade.tsx";
import Contact from "../pages/Contact.tsx";
import DocsLayout from "../pages/Docs.tsx";
import FAQ from "../pages/FAQ.tsx";
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
        {/* Public routes */}
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<Login />} />
        <Route path="/licence" element={<Licence />} />
        <Route path="/docs" element={<DocsLayout />} />
        <Route path="/docs/:page" element={<DocsLayout />} />
        <Route path="/features" element={<Features />} />
        <Route path="/pricing" element={<Pricing />} />
        <Route path="/faq" element={<FAQ />} />
        <Route path="/contact" element={<Contact />} />
        <Route
          path="/about"
          element={
            <>
              <About />
              <Footer />
            </>
          }
        />

        {/* Protected routes */}
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
          path="/csv"
          element={
            <ProtectedRoute>
              <Layout>
                <CSVTade />
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
