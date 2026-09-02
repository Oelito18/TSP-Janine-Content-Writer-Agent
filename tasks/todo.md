# Todo — repo bijwerken op basis van Drive "Project Janine"

## Uit te voeren

- [x] `src/send_email.py`: mailen naar twee ontvangers (Janine + Tobias)
- [x] `.env.example` en README-secrets bijwerken
- [x] `.github/workflows/weekly-draft.yml` aanmaken (draft + mail, wisselbaar posttijdstip)
- [x] Vaste rotatie vervangen door het event-gedreven content-principe
- [x] Oude pijlers vervangen door de vijf subagenten uit de briefs
- [x] `config/style-guide.md` vervangen door de definitieve stijlgids uit Drive
- [x] `config/topics.md` herschrijven naar subagent-overzicht
- [x] `prompts/system-prompt.md` afstemmen op event-gedreven werkwijze
- [ ] De veertien echte posts van Janine in `data/style-samples/` zetten
      **Geblokkeerd:** de volledige teksten staan niet als tekst in Drive
      (alleen genoemd in de stijlgids). Aanleveren als los bestand of plakken.
- [x] README "Nog te doen" nalopen en afvinken

## Openstaand voor Olivier (setup, buiten de repo)

- [ ] Resend: API-key aanmaken en afzenderdomein verifiëren
- [ ] `ANTHROPIC_API_KEY` aanmaken
- [ ] Mailadressen Janine + Tobias vastleggen
- [ ] GitHub Secrets zetten: `ANTHROPIC_API_KEY`, `RESEND_API_KEY`,
      `APPROVER_EMAILS`, `SENDER_EMAIL`
- [ ] GitHub Variable `POST_SLOT` zetten op `vroeg` of `laat`

## Review

**Gewijzigd**

- `src/send_email.py` — mailt naar alle adressen uit `APPROVER_EMAILS` (komma-gescheiden), met terugval op `APPROVER_EMAIL` en `SECOND_APPROVER_EMAIL`. Dubbele adressen worden ontdubbeld. Datumformat werkt nu ook op Windows.
- `src/generate_draft.py` — rotatie en `data/rotatie-state.json` zijn weg. De agent krijgt alle vijf briefs mee, bepaalt zelf of er een aanleiding is, en antwoordt met `SUBAGENT: <n>` plus de post of met `GEEN POST: <reden>`. `--pijler` blijft werken als alias voor `--subagent`.
- `.github/workflows/weekly-draft.yml` — nieuw. Twee crons (06:00 en 09:45 UTC), waarvan er één draait op basis van de repositoryvariabele `POST_SLOT`. Commit het concept en mailt daarna. Bij `GEEN POST` gebeurt geen van beide.
- `config/style-guide.md` — vervangen door de definitieve stijlgids uit Drive.
- `config/content-principe.md` — nieuw, met een sectie over wat het principe voor de agent betekent.
- `config/subagenten/` — de vijf briefs.
- `config/topics.md` — rotatie eruit, subagent-overzicht erin; het cyber-on-hold-blok is behouden.
- `config/schrijfregels.md` — behouden als ambachtelijke laag onder de stijlgids; verwijzingen naar oude pijlers bijgewerkt.
- `prompts/system-prompt.md` — event-gedreven werkwijze, vijf subagenten, stijlgids-checklist.
- `.env.example` en README-secrets bijgewerkt; README "Nog te doen" afgevinkt.

**Keuzes die afweken van de letterlijke opdracht**

- De opdracht luidde "vervang `style-guide.md` / `schrijfregels.md` door de definitieve stijlgids". `schrijfregels.md` is niet verwijderd: het bevat de anti-slop- en verhaalregels die de stijlgids niet dubbelt, en de prompt leunt erop. De stijlgids is expliciet leidend gemaakt bij tegenspraak.
- De veertien posts konden niet geplaatst worden: ze staan niet als tekst in Drive.
