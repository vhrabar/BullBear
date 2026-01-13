import { useState, useEffect } from "react";
import "../styles/Contact.css";
import Footer from "../components/Footer.tsx";

interface ContactProfile {
  full_name: string;
  email: string;
  subject: string;
  message: string;
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
    fetch(CONTACT_URL, { credentials: "include" })
      .then(async (res) => {
        const data = await res.json().catch(() => ({}));
        if (!res.ok) {
          throw new Error(data?.detail || "Failed to load contact data.");
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
    const { name, value } = e.target;
    setProfile((prev) => ({ ...prev, [name]: value }));
  }

  function validate(): string | null {
    if (!profile.full_name.trim()) return "Full name is required.";
    if (!profile.email.trim()) return "Email is required.";
    if (!profile.subject.trim()) return "Subject is required.";
    if (!profile.message.trim()) return "Message is required.";
    if (!/^\S+@\S+\.\S+$/.test(profile.email.trim()))
      return "Please enter a valid email address.";
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
      const res = await fetch(CONTACT_URL, {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(profile),
      });

      const data = await res.json().catch(() => ({}));

      if (!res.ok) {
        throw new Error(
          data?.detail || data?.error || "Message could not be sent."
        );
      }

      setSuccess("Your message has been sent successfully.");
      setProfile((prev) => ({ ...prev, subject: "", message: "" }));
    } catch (e: any) {
      setError(e?.message || "Unexpected error.");
    } finally {
      setSubmitting(false);
    }
  }

  if (loading) return <div className="contact-state">Loading contact form...</div>;
  if (error && !submitting)
    return (
      <div className="contact-state contact-state--error">
        <div className="contact-state__title">Contact Error</div>
        <div className="contact-state__desc">{error}</div>
        <button
          onClick={() => window.location.reload()}
          className="contact-btn contact-btn--neutral"
        >
          Reload
        </button>
      </div>
    );

  return (
  <div className="contact-shell">
    <main className="contact-main">
      <div className="contact-page">
        <div className="contact-card">
          <div className="contact-header">
            <div className="contact-title">Contact</div>
            <div className="contact-subtitle">
              Use this form to contact support or the administrators.
            </div>
          </div>

          <form onSubmit={onSubmit} className="contact-form">
            <div className="contact-grid">
              <div className="contact-field">
                <label className="contact-label">Full name</label>
                <input
                  className="contact-input"
                  name="full_name"
                  value={profile.full_name}
                  onChange={onChange}
                  placeholder="Your full name"
                  autoComplete="name"
                />
              </div>

              <div className="contact-field">
                <label className="contact-label">Email</label>
                <input
                  className="contact-input"
                  name="email"
                  value={profile.email}
                  onChange={onChange}
                  placeholder="you@example.com"
                  autoComplete="email"
                />
              </div>
            </div>

            <div className="contact-field">
              <label className="contact-label">Subject</label>
              <input
                className="contact-input"
                name="subject"
                value={profile.subject}
                onChange={onChange}
                placeholder="What is the issue about?"
              />
            </div>

            <div className="contact-field">
              <label className="contact-label">Message</label>
              <textarea
                className="contact-input contact-textarea"
                name="message"
                value={profile.message}
                onChange={onChange}
                placeholder="Write your message here..."
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
                {submitting ? "Sending..." : "Send"}
              </button>

              <button
                type="button"
                className="contact-btn contact-btn--neutral"
                onClick={() => {
                  setError(null);
                  setSuccess(null);
                  setProfile((prev) => ({ ...prev, subject: "", message: "" }));
                }}
              >
                Clear
              </button>
            </div>
          </form>
        </div>
      </div>
    </main>

    <Footer />
  </div>

  );
}

export default ContactPage;
