#!/usr/bin/env python3
"""Legacy XML-RPC example for Odoo 19.

Prefer JSON-2 for new Odoo 19-only integrations. XML-RPC is deprecated in
Odoo 19 and scheduled for removal in Odoo 22.
"""

from __future__ import annotations

import os
import sys
import xmlrpc.client

url = os.environ.get("ODOO_URL")
db = os.environ.get("ODOO_DB")
login = os.environ.get("ODOO_LOGIN")
password_or_key = os.environ.get("ODOO_PASSWORD_OR_API_KEY")

if not all([url, db, login, password_or_key]):
    print("Set ODOO_URL, ODOO_DB, ODOO_LOGIN, ODOO_PASSWORD_OR_API_KEY", file=sys.stderr)
    sys.exit(2)

common = xmlrpc.client.ServerProxy(f"{url.rstrip('/')}/xmlrpc/2/common")
uid = common.authenticate(db, login, password_or_key, {})
if not uid:
    raise SystemExit("authentication failed")

models = xmlrpc.client.ServerProxy(f"{url.rstrip('/')}/xmlrpc/2/object")
partners = models.execute_kw(
    db, uid, password_or_key,
    "res.partner", "search_read",
    [[['is_company', '=', True]]],
    {"fields": ["name", "email", "phone"], "limit": 5},
)
print(partners)
