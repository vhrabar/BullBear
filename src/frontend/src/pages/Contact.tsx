import {useState, useEffect} from "react";
import "../styles/Contact.css";
import Footer from "../components/Footer.tsx";

interface ContactProfile {
    full_name: string;
    email: string;
    subject: string;
    message: string;
}

function getCookie(name: string): string | null {
    const match = document.cookie.match(new RegExp("(^| )" + name + "=([^;]+)"));
    return match ? decodeURIComponent(match[2]) : null;
}


const CONTACT_URL = "/api/users/contact/";

function ContactPage() {
    const [profile, setProfile] = useState<ContactProfile>({
        full_name: "",
        email: "",
        subject: "",
        message: "",
    });

    const [loading, setLoading] = useState<boolean>(true);
    const [submitting, setSubmitting] = useState<boolean>(false);
    const [error, setError] = useState<string | null>(null);
    const [success, setSuccess] = useState<string | null>(null);

    useEffect(() => {
        fetch(CONTACT_URL, {credentials: "include"})
            .then(async (res) => {
                const data = await res.json().catch(() => ({}));
                if (!res.ok) {
                    throw new Error(data?.detail || "Neuspješno učitavanje kontaktnih podataka.");
                }
                return data;
            })
            .then((data: Partial<ContactProfile>) => {
                setProfile((prev) => ({
                    ...prev,
                    full_name: data?.full_name ?? prev.full_name,
                    email: data?.email ?? prev.email,
                }));
                setError(null);
            })
            .catch((e: Error) => setError(e.message))
            .finally(() => setLoading(false));
    }, []);

    function onChange(
        e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
    ) {
        const {name, value} = e.target;
        setProfile((prev) => ({...prev, [name]: value}));
    }

    function validate(): string | null {
        if (!profile.full_name.trim()) return "Ime i prezime je obavezno.";
        if (!profile.email.trim()) return "E-mail je obavezan.";
        if (!profile.subject.trim()) return "Predmet je obavezan.";
        if (!profile.message.trim()) return "Poruka je obavezna.";
        if (!/^\S+@\S+\.\S+$/.test(profile.email.trim()))
            return "Molimo unesite valjanu e-mail adresu.";
        return null;
    }

    async function onSubmit(e: React.FormEvent) {
        e.preventDefault();
        setError(null);
        setSuccess(null);

        const validationError = validate();
        if (validationError) {
            setError(validationError);
            return;
        }

        setSubmitting(true);

        try {
            const csrfToken = getCookie("csrftoken");

            const res = await fetch(CONTACT_URL, {
                method: "POST",
                credentials: "include",
                headers: {
                    "Content-Type": "application/json",
                    ...(csrfToken ? {"X-CSRFToken": csrfToken} : {}),
                },
                body: JSON.stringify(profile),

            });

            const data = await res.json().catch(() => ({}));

            if (!res.ok) {
              const msg =
                data?.detail ||
                (typeof data === "object" ? JSON.stringify(data) : null) ||
                "Poruka nije mogla biti poslana.";

              throw new Error(msg);
            }


            setSuccess("Vaša poruka je uspješno poslana.");
            setProfile((prev) => ({...prev, subject: "", message: ""}));
        } catch (e: any) {
            setError(e?.message || "Neočekivana pogreška.");
        } finally {
            setSubmitting(false);
        }
    }

    if (loading) return <div className="contact-state">Učitavanje kontakt forme...</div>;
    if (error && !submitting)
        return (
            <div className="contact-state contact-state--error">
                <div className="contact-state__title">Pogreška kontakta</div>
                <div className="contact-state__desc">{error}</div>
                <button
                    onClick={() => window.location.reload()}
                    className="contact-btn contact-btn--neutral"
                >
                    Ponovno učitaj
                </button>
            </div>
        );

    return (
        <div className="contact-shell">
            <main className="contact-main">
                <div className="contact-page">
                    <div className="contact-card">
                        <div className="contact-header">
                            <div className="contact-title">Kontakt</div>
                            <div className="contact-subtitle">
                                Koristite ovu formu za kontaktiranje podrške ili administratora.
                            </div>
                        </div>

                        <form onSubmit={onSubmit} className="contact-form">
                            <div className="contact-grid">
                                <div className="contact-field">
                                    <label className="contact-label">Ime i prezime</label>
                                    <input
                                        className="contact-input"
                                        name="full_name"
                                        value={profile.full_name}
                                        onChange={onChange}
                                        placeholder="Vaše ime i prezime"
                                        autoComplete="name"
                                    />
                                </div>

                                <div className="contact-field">
                                    <label className="contact-label">E-mail</label>
                                    <input
                                        className="contact-input"
                                        name="email"
                                        value={profile.email}
                                        onChange={onChange}
                                        placeholder="vi@primjer.com"
                                        autoComplete="email"
                                    />
                                </div>
                            </div>

                            <div className="contact-field">
                                <label className="contact-label">Predmet</label>
                                <input
                                    className="contact-input"
                                    name="subject"
                                    value={profile.subject}
                                    onChange={onChange}
                                    placeholder="O čemu se radi?"
                                />
                            </div>

                            <div className="contact-field">
                                <label className="contact-label">Poruka</label>
                                <textarea
                                    className="contact-input contact-textarea"
                                    name="message"
                                    value={profile.message}
                                    onChange={onChange}
                                    placeholder="Ovdje napišite svoju poruku..."
                                />
                            </div>

                            {error && (
                                <div className="contact-alert contact-alert--error">{error}</div>
                            )}
                            {success && (
                                <div className="contact-alert contact-alert--success">{success}</div>
                            )}

                            <div className="contact-actions">
                                <button
                                    type="submit"
                                    className="contact-btn contact-btn--primary"
                                    disabled={submitting}
                                >
                                    {submitting ? "Slanje..." : "Pošalji"}
                                </button>

                                <button
                                    type="button"
                                    className="contact-btn contact-btn--neutral"
                                    onClick={() => {
                                        setError(null);
                                        setSuccess(null);
                                        setProfile((prev) => ({...prev, subject: "", message: ""}));
                                    }}
                                >
                                    Očisti
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            </main>

            <Footer/>
        </div>

    );
}

export default ContactPage;
