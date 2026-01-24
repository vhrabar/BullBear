import "../styles/Pricing.css";
import Footer from "../components/Footer.tsx";
import {useNavigate} from "react-router-dom";

function Pricing() {
    const navigate = useNavigate();

    return (
        <div className="pricing-shell">
            <main className="pricing-main">
                <section className="pricing">
                    <div className="pricing-container">
                        <div className="pricing-header">
                            <h2 className="pricing-title">Cjenik</h2>
                            <p className="pricing-subtitle">
                                Odaberite plan koji odgovara vašem načinu učenja i korištenja
                                platforme.
                            </p>
                        </div>

                        <div className="pricing-grid">
                            {/* BASIC */}
                            <div className="plan-card">
                                <div className="plan-header">
                                    <div className="plan-badge plan-badge--neutral">
                                        OSNOVNI PLAN
                                    </div>
                                    <h3 className="plan-title">Besplatno</h3>

                                    <div className="plan-price">
                                        <span className="plan-price__value">0€</span>
                                        <span className="plan-price__period">/ mj.</span>
                                    </div>

                                    <p className="plan-desc">
                                        Idealno za početnike i testiranje platforme uz osnovna
                                        ograničenja.
                                    </p>
                                </div>

                                <ul className="plan-features">
                                    <li className="plan-feature plan-feature--limited">
                                        Ograničen broj trgovanja dnevno
                                    </li>
                                    <li className="plan-feature plan-feature--limited">
                                        Ograničen broj instrumenata dnevno
                                    </li>
                                    <li className="plan-feature plan-feature--limited">
                                        Nema pristupa kreiranju Mini fondova
                                    </li>
                                    <li className="plan-feature plan-feature--limited">
                                        Ograničene analize i napredne opcije
                                    </li>
                                </ul>

                                <div className="plan-actions">
                                    <button className="plan-btn plan-btn--neutral" type="button">
                                        Trenutni plan
                                    </button>
                                </div>
                            </div>

                            {/* PREMIUM */}
                            <div className="plan-card plan-card--featured">
                                <div className="plan-header">
                                    <div className="plan-badge plan-badge--primary">
                                        NAJPOPULARNIJE
                                    </div>
                                    <h3 className="plan-title">Neograničeno</h3>

                                    <div className="plan-price">
                                        <span className="plan-price__value">20€</span>
                                        <span className="plan-price__period">/ mj.</span>
                                    </div>

                                    <p className="plan-desc">
                                        Puni pristup svim funkcijama, bez dnevnih ograničenja.
                                    </p>
                                </div>

                                <ul className="plan-features">
                                    <li className="plan-feature plan-feature--ok">
                                        Neograničen broj trgovanja
                                    </li>
                                    <li className="plan-feature plan-feature--ok">
                                        Neograničen pristup instrumentima
                                    </li>
                                    <li className="plan-feature plan-feature--ok">
                                        Kreiranje i dijeljenje Mini fondova
                                    </li>
                                    <li className="plan-feature plan-feature--ok">
                                        Napredne analize i proširene opcije
                                    </li>
                                    <li className="plan-feature plan-feature--ok">
                                        Prioritetna podrška
                                    </li>
                                </ul>

                                <div className="plan-actions">
                                    <button
                                        type="button"
                                        className="plan-btn plan-btn--primary"
                                        onClick={() => navigate("/subscription")}
                                    >
                                        Aktiviraj Premium
                                    </button>

                                    <div className="plan-note">
                                        Naplata se vrši mjesečno. Otkazivanje je moguće u bilo kojem
                                        trenutku.
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div className="pricing-footnote">
                            <div className="pricing-info-card">
                                <div className="pricing-info-title">Napomena</div>
                                <div className="pricing-info-text">
                                    Platforma je namijenjena edukaciji i simulaciji trgovanja
                                    (paper trading). Premium plan donosi neograničen pristup i
                                    dodatne funkcije, bez promjene u sigurnosti ili načinu
                                    korištenja.
                                </div>
                            </div>
                        </div>
                        <div className="pricing-payments">
                            {/* Payment Methods Logos */}
                            <div className="pricing-payments__label">Dostupni načini plaćanja</div>

                            <div className="pricing-payments__logos">
                                <div className="payment-logo-card">
                                    <img
                                        src="https://cdn.simpleicons.org/stripe/FFFFFF"
                                        alt="Stripe"
                                        className="payment-logo"
                                        loading="lazy"
                                    />
                                </div>

                                <div className="payment-logo-card">
                                    <img
                                        src="https://cdn.simpleicons.org/paypal/FFFFFF"
                                        alt="PayPal"
                                        className="payment-logo"
                                        loading="lazy"
                                    />
                                </div>
                            </div>
                        </div>

                    </div>
                </section>
            </main>

            <Footer/>
        </div>
    );
}

export default Pricing;
