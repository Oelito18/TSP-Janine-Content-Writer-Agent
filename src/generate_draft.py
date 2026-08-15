"""Genereert een LinkedIn-conceptpost en schrijft die naar data/drafts/.

Draait wekelijks via GitHub Actions, of handmatig met:
    python src/generate_draft.py
    python src/generate_draft.py --pijler 2      # forceer een specifieke pijler
    python src/generate_draft.py --dry-run       # geen API-call, toont alleen de prompt
"""

import argparse
import datetime as dt
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "config"
DRAFTS = ROOT / "data" / "drafts"
IDEAS = ROOT / "data" / "ideas-inbox"
SAMPLES = ROOT / "data" / "style-samples"
STATE = ROOT / "data" / "rotatie-state.json"

MODEL = os.environ.get("CLAUDE_MODEL", "claude-sonnet-4-6")

# Actieve pijlers. Cyber staat bewust NIET in deze lijst: het traineeship is nog
# in opbouw. Zodra het live is, voeg je hem hier toe (zie config/topics.md).
PIJLERS = {
    1: "Ondernemer in een mannendominante sector",
    2: "Talentontwikkeling",
    3: "Trainee-ervaringen",
    4: "Sectortrends (pensioenen en accountancy)",
    5: "Actualiteit/opinie",
}


def lees(pad: Path) -> str:
    return pad.read_text(encoding="utf-8") if pad.exists() else ""


def volgende_pijler() -> int:
    """Round-robin over de actieve pijlers, met geheugen tussen runs."""
    vorige = 0
    if STATE.exists():
        try:
            vorige = json.loads(STATE.read_text()).get("laatste_pijler", 0)
        except (json.JSONDecodeError, OSError):
            vorige = 0
    keys = sorted(PIJLERS)
    volgende = keys[(keys.index(vorige) + 1) % len(keys)] if vorige in keys else keys[0]
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps({"laatste_pijler": volgende}, indent=2))
    return volgende


def verzamel_ideeen() -> str:
    """Losse notities van haar krijgen voorrang boven een generiek onderwerp."""
    if not IDEAS.exists():
        return ""
    bestanden = sorted(p for p in IDEAS.glob("*.md") if p.name != ".gitkeep")
    return "\n\n---\n\n".join(f"### {p.name}\n{lees(p)}" for p in bestanden)


def verzamel_samples(maximum: int = 5) -> str:
    """Echte, door haar goedgekeurde posts als voorbeeldmateriaal."""
    if not SAMPLES.exists():
        return ""
    bestanden = sorted(p for p in SAMPLES.glob("*.md") if p.name != ".gitkeep")[:maximum]
    return "\n\n---\n\n".join(lees(p) for p in bestanden)


def bouw_prompt(pijler: int) -> str:
    delen = [
        f"Schrijf één LinkedIn-post voor pijler {pijler}: {PIJLERS[pijler]}.",
        "\n## Schrijfregels — deze gaan boven alle andere voorkeuren\n"
        + lees(CONFIG / "schrijfregels.md"),
        "\n## Schrijfstijl\n" + lees(CONFIG / "style-guide.md"),
        "\n## Contentpijlers\n" + lees(CONFIG / "topics.md"),
        "\n## Harde compliance-regels\n" + lees(CONFIG / "compliance.md"),
        "\n## Toegestane cijfers (gebruik NOOIT een cijfer dat hier niet staat)\n"
        + lees(CONFIG / "sector-facts.md"),
    ]

    ideeen = verzamel_ideeen()
    if ideeen:
        delen.append(
            "\n## Haar eigen aantekeningen — GEBRUIK DEZE BIJ VOORKEUR\n"
            "Deze notities komen rechtstreeks van haar. Als hier iets bruikbaars in staat "
            "voor deze pijler, bouw de post daar dan omheen in plaats van een onderwerp "
            "te verzinnen.\n\n" + ideeen
        )

    samples = verzamel_samples()
    if samples:
        delen.append(
            "\n## Voorbeelden van haar eigen goedgekeurde posts — imiteer deze zinsbouw\n"
            + samples
        )

    delen.append(
        "\n## Opdracht\n"
        "Schrijf de post. Loop daarna in stilte de eindcontrole uit de schrijfregels langs en "
        "herschrijf wat er niet doorheen komt — met name de 'niet X, maar Y'-constructie, "
        "verzonnen details, en zinnen die allemaal even lang zijn.\n"
        "Geef alleen de definitieve posttekst terug, klaar om te plakken op LinkedIn — "
        "geen inleiding, geen uitleg, geen controlelijst, geen aanhalingstekens eromheen. "
        "Als je op basis van bovenstaande regels geen verantwoorde post kunt schrijven "
        "(bijvoorbeeld omdat een trainee-verhaal toestemming vereist die er niet is), "
        "schrijf dan in plaats daarvan één regel die begint met 'GEEN POST:' gevolgd door de reden."
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


def slug(tekst: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", tekst.lower()).strip("-")[:40]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pijler", type=int, choices=sorted(PIJLERS))
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    pijler = args.pijler or volgende_pijler()
    prompt = bouw_prompt(pijler)

    if args.dry_run:
        print(prompt)
        return

    post = genereer(prompt)

    DRAFTS.mkdir(parents=True, exist_ok=True)
    vandaag = dt.date.today().isoformat()
    bestand = DRAFTS / f"{vandaag}_{slug(PIJLERS[pijler])}.md"
    bestand.write_text(
        f"# Concept {vandaag} — {PIJLERS[pijler]}\n\n"
        f"*Status: nog niet goedgekeurd.*\n\n---\n\n{post}\n",
        encoding="utf-8",
    )

    print(f"Concept geschreven naar {bestand.relative_to(ROOT)}")
    # Doorgegeven aan de volgende stap in de GitHub Actions-workflow.
    if uitvoer := os.environ.get("GITHUB_OUTPUT"):
        with open(uitvoer, "a", encoding="utf-8") as fh:
            fh.write(f"draft_path={bestand.relative_to(ROOT)}\n")
            fh.write(f"pijler={PIJLERS[pijler]}\n")


if __name__ == "__main__":
    main()
