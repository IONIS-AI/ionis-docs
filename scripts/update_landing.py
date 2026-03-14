#!/usr/bin/env python3
"""Update ionis-ai.com landing page numbers from ClickHouse.

Queries ClickHouse for current observation counts, signature distributions,
dataset volumes, disk usage, and live solar conditions. Patches the values
into overrides/home.html.

Usage:
    python scripts/update_landing.py [--dry-run] [--ch-host HOST]

Designed to run on the 3-hour cron cycle on 9975WX.
"""

from __future__ import annotations

import argparse
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests

# Band ID → label mapping (ADIF band IDs)
BAND_MAP = {
    102: "160m", 103: "80m", 105: "40m", 106: "30m",
    107: "20m", 108: "17m", 109: "15m", 110: "12m", 111: "10m",
}

HTML_PATH = Path(__file__).resolve().parent.parent / "overrides" / "home.html"


def ch_query(sql: str, host: str) -> list[dict]:
    """Run a ClickHouse query, return rows as list of dicts."""
    r = requests.get(
        f"http://{host}:8123",
        params={"query": f"{sql} FORMAT JSON"},
        timeout=30,
    )
    r.raise_for_status()
    return r.json()["data"]


def ch_scalar(sql: str, host: str):
    """Run a query that returns a single value."""
    rows = ch_query(sql, host)
    return list(rows[0].values())[0] if rows else None


def fmt_count(n: int) -> str:
    """Format a count for display: 14.71B, 14.1M, 39K."""
    if n >= 1e9:
        return f"{n / 1e9:.2f}B"
    if n >= 1e6:
        v = n / 1e6
        return f"{v:.1f}M" if v < 100 else f"{v:.0f}M"
    if n >= 1e3:
        return f"{n / 1e3:.0f}K"
    return str(n)


def fmt_disk(gib: float) -> str:
    """Format GiB as integer."""
    return str(int(round(gib)))


def fetch_data(host: str) -> dict:
    """Fetch all landing page data from ClickHouse."""
    data = {}

    # ── Big numbers ──────────────────────────────────────────
    obs = ch_query(
        "SELECT 'wspr' as src, count() as cnt FROM wspr.bronze "
        "UNION ALL SELECT 'rbn', count() FROM rbn.bronze "
        "UNION ALL SELECT 'contest', count() FROM contest.bronze "
        "UNION ALL SELECT 'pskr', count() FROM pskr.bronze",
        host,
    )
    obs_map = {r["src"]: int(r["cnt"]) for r in obs}
    data["total_obs"] = sum(obs_map.values())
    data["obs"] = obs_map

    sigs = ch_query(
        "SELECT 'wspr' as src, count() as cnt FROM wspr.signatures_v2_terrestrial "
        "UNION ALL SELECT 'rbn', count() FROM rbn.signatures "
        "UNION ALL SELECT 'contest', count() FROM contest.signatures "
        "UNION ALL SELECT 'dxped', count() FROM rbn.dxpedition_signatures",
        host,
    )
    sig_map = {r["src"]: int(r["cnt"]) for r in sigs}
    data["total_sigs"] = sum(sig_map.values())

    disk_raw = ch_scalar(
        "SELECT sum(bytes_on_disk) FROM system.parts WHERE active "
        "AND database IN ('wspr','rbn','contest','pskr','solar',"
        "'training','messages','validation','dxpedition')",
        host,
    )
    data["disk_gib"] = int(disk_raw) / (1024 ** 3)

    # ── Band distribution (all signature tables) ───────────────
    bands = ch_query(
        "SELECT band, sum(cnt) as cnt FROM ("
        "  SELECT band, count() as cnt FROM wspr.signatures_v2_terrestrial GROUP BY band"
        "  UNION ALL SELECT band, count() FROM rbn.signatures GROUP BY band"
        "  UNION ALL SELECT band, count() FROM contest.signatures GROUP BY band"
        "  UNION ALL SELECT band, count() FROM rbn.dxpedition_signatures GROUP BY band"
        ") GROUP BY band ORDER BY band",
        host,
    )
    band_counts = {}
    for r in bands:
        bid = int(r["band"])
        if bid in BAND_MAP:
            band_counts[BAND_MAP[bid]] = int(r["cnt"])
    data["bands"] = band_counts

    # ── Solar / DSCOVR counts ────────────────────────────────
    data["iri_count"] = int(ch_scalar("SELECT count() FROM solar.iri_lookup", host))
    data["dscovr_count"] = int(ch_scalar("SELECT count() FROM solar.dscovr", host))

    # ── Live conditions ──────────────────────────────────────
    cond = ch_query("SELECT solar_flux, kp_index FROM wspr.live_conditions LIMIT 1", host)
    if cond:
        data["sfi"] = int(float(cond[0]["solar_flux"]))
        data["kp"] = round(float(cond[0]["kp_index"]), 1)
    else:
        data["sfi"] = 0
        data["kp"] = 0.0

    return data


