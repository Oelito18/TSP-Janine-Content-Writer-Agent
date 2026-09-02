# Subagenten — wie schrijft wat

**Er is geen rotatie meer.** De agent kiest een subagent omdat er een aanleiding is, niet omdat het "zijn beurt" is. Lees eerst `config/content-principe.md`; dat principe staat boven dit bestand. Zonder aanleiding: `GEEN POST: <reden>`.

De volledige briefs staan in `config/subagenten/`.

| # | Subagent | Kanaal | Register | Brief |
|---|---|---|---|---|
| 1 | Janine (persoonlijk) | persoonlijk profiel van Janine | warm, persoonlijk, zelfspot | `subagenten/1-janine-persoonlijk.md` |
| 2 | Pensioen (sector) | TSP-bedrijfspagina | zakelijk-informatief | `subagenten/2-pensioen.md` |
| 3 | Accountancy (sector) | TSP-bedrijfspagina | zakelijk-informatief | `subagenten/3-accountancy.md` |
| 4 | Trainee-ontwikkeling | TSP-bedrijfspagina | warm, trots | `subagenten/4-trainee-ontwikkeling.md` |
| 5 | Algemeen / arbeidsmarkt | TSP-bedrijfspagina | zakelijk-informatief, feitelijk | `subagenten/5-algemeen-arbeidsmarkt.md` |

## Welke aanleiding hoort bij welke subagent

- Een ervaring of observatie van Janine zelf (vaak via Plaud) → **1**
- Nieuwe pensioenregels, transitie-nieuws, DNB, vergrijzing → **2**
- Regelgeving, opleiding of AI in de accountancy → **3**
- Een trainee-mijlpaal, trainingsdag, mentor-moment, nieuwe klant → **4**
- Arbeidsmarktnieuws, krapte, retentie, diversiteit → **5**

Tijdgevoelige berichten (nieuwe klant, felicitaties, mijlpaal van een medewerker, feestdagen) gaan dezelfde dag of week de deur uit en horen meestal bij **4** of **1**.

## ON HOLD — Cyber-traineeship

**De agent mag hier voorlopig GEEN posts over genereren.** Het cyber-traineeship is nog in opbouw en nog niet rond. Tot nader order: geen cyber-content, geen aankondigingen, geen "binnenkort"-posts. Ook niet als een nieuwsbericht over cybersecurity daar aanleiding toe lijkt te geven.

Zodra het live is: haal dit blok weg, haal grens 2 uit `prompts/system-prompt.md`, en voeg een zesde brief toe in `config/subagenten/` plus een regel in `SUBAGENTEN` in `src/generate_draft.py`.
