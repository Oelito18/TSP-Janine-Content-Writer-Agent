"""Genereert een LinkedIn-conceptpost en schrijft die naar data/drafts/.

Posten is event-gedreven (zie config/content-principe.md): er komt alleen een
concept als er een aanleiding is. Is die er niet, dan geeft het script
"GEEN POST: <reden>" terug en wordt er niets gemaild.

Draait wekelijks via GitHub Actions, of handmatig met:
    python src/generate_draft.py
    python src/generate_draft.py --subagent 2   # forceer een specifieke subagent
    python src/generate_draft.py --dry-run      # geen API-call, toont alleen de prompt
"""

import argparse
import datetime as dt
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "config"
BRIEFS = CONFIG / "subagenten"
DRAFTS = ROOT / "data" / "drafts"
IDEAS = ROOT / "data" / "ideas-inbox"
SAMPLES = ROOT / "data" / "style-samples"

MODEL = os.environ.get("CLAUDE_MODEL", "claude-sonnet-4-6")

# De config staat vol met pijlen en accenten; een Windows-console draait standaard
# op cp1252 en klapt daarop om. Forceer UTF-8 op de uitvoer.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# De vijf subagenten uit de briefs in config/subagenten/. Cyber staat hier
# bewust niet bij: het traineeship is nog in opbouw (zie config/topics.md).
SUBAGENTEN = {
    1: ("Janine persoonlijk", "persoonlijk profiel van Janine", "1-janine-persoonlijk.md"),
    2: ("Pensioen", "TSP-bedrijfspagina", "2-pensioen.md"),
    3: ("Accountancy", "TSP-bedrijfspagina", "3-accountancy.md"),
    4: ("Trainee-ontwikkeling", "TSP-bedrijfspagina", "4-trainee-ontwikkeling.md"),
    5: ("Algemeen/arbeidsmarkt", "TSP-bedrijfspagina", "5-algemeen-arbeidsmarkt.md"),
}

KOP_PATROON = re.compile(r"^\s*SUBAGENT:\s*([1-5])\b.*?$", re.MULTILINE)


def lees(pad: Path) -> str:
    return pad.read_text(encoding="utf-8") if pad.exists() else ""


def naam(nummer: int) -> str:
    return SUBAGENTEN[nummer][0]


def kanaal(nummer: int) -> str:
    return SUBAGENTEN[nummer][1]


def brief(nummer: int) -> str:
    return lees(BRIEFS / SUBAGENTEN[nummer][2])


def verzamel_ideeen() -> str:
    """Notities en Plaud-transcripties. Dit is de bron van de aanleiding."""
    if not IDEAS.exists():
        return ""
    bestanden = sorted(p for p in IDEAS.glob("*.md") if p.name != ".gitkeep")
    return "\n\n---\n\n".join(f"### {p.name}\n{lees(p)}" for p in bestanden)


def verzamel_samples(maximum: int = 5) -> str:
    """Echte, door haar goedgekeurde posts als voorbeeldmateriaal."""
    if not SAMPLES.exists():
        return ""
    bestanden = sorted(
        p for p in SAMPLES.glob("*.md") if p.name not in {".gitkeep", "README.md"}
    )[:maximum]
    return "\n\n---\n\n".join(lees(p) for p in bestanden)


def bouw_prompt(gekozen: int | None) -> str:
    if gekozen:
        opdrachtregel = (
            f"Schrijf één LinkedIn-post voor subagent {gekozen}: {naam(gekozen)} "
            f"(kanaal: {kanaal(gekozen)}).\n"
            "Ook hier geldt het content-principe: is er geen echte aanleiding in het "
            "aangeleverde materiaal, geef dan 'GEEN POST: <reden>' terug."
        )
        briefs = f"\n## Brief van deze subagent\n{brief(gekozen)}"
    else:
        overzicht = "\n".join(
            f"- {n}. {naam(n)} — kanaal: {kanaal(n)}" for n in sorted(SUBAGENTEN)
        )
        opdrachtregel = (
            "Bepaal eerst of er een aanleiding is om te posten. Zo ja, kies de subagent "
            "die bij die aanleiding hoort en schrijf één LinkedIn-post. Zo nee, geef "
            "'GEEN POST: <reden>' terug.\n\nBeschikbare subagenten:\n" + overzicht
        )
        briefs = "\n".join(
            f"\n## Brief subagent {n} — {naam(n)}\n{brief(n)}" for n in sorted(SUBAGENTEN)
        )

    delen = [
        opdrachtregel,
        "\n## Content-principe — dit staat boven alles\n"
        + lees(CONFIG / "content-principe.md"),
        "\n## Schrijfregels — deze gaan boven alle stijlvoorkeuren\n"
        + lees(CONFIG / "schrijfregels.md"),
        "\n## Stijlgids (leidend bij tegenspraak met de schrijfregels)\n"
        + lees(CONFIG / "style-guide.md"),
        "\n## Subagenten-overzicht\n" + lees(CONFIG / "topics.md"),
        briefs,
        "\n## Harde compliance-regels\n" + lees(CONFIG / "compliance.md"),
        "\n## Toegestane cijfers (gebruik NOOIT een cijfer dat hier niet staat)\n"
        + lees(CONFIG / "sector-facts.md"),
    ]

    ideeen = verzamel_ideeen()
    if ideeen:
        delen.append(
            "\n## Aangeleverd materiaal — hier zit de aanleiding\n"
            "Notities en transcripties van Janine en het team. Een post bouw je hier "
            "omheen. Staat er niets bruikbaars in en is er ook geen sector- of "
            "arbeidsmarktontwikkeling die je uit dit materiaal kunt onderbouwen, dan is "
            "'GEEN POST' het juiste antwoord.\n\n" + ideeen
        )
    else:
        delen.append(
            "\n## Aangeleverd materiaal — hier zit de aanleiding\n"
            "Er is deze keer niets aangeleverd in data/ideas-inbox/. Zonder aanleiding "
            "geen post: geef 'GEEN POST: geen aanleiding aangeleverd' terug."
        )

    samples = verzamel_samples()
    if samples:
        delen.append(
            "\n## Voorbeelden van haar eigen goedgekeurde posts — imiteer deze zinsbouw\n"
            + samples
        )

    delen.append(
        "\n## Opdracht\n"
        "Schrijf de post. Loop daarna in stilte de eindcontrole uit de schrijfregels en "
        "de AI-detectie-checklist uit de stijlgids langs, en herschrijf wat er niet "
        "doorheen komt — met name de 'niet X, maar Y'-constructie, verzonnen details, "
        "en zinnen die allemaal even lang zijn.\n\n"
        "Antwoordformaat, precies zo:\n"
        "Regel 1: 'SUBAGENT: <nummer>' (1 t/m 5)\n"
        "Regel 2: '---'\n"
        "Daarna: alleen de definitieve posttekst, klaar om te plakken op LinkedIn — geen "
        "inleiding, geen uitleg, geen controlelijst, geen aanhalingstekens eromheen. "
        "Sluit af met een regel 'Beeldsuggestie: <suggestie + alt-tekst>'.\n\n"
        "Kun je op basis van bovenstaande regels geen verantwoorde post schrijven, of is "
        "er simpelweg geen aanleiding, geef dan in plaats van alles hierboven één regel "
        "terug die begint met 'GEEN POST:' gevolgd door de reden. Dat is een prima "
        "uitkomst."
    )
    return "\n".join(delen)


