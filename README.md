# Content Writer Agent — LinkedIn

Schrijft LinkedIn-conceptposts in Janines stem, mailt die ter goedkeuring naar Janine en Tobias, en publiceert niets zonder akkoord.

## Hoe het werkt

1. GitHub Actions draait wekelijks `src/generate_draft.py`.
2. Het script leest het content-principe, de stijlgids en de vijf subagent-briefs, en kijkt of er een **aanleiding** is in `data/ideas-inbox/`.
3. Is er een aanleiding? Dan kiest de agent de bijpassende subagent en schrijft één post. Het concept komt in `data/drafts/` en wordt gemaild via `src/send_email.py`.
4. Is er geen aanleiding? Dan geeft de agent `GEEN POST: <reden>` terug en wordt er niets gemaild. Dat is een prima uitkomst.
5. Janine of Tobias antwoordt met akkoord of met aanpassingen.
6. Na akkoord verplaats je het bestand naar `outbox/approved/` en wordt het handmatig op LinkedIn geplaatst.

## Event-gedreven, geen rotatie

Er is geen vaste pijler-rotatie meer. We posten omdat er iets te melden is, nooit om een schema te vullen. Janine post minimaal wekelijks; tijdgevoelige items (nieuwe klant, felicitaties, mijlpaal van een medewerker) en sector- of arbeidsmarktontwikkelingen kunnen extra posts opleveren. De volledige regel staat in `config/content-principe.md`.

## De vijf subagenten

| # | Subagent | Kanaal |
|---|---|---|
| 1 | Janine persoonlijk | persoonlijk profiel van Janine |
| 2 | Pensioen (sector) | TSP-bedrijfspagina |
| 3 | Accountancy (sector) | TSP-bedrijfspagina |
| 4 | Trainee-ontwikkeling | TSP-bedrijfspagina |
| 5 | Algemeen / arbeidsmarkt | TSP-bedrijfspagina |

De briefs staan in `config/subagenten/`.

## Structuur

| Map | Wat erin hoort |
|---|---|
| `config/` | Alle regels: content-principe, stijlgids, schrijfregels, subagent-briefs, compliance, sectorcijfers met bron |
| `config/subagenten/` | De vijf briefs, één bestand per subagent |
| `prompts/` | De system prompt met de vier harde grenzen |
| `data/drafts/` | Elk gegenereerd concept, gedateerd — ook de afgekeurde |
| `data/style-samples/` | Haar eigen goedgekeurde posts; hoe meer hier staan, hoe beter de stem wordt |
| `data/ideas-inbox/` | Notities en Plaud-transcripties. Hier zit de aanleiding om te posten |
| `outbox/approved/` | Goedgekeurd, klaar om te posten |
| `docs/` | Toestemmingsformulier voor trainees |

## Aan de slag

```bash
pip install -r requirements.txt
cp .env.example .env        # vul je sleutels in
```

```bash
python src/generate_draft.py --dry-run
```

```bash
python src/generate_draft.py --subagent 4
```

```bash
python src/send_email.py data/drafts/<bestand>
```

Secrets horen in GitHub → Settings → Secrets and variables → Actions:
`ANTHROPIC_API_KEY`, `RESEND_API_KEY`, `APPROVER_EMAILS` (komma-gescheiden: Janine, Tobias), `SENDER_EMAIL`.

Variabelen (zelfde scherm, tabblad Variables): `POST_SLOT` op `vroeg` (~08:00) of `laat` (~11:45), en optioneel `CLAUDE_MODEL`.

## Vier harde grenzen

De agent schrijft liever géén post dan een post die een van deze regels breekt. Bij twijfel geeft hij `GEEN POST: <reden>` terug en wordt er niets gemaild.

1. **Geen verzonnen cijfers** — alleen wat in `config/sector-facts.md` staat.
2. **Geen cyber-content** — het traineeship is nog in opbouw. De structuur staat klaar, de inhoud staat uit.
3. **Geen trainee zonder schriftelijke toestemming** — zie `docs/toestemmingsformulier-trainees.md`.
4. **Geen financieel advies** — ervaring en opinie mogen, aanbevelingen niet (Wft).

## Nog te doen

- [x] Interview met Janine verwerken — `config/style-guide.md` bevat de definitieve stijlgids
- [x] Vaste rotatie vervangen door het event-gedreven content-principe
- [x] De vijf subagent-briefs in `config/subagenten/`
- [x] Concepten naar twee goedkeurders (Janine en Tobias)
- [x] `.github/workflows/weekly-draft.yml` aangemaakt, met wisselbaar posttijdstip via `POST_SLOT`
- [ ] Haar eigen teksten in `data/style-samples/` zetten — de veertien posts staan nog niet als tekst in Drive, zie `data/style-samples/README.md`
- [ ] Bronnenlijsten aanvullen in de briefs 2, 3 en 5 (Janine/Tobias)
- [ ] Cyber-subagent activeren zodra het traineeship rond is: verwijder het on-hold-blok in `config/topics.md` en grens 2 in `prompts/system-prompt.md`, voeg een zesde brief toe in `config/subagenten/` plus een regel in `SUBAGENTEN` in `src/generate_draft.py`, en vul de cyber-cijfers aan in `config/sector-facts.md`
- [ ] `config/sector-facts.md` elk kwartaal controleren — cijfers verouderen
- [ ] Setup buiten de repo: Resend-key plus domeinverificatie, `ANTHROPIC_API_KEY`, mailadressen van Janine en Tobias, en de GitHub Secrets en Variables hierboven
