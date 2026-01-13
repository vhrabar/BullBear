import React from "react";
import {BrowserRouter as Router, Routes, Route} from "react-router-dom";
import Home from "../pages/Home.tsx";
import Login from "../pages/Login.tsx";
import PortfolioPage from "../pages/PortofolioPage.tsx";
import Layout from "../components/Layout.tsx";
import QuotePage from "../pages/QuotePage.tsx";
import ExchangePage from "../pages/ExplorePage.tsx";
import Licence  from "../pages/Licence.tsx";
import DocsLayout from "../pages/Docs.tsx";

import ProtectedRoute from "../auth/AuthProtection.tsx";
import About from "../components/About.tsx";
import Features from "../components/Features.tsx";
import Footer from "../components/Footer.tsx";
import PageNotFound from "../pages/PageNotFound.tsx";
import Contact from "../pages/Contact.tsx";


const AppRouter: React.FC = () => {
    return (
        <Router>
            <Routes>
                <Route path="/" element={<Home/>}/>
                <Route path="/licence" element={<Licence />}/>
                <Route path="/docs/:page" element={<DocsLayout />} />
                <Route path="/docs" element={<DocsLayout />} />
                <Route path="/features" element={<><Features/><Footer/></>} />
                {/*<Route path="/pricing" element={<Pricing />} />*/}
                {/*<Route path="/faq" element={<FAQ />} />*/}
                <Route path="/contact" element={<Contact />} />
                <Route path="/about" element={<><About/><Footer/></>} />
                <Route path="/login" element={<Login/>}/>

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

                <Route path="*" element={<PageNotFound />} />
            </Routes>
        </Router>
    );
};

export default AppRouter;
