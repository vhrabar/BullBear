> 🇭🇷 [Hrvatski](README.md) | 🇬🇧 [English](README.en.md)

<!-- Light mode -->
![FER-UNIZG (light)](assets/logo_light_hr.png#gh-light-mode-only)

<!-- Dark mode -->
![FER-UNIZG (dark)](assets/logo_dark_hr.png#gh-dark-mode-only)


# BullBear
BullBear je brokerska aplikacija za simulirano trgovanje dionicama i ETF-ovima uz tržišne podatke u stvarnom vremen.  Projekt je razvijen na FER, UNIZG u sklopu kolegija Programsko inženjerstvo, s ciljem primjene principa timskog rada, dizajna sustava, dokumentiranja, ispitivanja i modernih metoda razvoja.

Ovaj projekt je reultat timskog rada u sklopu projeknog zadatka kolegija [Programsko inženjerstvo](https://www.fer.unizg.hr/predmet/proinz) na Fakultetu elektrotehnike i računarstva Sveučilišta u Zagrebu. 

# Funkcijski zahtjevi
| ID zahtjeva | Opis                                                                                      | Prioritet | Izvor               | Kriteriji prihvaćanja                                                                                                                                             |
| ----------- |-------------------------------------------------------------------------------------------| --------- | ------------------- |-------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **FZ-1**    | Sustav mora podržavati prijavu i odjavu korisnika.                                        | Visok     | Poslovni zahtjevi   | Korisnik se može uspješno prijaviti putem Google i/ili MS računa i odjaviti bez pogrešaka.                                                                        |
| **FZ-2**    | Sustav mora omogućiti upravljanje profilom i korisničkim podacima.                        | Srednji   | Poslovni zahtjevi   | Korisnik može mijenjati osobne podatke (korisničko ime, profilnu fotografiju, BIO), te spremiti izmjene.                                                          |
| **FZ-3**    | Sustav mora dohvaćati cijene i podatke o instrumentima.                                   | Visok     | Tehnički zahtjevi   | Sustav dohvaća ažurne podatke (cijena, open, close, high, low, volumen, profil korporacije) i koristi caching radi bržeg pristupa i smanjenog opterećenja API-ja. |
| **FZ-4**    | Sustav mora omogućiti pretraživanje instrumenata po nazivu.                               | Srednji   | Korisnički zahtjevi | Upis djelomičnog ili potpunog naziva instrumenta (dionica/ETF) vraća relevantne rezultate.                                                                        |
| **FZ-5**    | Sustav mora omogućiti **simuliranu kupnju i prodaju instrumenata**.                       | Visok     | Poslovni zahtjevi   | Korisnik može simulirano kupovati i prodavati instrumente; sustav bilježi transakcije, ažurira stanje portfelja i prikazuje promjene u stvarnome vremenu.         |
| **FZ-6**    | Sustav mora izračunavati vrijednosti u stvarnome vremenu.                                 | Visok     | Tehnički zahtjevi   | Promjene cijena instrumenata odmah se reflektiraju na ukupnu vrijednost portfelja.                                                                                |
| **FZ-7**    | Sustav mora prikazivati sve relevantne informacije korisniku u grafičkome obliku.         | Srednji   | Korisnički zahtjevi | Grafovi i pokazatelji dinamički prikazuju tržišne promjene i rezultate korisnika.                                                                                 |
| **FZ-8**    | Sustav mora omogućiti upravljanje i brisanje portfelja.                                   | Srednji   | Poslovni zahtjevi   | Korisnik može kreirati, preimenovati i brisati portfelje; sustav automatski ažurira povezane podatke.                                                             |
| **FZ-9**    | Sustav mora omogućiti uvoz i izvoz CSV datoteka s poviješću transakcija.                  | Nizak     | Tehnički zahtjevi   | Korisnik može uvesti i izvesti CSV datoteke s točnim i potpunim zapisima o transakcijama (vrijeme, simbol, opis, tip, količina, cijena, klasa).                   |
| **FZ-10**   | Sustav mora prikazivati sortiranu ljestvicu javnih korisnika prema prinosu.               | Srednji   | Korisnički zahtjevi | Rang lista javnih korisnika automatski se sortira prema postotnom prinosu i redovito ažurira.                                                                     |
| **FZ-11**   | Sustav mora omogućiti kreiranje i upravljanje Mini-Fondovima.                             | Srednji   | Poslovni zahtjevi   | Korisnik može osnovati Mini-Fond (simulirani ETF), dodavati članove i instrumente te pratiti kolektivni prinos.                                                   |
| **FZ-12**   | Sustav mora omogućiti interakciju s drugim korisnicima.                                   | Nizak     | Korisnički zahtjevi | Korisnici mogu međusobno komunicirati, komentirati i dijeliti rezultate simulacija unutar sustava putem vanjske integracije.                                      |
| **FZ-13** | Sustav mora omogućiti kreiranje i upravljanje Mini-Fondovima.                             | Srednji       | Korisnički zahtjevi    | Korisnik može kreirati, uređivati i dijeliti popise omiljenih instrumenata.                                                                                       |
| **FZ-14** | Sustav mora omogućiti kupnju i obnovu premium pretplate.                                  | Visok         | Tehnička specifikacija | Korisnik može uspješno aktivirati i produžiti premium pretplatu uplatom putem PayPala ili kartičnim plačanjem.                                                    |
| **FZ-15** | Sustav mora omogućiti administratorima upravljanje korisnicima i postavljanje cijene pretplate. | Visok         | Poslovna pravila       | Administrator može mijenjati cijene i blokirati korisnike putem administratorskog sučelja.                                                                        |
| **FZ-16** | Sustav mora omogućiti korisnicima da odaberu je li njihov profil javan ili privatan.      | Srednji       | Korisnički zahtjevi    | Korisnik može promijeniti vidljivost profila; privatni profili nisu uključeni u ljestvicu.                                                                        |
| **FZ-17** | Sustav mora omogućiti usporedbu prinosa korisnika s tržišnim indeksima (S&P 500, NASDAQ, EURONEXT 100). | Nizak         | Tehnička specifikacija | Sustav prikazuje grafičku usporedbu prinosa korisnika s indeksima.                                                                                                |
| **FZ-18** | Sustav mora prikazivati pokazatelje rizika, uključujući volatilnost i beta vrijednost.    | Nizak         | Tehnička specifikacija | U sučelju se prikazuju vrijednosti standardne devijacije i beta koeficijenta.                                                                                     |
| **FZ-19** | Sustav mora omogućiti dodavanje i uklanjanje instrumenata s popisa omiljenih instrumenata. | Srednji       | Korisnički zahtjevi    | Korisnik može dodati instrument u popis omiljenih i ukloniti ga po želji.                                                                                         |
                                                             


# Upotrijebljene Tehnologije i Alata
![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=green)
![Django-Rest](https://img.shields.io/badge/django--rest--framework-blue?style=for-the-badge&labelColor=333333&logo=django&logoColor=white&color=blue)
![React](https://img.shields.io/badge/React-61DAFB?logo=react&logoColor=white&style=for-the-badge)
![Vite](https://img.shields.io/badge/Vite-646CFF?style=for-the-badge&logo=Vite&logoColor=white)


![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2CA5E0?style=for-the-badge&logo=docker&logoColor=white)
![NNGINX](https://img.shields.io/badge/Nginx-009639?logo=nginx&logoColor=white&style=for-the-badge)
![DO](https://img.shields.io/badge/DigitalOcean-0080FF?style=for-the-badge&logo=digitalocean&logoColor=white)

![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/Github%20Actions-282a2e?style=for-the-badge&logo=githubactions&logoColor=367cfe)


![VSCode](https://img.shields.io/badge/VSCode-0078D4?style=for-the-badge&logo=visual%20studio%20code&logoColor=white)
![PyCharm Pro](https://img.shields.io/badge/JetBrains%20PyCharm%20Pro-000000?logo=pycharm&logoColor=white&style=for-the-badge)
![DataGrip](https://img.shields.io/badge/JetBrains%20DataGrip-000000?logo=datagrip&logoColor=white&style=for-the-badge)
![Postman](https://img.shields.io/badge/Postman-FF6C37?style=for-the-badge&logo=Postman&logoColor=white)

![Microsoft Teams](https://img.shields.io/badge/Microsoft_Teams-6264A7?style=for-the-badge&logo=microsoft-teams&logoColor=white)


# Instalacija
## Kloniranje repozitorija
```bash
git clone git@github.com:vhrabar/BullBear.git
cd BullBear
```

## Uređivanje varijabli
Nakon unosa svih potrebnih varijabli (Google OAuth, MS OAuth, finnhub.io, baza podataka,...) u `.env.example`
```bash
cp .env.example .env
```

## Pokretanje 
```bash
docker compose up --build
```

## Postavljanje baze
```bash
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py createsuperuser
```

## (Opcionalno) Pokretanje testova
```bash
docker compose exec backend pytest
docker compose exec frontend npm test
```


# Članovi tima 
| Ime i prezime                  | GitHub profil                                        | Uloga u timu                                                | Odgovornosti                                                                                                                                             |
| ------------------------------ | ---------------------------------------------------- | ----------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Vedran Hrabar**              | [@vhrabar](https://github.com/vhrabar)               | Voditelj tima / DevOps / Frontend / Backend / Baze podataka | Koordinira razvojni proces, održava CI/CD okruženja, razvija ključne komponente frontenda i backenda te upravlja bazama podataka.                        |
| **Antun Silov**                | [@AntunSilov](https://github.com/AntunSilov)         | Backend razvojni inženjer                                   | Razvija API funkcionalnosti, implementira poslovnu logiku i održava stabilnost komunikacije s bazom podataka.                                            |
| **Leon Zorko**                 | [@LeonZorko](https://github.com/LeonZorko)           | Frontend razvojni inženjer                                  | Razvija i optimizira React korisničko sučelje, implementira dinamične komponente i vizualizacije podataka te osigurava konzistentno korisničko iskustvo. |
| **Vedran Radojčić**            | [@VedranRadojcic](https://github.com/VedranRadojcic) | Frontend razvojni inženjer                                  | Razvija i optimizira React korisničko sučelje, implementira dinamične komponente i vizualizacije podataka te osigurava konzistentno korisničko iskustvo. |
| **Viktor Lazić**               | [@ViktorLazic3](https://github.com/ViktorLazic3)     | Frontend razvojni inženjer                                  | Razvija i optimizira React korisničko sučelje, implementira dinamične komponente i vizualizacije podataka te osigurava konzistentno korisničko iskustvo. |
| **Luka Varga**                 | [@MegaNoris](https://github.com/MegaNoris)           | Full-stack razvojni inženjer                                | Radi na povezivanju frontenda i backenda, unaprjeđuje performanse sustava i osigurava tehničku stabilnost aplikacije.                                    |



# 📝 Kodeks ponašanja [![Contributor Covenant](https://img.shields.io/badge/Contributor%20Covenant-2.1-4baaaa.svg)](CODE_OF_CONDUCT.md)
Minimumo prihvatljivog ponašanja definiran je u [KODEKS PONAŠANJA STUDENATA FAKULTETA ELEKTROTEHNIKE I RAČUNARSTVA SVEUČILIŠTA U ZAGREBU](https://www.fer.hr/_download/repository/Kodeks_ponasanja_studenata_FER-a_procisceni_tekst_2016%5B1%5D.pdf), te dodatnim naputcima za timski rad na predmetu [Programsko inženjerstvo](https://www.fer.unizg.hr/predmet/proinz).
Pri izradi projekta poštovan je [etički kodeks IEEE-a](https://www.ieee.org/about/corporate/governance/p7-8.html) koji ima važnu obrazovnu funkciju sa svrhom postavljanja najviših standarda integriteta, odgovornog ponašanja i etičkog ponašanja u profesionalnim aktivnosti. Time profesionalna zajednica programskih inženjera definira opća načela koja definiranju  moralni karakter, donošenje važnih poslovnih odluka i uspostavljanje jasnih moralnih očekivanja za sve pripadnike zajenice.

Kodeks ponašanja skup je provedivih pravila koja služe za jasnu komunikaciju očekivanja i zahtjeva za rad zajednice/tima. Njime se jasno definiraju obaveze, prava, neprihvatljiva ponašanja te  odgovarajuće posljedice (za razliku od etičkog kodeksa.


# 📝 Licenca
![GPLv2 License](https://img.shields.io/badge/License-GPL%20v2-blue.svg)

Ovaj projekt je licenciran pod **GNU General Public License v2 (GPL-2.0)**.  
To znači da slobodno možete koristiti, mijenjati i distribuirati ovaj projekt, pod uvjetima koje propisuje GPL v2. Svaka distribucija mora također biti pod istom licencom.

Za više informacija o GPL v2 licenci, posjetite [GNU licencu](https://www.gnu.org/licenses/old-licenses/gpl-2.0.html).


> ### Napomena:
>
> Svi paketi distribuiraju se pod vlastitim licencama.
> Svi upotrijebleni materijali  (slike, modeli, animacije, ...) distribuiraju se pod vlastitim licencama.


### Reference na licenciranje repozitorija

Za smjernice o licenciranju ovog repozitorija i primjeni GPLv2 u praksi pogledati:

- [Službena dokumentacija GNU GPL v2](https://www.gnu.org/licenses/old-licenses/gpl-2.0.html)  
- [GitHub vodič o licencama](https://docs.github.com/en/repositories/managing-your-repository/licensing-a-repository)  
- [Općenite smjernice za otvoreni kod](https://opensource.org/licenses/GPL-2.0)
