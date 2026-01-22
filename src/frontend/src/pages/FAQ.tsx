import { useState } from "react";
import "../styles/FAQ.css";
import Footer from "../components/Footer.tsx";

interface FAQItem {
  question: string;
  answer: string;
}

function FAQ() {
  const faqs: FAQItem[] = [
    {
      question: "Što je BullBear platforma?",
      answer:
        "BullBear je edukativna platforma za simulaciju trgovanja (paper trading) dionicama i ETF-ovima. Omogućuje praćenje portfelja, analize i usporedbu s drugim korisnicima bez rizika stvarnog gubitka kapitala.",
    },
    {
      question: "Je li ovo stvarno trgovanje ili simulacija?",
      answer:
        "Sve transakcije unutar platforme su simulirane. Cijene instrumenata temelje se na tržišnim podacima, ali nema kupnje ili prodaje stvarnih financijskih instrumenata.",
    },
    {
      question: "Koja je razlika između Osnovnog i Premium plana?",
      answer:
        "Osnovni plan ima dnevna ograničenja (broj trgovanja i broj instrumenata) i nema pristup kreiranju Mini fondova. Premium plan uklanja ograničenja i uključuje napredne opcije te prioritetnu podršku.",
    },
    {
      question: "Koji su načini plaćanja dostupni za Premium?",
      answer:
        "Premium pretplatu možete platiti putem Stripe-a i PayPala. Naplata se vrši mjesečno, a pretplatu možete otkazati u bilo kojem trenutku.",
    },
    {
      question: "Mogu li otkazati pretplatu u bilo kojem trenutku?",
      answer:
        "Da. Pretplatu možete otkazati u bilo kojem trenutku. Nakon otkazivanja, Premium pogodnosti ostaju aktivne do kraja već plaćenog razdoblja.",
    },
    {
      question: "Što su Mini fondovi?",
      answer:
        "Mini fondovi su popisi instrumenata koje možete kreirati, pratiti i dijeliti s drugim korisnicima. Primjerice, možete složiti 'ETF fond' ili 'Dionice rasta' i pratiti izvedbu.",
    },
    {
      question: "Kako funkcionira uvoz transakcija putem CSV-a?",
      answer:
        "Putem CSV datoteke možete izvesti podatke i uvesti ih na novi račun, također moguće je i uvesti povijest trgovine s brokerskih platformi (podržan je isključivo IBKR). Nakon uvoza, platforma će ažurirati portfelj i prikazati statistike.",
    },
  ];

  const [openIndex, setOpenIndex] = useState<number | null>(0);

  function toggle(index: number) {
    setOpenIndex((prev) => (prev === index ? null : index));
  }

  return (
    <div className="faq-shell">
      <main className="faq-main">
        <section className="faq">
          <div className="faq-container">
            <div className="faq-header">
              <h2 className="faq-title">FAQ</h2>
              <p className="faq-subtitle">
                Najčešća pitanja i odgovori o platformi, pretplatama i
                funkcionalnostima.
              </p>
            </div>

            <div className="faq-list">
              {faqs.map((item, index) => {
                const isOpen = openIndex === index;

                return (
                  <div
                    key={index}
                    className={`faq-item ${isOpen ? "faq-item--open" : ""}`}
                  >
                    <button
                      type="button"
                      className="faq-question"
                      onClick={() => toggle(index)}
                      aria-expanded={isOpen}
                    >
                      <span>{item.question}</span>
                      <span className="faq-icon">{isOpen ? "−" : "+"}</span>
                    </button>

                    <div
                      className={`faq-answer ${isOpen ? "faq-answer--open" : ""}`}
                    >
                      <div className="faq-answer__inner">{item.answer}</div>
                    </div>
                  </div>
                );
              })}
            </div>

            <div className="faq-note">
              <div className="faq-note__title">Niste pronašli odgovor?</div>
              <div className="faq-note__text">
                Kontaktirajte nas putem kontakt forme, a mi ćemo vam odgovoriti u
                najkraćem mogućem roku.
              </div>
            </div>
          </div>
        </section>
      </main>

      <Footer />
    </div>
  );
}

export default FAQ;
