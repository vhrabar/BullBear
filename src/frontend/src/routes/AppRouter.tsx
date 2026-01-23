import React from "react";
import {BrowserRouter as Router, Routes, Route} from "react-router-dom";
import Home from "../pages/Home.tsx";
import Login from "../pages/Login.tsx";
import PortfolioPage from "../pages/PortofolioPage.tsx";
import Layout from "../components/Layout.tsx";
import QuotePage from "../pages/QuotePage.tsx";
import ExchangePage from "../pages/ExplorePage.tsx";
import ETFCreate from "../pages/ETFCreate.tsx";
import ETFOverview from "../pages/ETFOverview.tsx";
import ETFEdit from "../pages/ETFEdit.tsx";
import ETFExplore from "../pages/ETFExplore.tsx";

import ProtectedRoute from "../auth/AuthProtection.tsx";
import Licence from "../pages/Licence";
import FAQ from "../pages/FAQ";
import Pricing from "../pages/Pricing";
import Features from "../components/Features";
import About from "../components/About";
import Contact from "../pages/Contact";
import CSVTade from "../pages/CSVTade";

const AppRouter: React.FC = () => {
    return (
        <Router>
            <Routes>

                <Route path="/" element={<Home/>}/>
                <Route path="/login" element={<Login/>}/>
                <Route path="/license" element={<Licence/>}/>
                <Route path="/faq" element={<FAQ/>}/>
                <Route path="/pricing" element={<Pricing/>}/>
                <Route path="/features" element={<Features/>}/>
                <Route path="/about" element={<About/>}/>
                <Route path="/contact" element={<Contact/>}/>

                <Route
                    path="/positions"
                    element={
                        <ProtectedRoute>
                            <Layout>
                                <PortfolioPage/>
                            </Layout>
                        </ProtectedRoute>
                    }
                />

                <Route
                    path="/quote/:symbol"
                    element={
                        <ProtectedRoute>
                            <Layout>
                                <QuotePage/>
                            </Layout>
                        </ProtectedRoute>
                    }
                />

                <Route
                    path="/explore"
                    element={
                        <ProtectedRoute>
                            <Layout>
                                <ExchangePage/>
                            </Layout>
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/csv"
                    element={
                        <ProtectedRoute>
                            <Layout>
                                <CSVTade/>
                            </Layout>
                        </ProtectedRoute>
                    }
                />

                <Route
                    path="/ETF/explore"
                    element={
                        <ProtectedRoute>
                            <Layout>
                                <ETFExplore/>
                            </Layout>
                        </ProtectedRoute>
                    }
                />

                <Route
                    path="/ETF/create"
                    element={
                        <ProtectedRoute>
                            <Layout>
                                <ETFCreate/>
                            </Layout>
                        </ProtectedRoute>
                    }
                />

                <Route
                    path="/ETF/edit/:id"
                    element={
                        <ProtectedRoute>
                            <Layout>
                                <ETFEdit/>
                            </Layout>
                        </ProtectedRoute>
                    }
                />

                <Route
                    path="/ETF/:id"
                    element={
                        <ProtectedRoute>
                            <Layout>
                                <ETFOverview/>
                            </Layout>
                        </ProtectedRoute>
                    }
                />

            </Routes>
        </Router>
    );
};

export default AppRouter;
