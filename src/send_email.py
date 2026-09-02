"""Mailt een gegenereerd concept ter goedkeuring.

    python src/send_email.py data/drafts/2026-08-17_talentontwikkeling.md
"""

import datetime as dt
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
API = "https://api.resend.com/emails"

# Een Windows-console draait standaard op cp1252 en klapt om op accenten en
# streepjes uit de posttekst. Forceer UTF-8 op de uitvoer.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def ontvangers() -> list[str]:
    """Alle goedkeurders: Janine en Tobias.

    Voorkeur: APPROVER_EMAILS als komma-gescheiden lijst. De oudere
    APPROVER_EMAIL en SECOND_APPROVER_EMAIL blijven werken, zodat een
    half-ingevulde .env of Secrets-set niet stilletjes één adres overslaat.
    """
    rauw = os.environ.get("APPROVER_EMAILS", "")
    adressen = [deel.strip() for deel in rauw.split(",")]
    adressen += [
        os.environ.get("APPROVER_EMAIL", "").strip(),
        os.environ.get("SECOND_APPROVER_EMAIL", "").strip(),
    ]

    uniek: list[str] = []
    for adres in adressen:
        if adres and adres not in uniek:
            uniek.append(adres)
    return uniek


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit("Gebruik: python src/send_email.py <pad-naar-concept>")

    pad = ROOT / sys.argv[1] if not Path(sys.argv[1]).is_absolute() else Path(sys.argv[1])
    if not pad.exists():
        sys.exit(f"Bestand niet gevonden: {pad}")

    inhoud = pad.read_text(encoding="utf-8")
    body = inhoud.split("---", 2)[-1].strip()

    if body.startswith("GEEN POST:"):
        print(f"Agent heeft bewust geen post geschreven — niets gemaild.\n{body}")
        return

    sleutel = os.environ.get("RESEND_API_KEY")
    naar = ontvangers()
    van = os.environ.get("SENDER_EMAIL")
    if not sleutel or not naar or not van:
        sys.exit(
            "RESEND_API_KEY, APPROVER_EMAILS of SENDER_EMAIL ontbreekt. "
            "APPROVER_EMAILS is komma-gescheiden, bijv. janine@…,tobias@…"
        )

    try:
        import requests
    except ImportError:
        sys.exit("requests-package ontbreekt. Draai: pip install -r requirements.txt")

    subagent = pad.stem.split("_", 1)[-1].replace("-", " ")
    vandaag = dt.date.today()
    datum = f"{vandaag.day}-{vandaag.month}-{vandaag.year}"
    onderwerp = f"[Concept] LinkedIn-post – {datum} – {subagent}"

    html = f"""
    <div style="font-family:Helvetica,Arial,sans-serif;max-width:600px;line-height:1.6">
      <p style="color:#666;font-size:14px">
        Hieronder een concept. Janine of Tobias: antwoord met <strong>akkoord</strong> om te
        publiceren, of stuur je aanpassingen terug — die gebruiken we ook om de stijl
        verder bij te schaven.
      </p>
      <div style="border-left:3px solid #4162d7;padding:12px 20px;margin:24px 0;
                  background:#fafafa;white-space:pre-wrap">{body}</div>
      <p style="color:#999;font-size:12px">
        Automatisch gegenereerd concept. Er wordt niets gepubliceerd zonder jouw akkoord.
      </p>
    </div>
    """

    antwoord = requests.post(
        API,
        headers={"Authorization": f"Bearer {sleutel}", "Content-Type": "application/json"},
        json={"from": van, "to": naar, "subject": onderwerp, "html": html},
        timeout=30,
    )
    antwoord.raise_for_status()
    print(f"Concept gemaild naar {', '.join(naar)}: {onderwerp}")


if __name__ == "__main__":
    main()