def patch_html(html: str, data: dict) -> str:
    """Patch hardcoded values in landing page HTML."""

    # ── Big numbers ──────────────────────────────────────────
    # Pattern: <div class="number">VALUE</div>\n          <div class="unit">LABEL</div>
    def replace_big_num(label: str, value: str, text: str) -> str:
        pattern = (
            r'(<div class="number">)[^<]*(</div>\s*'
            r'<div class="unit">' + re.escape(label) + r'</div>)'
        )
        return re.sub(pattern, rf"\g<1>{value}\g<2>", text)

    html = replace_big_num("Observations", fmt_count(data["total_obs"]), html)
    html = replace_big_num("Signatures", fmt_count(data["total_sigs"]), html)
    html = replace_big_num("GiB on Disk", fmt_disk(data["disk_gib"]), html)

    # ── Band distribution bars ───────────────────────────────
    max_band = max(data["bands"].values()) if data["bands"] else 1
    for band_label, count in data["bands"].items():
        pct = int(round(count / max_band * 100))
        css_class = f"band-{band_label}"
        # Update data-width
        html = re.sub(
            rf'(bar-fill {css_class}" data-width=")[^"]*(")',
            rf"\g<1>{pct}\g<2>",
            html,
        )
        # Update bar-value (next bar-value after this band's bar-fill)
        pattern = (
            rf'(bar-fill {css_class}" data-width="{pct}"></div></div>\s*'
            r'<span class="bar-value">)[^<]*(</span>)'
        )
        html = re.sub(pattern, rf"\g<1>{fmt_count(count)}\g<2>", html)

    # ── Dataset volume bars ──────────────────────────────────
    ds_values = {
        "ds-wspr": data["obs"].get("wspr", 0),
        "ds-rbn": data["obs"].get("rbn", 0),
        "ds-pskr": data["obs"].get("pskr", 0),
        "ds-contest": data["obs"].get("contest", 0),
    }
    max_ds = max(ds_values.values()) if ds_values else 1
    for css_class, count in ds_values.items():
        pct = round(count / max_ds * 100, 1)
        html = re.sub(
            rf'(bar-fill {css_class}" data-width=")[^"]*(")',
            rf"\g<1>{pct}\g<2>",
            html,
        )
        pattern = (
            rf'(bar-fill {css_class}" data-width="{pct}"></div></div>\s*'
            r'<span class="bar-value">)[^<]*(</span>)'
        )
        html = re.sub(pattern, rf"\g<1>{fmt_count(count)}\g<2>", html)

    # Solar IRI bar — uses ds-solar class, match by bar-label "Solar"
    html = re.sub(
        r'(<span class="bar-label">Solar</span>\s*'
        r'<div class="bar-track"><div class="bar-fill ds-solar" data-width=")[^"]*(")'
        ,
        rf"\g<1>40\g<2>",
        html,
    )
    html = re.sub(
        r'(<span class="bar-label">Solar</span>.*?<span class="bar-value">)[^<]*(</span>)',
        rf"\g<1>{fmt_count(data['iri_count'])} IRI\g<2>",
        html,
        flags=re.DOTALL,
    )

    # DSCOVR bar
    html = re.sub(
        r'(<span class="bar-label">DSCOVR</span>.*?<span class="bar-value">)[^<]*(</span>)',
        rf"\g<1>{fmt_count(data['dscovr_count'])} L1\g<2>",
        html,
        flags=re.DOTALL,
    )

    # ── Solar HUD (JavaScript) ───────────────────────────────
    html = re.sub(
        r"(hudSfi\.textContent\s*=\s*')[^']*(')",
        rf"\g<1>{data['sfi']}\g<2>",
        html,
    )
    html = re.sub(
        r"(hudKp\.textContent\s*=\s*')[^']*(')",
        rf"\g<1>{data['kp']}\g<2>",
        html,
    )

    # ── Last updated timestamp ───────────────────────────────
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%MZ")
    # Add or update timestamp in the solar HUD area
    if "hud-updated" in html:
        html = re.sub(
            r'(id="hud-updated">)[^<]*(</)',
            rf"\g<1>{now}\g<2>",
            html,
        )

    return html


def main():
    parser = argparse.ArgumentParser(description="Update landing page from ClickHouse")
    parser.add_argument("--dry-run", action="store_true", help="Print changes, don't write")
    parser.add_argument("--ch-host", default="localhost", help="ClickHouse host (default: localhost)")
    args = parser.parse_args()

    if not HTML_PATH.exists():
        print(f"ERROR: {HTML_PATH} not found", file=sys.stderr)
        sys.exit(1)

    print(f"Querying ClickHouse at {args.ch_host}...")
    data = fetch_data(args.ch_host)

    print(f"  Observations: {fmt_count(data['total_obs'])} ({data['total_obs']:,})")
    print(f"  Signatures:   {fmt_count(data['total_sigs'])} ({data['total_sigs']:,})")
    print(f"  Disk:         {fmt_disk(data['disk_gib'])} GiB")
    print(f"  SFI:          {data['sfi']}  Kp: {data['kp']}")
    print(f"  Bands:        {len(data['bands'])} bands")
    print(f"  IRI:          {fmt_count(data['iri_count'])}  DSCOVR: {fmt_count(data['dscovr_count'])}")

    original = HTML_PATH.read_text(encoding="utf-8")
    patched = patch_html(original, data)

    if original == patched:
        print("No changes needed.")
        return

    if args.dry_run:
        # Show what changed
        orig_lines = original.splitlines()
        patch_lines = patched.splitlines()
        for i, (a, b) in enumerate(zip(orig_lines, patch_lines), 1):
            if a != b:
                print(f"  L{i}: {a.strip()}")
                print(f"    → {b.strip()}")
        print(f"\n{sum(1 for a, b in zip(orig_lines, patch_lines) if a != b)} lines changed (dry run)")
    else:
        HTML_PATH.write_text(patched, encoding="utf-8")
        print(f"Updated {HTML_PATH}")


if __name__ == "__main__":
    main()
