"""Mailt een gegenereerd concept ter goedkeuring.

    python src/send_email.py data/drafts/2026-08-17_talentontwikkeling.md
"""

import datetime as dt
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
API = "https://api.resend.com/emails"


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
    naar = os.environ.get("APPROVER_EMAIL")
    van = os.environ.get("SENDER_EMAIL")
    if not all([sleutel, naar, van]):
        sys.exit("RESEND_API_KEY, APPROVER_EMAIL of SENDER_EMAIL ontbreekt.")

    try:
        import requests
    except ImportError:
        sys.exit("requests-package ontbreekt. Draai: pip install -r requirements.txt")

    pijler = pad.stem.split("_", 1)[-1].replace("-", " ")
    datum = dt.date.today().strftime("%-d %B %Y")
    onderwerp = f"[Concept] LinkedIn-post – {datum} – {pijler}"

    html = f"""
    <div style="font-family:Helvetica,Arial,sans-serif;max-width:600px;line-height:1.6">
      <p style="color:#666;font-size:14px">
        Hieronder het concept voor deze week. Antwoord met <strong>akkoord</strong> om te
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
        json={"from": van, "to": [naar], "subject": onderwerp, "html": html},
        timeout=30,
    )
    antwoord.raise_for_status()
    print(f"Concept gemaild naar {naar}: {onderwerp}")


if __name__ == "__main__":
    main()