def genereer(prompt: str) -> str:
    try:
        from anthropic import Anthropic
    except ImportError:
        sys.exit("anthropic-package ontbreekt. Draai: pip install -r requirements.txt")

    sleutel = os.environ.get("ANTHROPIC_API_KEY")
    if not sleutel:
        sys.exit("ANTHROPIC_API_KEY ontbreekt. Zet hem in GitHub Actions Secrets of je .env.")

    client = Anthropic(api_key=sleutel)
    antwoord = client.messages.create(
        model=MODEL,
        max_tokens=2000,
        system=lees(ROOT / "prompts" / "system-prompt.md"),
        messages=[{"role": "user", "content": prompt}],
    )
    return "".join(blok.text for blok in antwoord.content if blok.type == "text").strip()


def splits_antwoord(antwoord: str, gekozen: int | None) -> tuple[int | None, str]:
    """Haalt het subagent-nummer uit de kop en geeft de kale posttekst terug."""
    if antwoord.startswith("GEEN POST:"):
        return gekozen, antwoord

    treffer = KOP_PATROON.search(antwoord)
    if not treffer:
        return gekozen, antwoord

    nummer = int(treffer.group(1))
    rest = antwoord[treffer.end():].lstrip()
    if rest.startswith("---"):
        rest = rest[3:].lstrip()
    return nummer, rest


def slug(tekst: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", tekst.lower()).strip("-")[:40]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--subagent",
        "--pijler",
        dest="subagent",
        type=int,
        choices=sorted(SUBAGENTEN),
        help="Forceer één subagent. Zonder deze vlag kiest de agent zelf, of geeft GEEN POST.",
    )
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    prompt = bouw_prompt(args.subagent)

    if args.dry_run:
        print(prompt)
        return

    antwoord = genereer(prompt)
    nummer, post = splits_antwoord(antwoord, args.subagent)

    if post.startswith("GEEN POST:"):
        print(post)
        print("Geen concept geschreven. Dat is een prima uitkomst — zie config/content-principe.md.")
        if uitvoer := os.environ.get("GITHUB_OUTPUT"):
            with open(uitvoer, "a", encoding="utf-8") as fh:
                fh.write("draft_path=\n")
                fh.write("geen_post=ja\n")
        return

    label = naam(nummer) if nummer in SUBAGENTEN else "onbekend"
    DRAFTS.mkdir(parents=True, exist_ok=True)
    vandaag = dt.date.today().isoformat()
    bestand = DRAFTS / f"{vandaag}_{slug(label)}.md"
    bestand.write_text(
        f"# Concept {vandaag} — {label}\n\n"
        f"*Kanaal: {kanaal(nummer) if nummer in SUBAGENTEN else 'onbekend'}.*\n"
        f"*Status: nog niet goedgekeurd.*\n\n---\n\n{post}\n",
        encoding="utf-8",
    )

    print(f"Concept geschreven naar {bestand.relative_to(ROOT)}")
    # Doorgegeven aan de volgende stap in de GitHub Actions-workflow.
    if uitvoer := os.environ.get("GITHUB_OUTPUT"):
        with open(uitvoer, "a", encoding="utf-8") as fh:
            fh.write(f"draft_path={bestand.relative_to(ROOT).as_posix()}\n")
            fh.write(f"subagent={label}\n")
            fh.write("geen_post=nee\n")


if __name__ == "__main__":
    main()
