#!/usr/bin/env python3
"""Minimal Odoo 19 JSON-2 client.

Environment variables:
  ODOO_URL      e.g. https://odoo.example.com
  ODOO_DB       database name, optional if host/dbfilter selects one DB
  ODOO_API_KEY  bearer API key

No secrets should be committed to Git.
"""

from __future__ import annotations

import os
import sys
from typing import Any

import requests


class OdooJson2:
    def __init__(self, base_url: str, api_key: str, db: str | None = None) -> None:
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": "hermes-odoo-json2-example/0.1",
        })
        if db:
            self.session.headers["X-Odoo-Database"] = db

    def call(self, model: str, method: str, **params: Any) -> Any:
        url = f"{self.base_url}/json/2/{model}/{method}"
        response = self.session.post(url, json=params, timeout=30)
        try:
            body = response.json()
        except Exception:
            response.raise_for_status()
            raise
        if not response.ok:
            raise RuntimeError(f"Odoo API error {response.status_code}: {body}")
        return body

    def search_read(self, model: str, domain: list, fields: list[str], limit: int = 10) -> list[dict[str, Any]]:
        return self.call(model, "search_read", domain=domain, fields=fields, limit=limit)


if __name__ == "__main__":
    url = os.environ.get("ODOO_URL")
    key = os.environ.get("ODOO_API_KEY")
    db = os.environ.get("ODOO_DB")
    if not url or not key:
        print("Set ODOO_URL and ODOO_API_KEY", file=sys.stderr)
        sys.exit(2)

    odoo = OdooJson2(url, key, db)
    partners = odoo.search_read(
        "res.partner",
        domain=[["is_company", "=", True]],
        fields=["name", "email", "phone"],
        limit=5,
    )
    for partner in partners:
        print(partner)
