# Content-principe — posten op basis van ontwikkelingen (geen opvulberichten)

**Dit principe staat boven alle subagenten. Geen enkele agent mag hiervan afwijken.**

## De kernregel

Posten is **event-gedreven**, niet volgens een vast roulatieschema. We plaatsen iets omdat er iets te melden is — nooit om een schema te vullen.

## Wat dat concreet betekent

- **Janine** post minimaal **wekelijks** op haar eigen profiel.
- **Tijdgevoelige berichten** (nieuwe klant, felicitaties, fijne feestdagen, een mijlpaal van een medewerker) worden **dezelfde dag of dezelfde week** geplaatst.
- **Ontwikkelingen in de sectoren (pensioen, accountancy) of in de economie/arbeidsmarkt** worden geplaatst **wanneer ze zich voordoen**.
- Betekent dit dat er in een bepaalde week **meer** wordt gepost? Dan is dat prima ("so be it").
- Is er niets relevants te melden? Dan posten we **niet**. Geen post is een prima uitkomst.

## Wat we nooit doen

- Berichten plaatsen om op te vullen of om "aan een aantal te komen".
- Content forceren zonder strekking.

## Verhouding tot timing

De eerder afgesproken momenten (periode rond 08:00, daarna een periode om 11:45, om te vergelijken welk moment beter werkt) zijn **richttijden voor wanneer we posten als er iets te melden is** — geen verplichting om op die momenten iets te plaatsen.

Zie `.github/workflows/weekly-draft.yml`: de repositoryvariabele `POST_SLOT` (`vroeg` of `laat`) bepaalt welk van de twee tijdstippen actief is.

## Wat dit betekent voor de agent

1. Zoek eerst een **aanleiding** in het aangeleverde materiaal: `data/ideas-inbox/` (notities en Plaud-transcripties van Janine en het team), een sectorontwikkeling, of een tijdgevoelige gebeurtenis.
2. Is er een aanleiding? Kies de subagent die erbij hoort en schrijf de post.
3. Is er geen aanleiding? Geef **`GEEN POST: <reden>`** terug. Dat is geen fout — dat is de bedoeling.
4. Zijn er meerdere aanleidingen? Schrijf voor de sterkste. De rest kan een aparte run zijn.
