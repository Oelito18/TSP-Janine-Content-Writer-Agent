# Content Writer Agent — LinkedIn

Schrijft wekelijks een LinkedIn-conceptpost in Janines stem, mailt die ter goedkeuring, en publiceert niets zonder haar akkoord.

## Hoe het werkt

1. GitHub Actions draait elke maandagochtend `src/generate_draft.py`.
2. Het script kiest de volgende pijler uit de rotatie, bouwt een prompt uit alles in `config/`, en vraagt Claude om een post.
3. Het concept komt in `data/drafts/` en wordt gemaild via `src/send_email.py`.
4. Janine antwoordt met akkoord of met aanpassingen.
5. Na akkoord verplaats je het bestand naar `outbox/approved/` en post ze het zelf op LinkedIn.

## Structuur

| Map | Wat erin hoort |
|---|---|
| `config/` | Alle regels: pijlers, schrijfstijl, beeldstijl, compliance, sectorcijfers met bron |
| `prompts/` | De system prompt met de vier harde grenzen |
| `data/drafts/` | Elk gegenereerd concept, gedateerd — ook de afgekeurde |
| `data/style-samples/` | Haar eigen goedgekeurde posts; hoe meer hier staan, hoe beter de stem wordt |
| `data/ideas-inbox/` | Losse notities van haar. Krijgen voorrang boven verzonnen onderwerpen |
| `outbox/approved/` | Goedgekeurd, klaar om te posten |
| `docs/` | Toestemmingsformulier voor trainees |

## Aan de slag

```bash
pip install -r requirements.txt
cp .env.example .env        # vul je sleutels in

python src/generate_draft.py --dry-run          # toont de prompt, geen API-call
python src/generate_draft.py --pijler 4         # forceer een pijler
python src/send_email.py data/drafts/<bestand>  # mail een concept
```

Secrets horen in GitHub → Settings → Secrets and variables → Actions:
`ANTHROPIC_API_KEY`, `RESEND_API_KEY`, `APPROVER_EMAIL`, `SENDER_EMAIL`.

## Vier harde grenzen

De agent schrijft liever géén post dan een post die een van deze regels breekt. Bij twijfel geeft hij `GEEN POST: <reden>` terug en wordt er niets gemaild.

1. **Geen verzonnen cijfers** — alleen wat in `config/sector-facts.md` staat.
2. **Geen cyber-content** — het traineeship is nog in opbouw. De structuur staat klaar, de inhoud staat uit.
3. **Geen trainee zonder schriftelijke toestemming** — zie `docs/toestemmingsformulier-trainees.md`.
4. **Geen financieel advies** — ervaring en opinie mogen, aanbevelingen niet (Wft).

## Nog te doen

- [ ] Interview met Janine (zie het interviewdocument in Drive) — daarna `config/style-guide.md` bijwerken
- [ ] Haar eigen teksten in `data/style-samples/` zetten
- [ ] Cyber-pijler activeren zodra het traineeship rond is: verwijder de on-hold-blokken in `config/topics.md` en `prompts/system-prompt.md`, voeg pijler 6 toe in `src/generate_draft.py`, en vul de cyber-cijfers aan in `config/sector-facts.md`
- [ ] Posttijdstip in `.github/workflows/weekly-draft.yml` afstemmen op haar voorkeur
- [ ] `config/sector-facts.md` elk kwartaal controleren — cijfers verouderen
