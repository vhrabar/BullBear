> 🇭🇷 [Croatian](README.md) | 🇬🇧 [English](README.en.md)

<!-- Light mode -->

![FER-UNIZG (light)](assets/logo_light_eng.png#gh-light-mode-only)

<!-- Dark mode -->

![FER-UNIZG (dark)](assets/logo_dark_eng.png#gh-dark-mode-only)

# BullBear

BullBear is a brokerage application for simulated trading of stocks and ETFs with real-time market data.
The project was developed at FER, University of Zagreb, within the Software Engineering course, with the goal of applying principles of teamwork, system design, documentation, testing, and modern development methodologies.

This project is the result of teamwork within the course project assignment for [Software Engineering](https://www.fer.unizg.hr/en/course/sofeng) at the Faculty of Electrical Engineering and Computing, University of Zagreb.

# Functional Requirements

| Requirement ID | Description                                                                                           | Priority | Source                  | Acceptance Criteria                                                                                                                                    |
| -------------- | ----------------------------------------------------------------------------------------------------- | -------- | ----------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **FR-1**       | The system must support user login and logout.                                                        | High     | Business requirements   | The user can successfully log in using a Google and/or MS account and log out without errors.                                                          |
| **FR-2**       | The system must allow management of profiles and user data.                                           | Medium   | Business requirements   | The user can edit personal data (username, profile picture, bio) and save the changes.                                                                 |
| **FR-3**       | The system must fetch prices and instrument data.                                                     | High     | Technical requirements  | The system fetches up-to-date data (price, open, close, high, low, volume, corporate profile) and uses caching for faster access and reduced API load. |
| **FR-4**       | The system must allow searching for instruments by name.                                              | Medium   | User requirements       | Entering a partial or full instrument name (stock/ETF) returns relevant results.                                                                       |
| **FR-5**       | The system must enable **simulated buying and selling of instruments**.                               | High     | Business requirements   | The user can buy and sell instruments in simulation; the system records transactions, updates the portfolio, and displays real-time changes.           |
| **FR-6**       | The system must calculate values in real time.                                                        | High     | Technical requirements  | Changes in instrument prices are immediately reflected in the total portfolio value.                                                                   |
| **FR-7**       | The system must display all relevant information graphically.                                         | Medium   | User requirements       | Charts and indicators dynamically show market movements and user performance.                                                                          |
| **FR-8**       | The system must allow portfolio management and deletion.                                              | Medium   | Business requirements   | The user can create, rename, and delete portfolios; the system automatically updates related data.                                                     |
| **FR-9**       | The system must allow importing and exporting CSV files with transaction history.                     | Low      | Technical requirements  | The user can import and export CSV files with accurate and complete transaction records (time, symbol, description, type, quantity, price, class).     |
| **FR-10**      | The system must display a sorted leaderboard of public users by return.                               | Medium   | User requirements       | The leaderboard of public users is automatically sorted by percentage return and updated regularly.                                                    |
| **FR-11**      | The system must allow the creation and management of Mini-Funds.                                      | Medium   | Business requirements   | The user can create a Mini-Fund (simulated ETF), add members and instruments, and track collective returns.                                            |
| **FR-12**      | The system must allow interaction between users.                                                      | Low      | User requirements       | Users can communicate, comment, and share simulation results within the system or via external integration.                                            |
| **FR-13**      | The system must allow the creation and management of Mini-Funds.                                      | Medium   | User requirements       | The user can create, edit, and share lists of favorite instruments.                                                                                    |
| **FR-14**      | The system must allow the purchase and renewal of premium subscriptions.                              | High     | Technical specification | The user can successfully activate and renew premium subscriptions via PayPal or card payment.                                                         |
| **FR-15**      | The system must allow administrators to manage users and set subscription prices.                     | High     | Business rules          | The administrator can change prices and block users through the admin interface.                                                                       |
| **FR-16**      | The system must allow users to choose whether their profile is public or private.                     | Medium   | User requirements       | The user can change profile visibility; private profiles are not included in the leaderboard.                                                          |
| **FR-17**      | The system must allow comparison of user returns with market indices (S&P 500, NASDAQ, EURONEXT 100). | Low      | Technical specification | The system displays a graphical comparison of user returns with indices.                                                                               |
| **FR-18**      | The system must display risk indicators, including volatility and beta value.                         | Low      | Technical specification | The interface displays standard deviation and beta coefficient values.                                                                                 |
| **FR-19**      | The system must allow adding and removing instruments from the favorites list.                        | Medium   | User requirements       | The user can add an instrument to favorites and remove it at will.                                                                                     |

# Technologies and Tools Used
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

# Installation

## Cloning the repository
```bash
git clone git@github.com:vhrabar/BullBear.git
cd BullBear
```

## Editing environment variables
After entering all required variables (Google OAuth, MS OAuth, finnhub.io, database, ...) in `.env.example`
```bash
cp .env.example .env
```

## Running the project

```bash
docker compose up --build
```

## Setting up the database

```bash
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py createsuperuser
```

## (Optional) Running tests

```bash
docker compose exec backend pytest
docker compose exec frontend npm test
```

# Team Members

| Name and Surname    | GitHub Profile                                       | Role in Team                                       | Responsibilities                                                                                                                         |
| ------------------- | ---------------------------------------------------- | -------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| **Vedran Hrabar**   | [@vhrabar](https://github.com/vhrabar)               | Team Lead / DevOps / Frontend / Backend / Database | Coordinates the development process, maintains CI/CD environments, develops core frontend and backend components, and manages databases. |
| **Antun Silov**     | [@AntunSilov](https://github.com/AntunSilov)         | Backend Engineer                                   | Develops API functionalities, implements business logic, and maintains stable communication with the database.                           |
| **Leon Zorko**      | [@LeonZorko](https://github.com/LeonZorko)           | Frontend Engineer                                  | Develops and optimizes the React UI, implements dynamic components and data visualizations, ensuring a consistent user experience.       |
| **Vedran Radojčić** | [@VedranRadojcic](https://github.com/VedranRadojcic) | Frontend Engineer                                  | Develops and optimizes the React UI, implements dynamic components and data visualizations, ensuring a consistent user experience.       |
| **Viktor Lazić**    | [@ViktorLazic3](https://github.com/ViktorLazic3)     | Frontend Engineer                                  | Develops and optimizes the React UI, implements dynamic components and data visualizations, ensuring a consistent user experience.       |
| **Luka Varga**      | [@MegaNoris](https://github.com/MegaNoris)           | Full-Stack Engineer                                | Works on connecting frontend and backend, improving system performance, and ensuring technical stability of the application.             |

# 📝 Code of Conduct [![Contributor Covenant](https://img.shields.io/badge/Contributor%20Covenant-2.1-4baaaa.svg)](CODE_OF_CONDUCT.md)

The minimum acceptable behavior is defined by the [CODE OF CONDUCT FOR STUDENTS OF THE FACULTY OF ELECTRICAL ENGINEERING AND COMPUTING, UNIVERSITY OF ZAGREB](https://www.fer.hr/_download/repository/Kodeks_ponasanja_studenata_FER-a_procisceni_tekst_2016%5B1%5D.pdf), as well as additional guidelines for teamwork within the [Software Engineering](https://www.fer.unizg.hr/en/course/sofeng) course.

The project adheres to the [IEEE Code of Ethics](https://www.ieee.org/about/corporate/governance/p7-8.html), which serves an educational purpose in setting the highest standards of integrity, responsibility, and ethical behavior in professional activities. It defines general principles that shape moral character, sound decision-making, and clear moral expectations for the software engineering community.

A code of conduct is a set of enforceable rules that serve to communicate expectations and standards for community/team work. It clearly defines obligations, rights, unacceptable behaviors, and corresponding consequences (unlike a mere ethical code).

# 📝 License

![GPLv2 License](https://img.shields.io/badge/License-GPL%20v2-blue.svg)

This project is licensed under the **GNU General Public License v2 (GPL-2.0)**.
This means you are free to use, modify, and distribute this project under the terms specified by GPL v2. Any redistribution must also be under the same license.

For more information about the GPL v2 license, visit [GNU License](https://www.gnu.org/licenses/old-licenses/gpl-2.0.html).

> ### Note:
>
> All packages are distributed under their respective licenses.
> All materials used (images, models, animations, etc.) are distributed under their own licenses.

### Repository Licensing References

For guidance on licensing this repository and applying GPLv2 in practice, see:

* [Official GNU GPL v2 Documentation](https://www.gnu.org/licenses/old-licenses/gpl-2.0.html)
* [GitHub Licensing Guide](https://docs.github.com/en/repositories/managing-your-repository/licensing-a-repository)
* [General Open Source Guidelines](https://opensource.org/licenses/GPL-2.0)
