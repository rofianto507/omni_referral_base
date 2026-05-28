# Omni Referral Base

**Version:** 19.0.1.0.0  
**Category:** Sales / Sales  
**License:** LGPL-3  
**Author:** [Sel Studio](https://selstudio.id)

---

## Overview

**Omni Referral Base** is the core module for building a multi-tier referral network and sales commission system in Odoo. It provides the foundational structure for managing referral members, commission rules, and automated commission calculations across multiple referral levels.

---

## Features

- 📊 **Multi-Level Commission Rules** — Define commission percentages for each referral depth level (e.g., Level 1 = Direct Sponsor, Level 2 = Upline's Upline, etc.)
- 👥 **Referral Member Management** — Track referral networks and member relationships
- 💰 **Commission Tracking** — Record and monitor commissions generated from referral transactions
- 🔢 **Auto Numbering** — Automatic sequence generation for referral members
- 🪪 **Member Card Report** — Printable member card for each referral member
- ⚙️ **Settings Integration** — Configurable options via Odoo General Settings

---

## Requirements

- **Odoo Version:** 19.0
- **Dependencies:**
  - `base`
  - `sale`
  - `mail`

---

## Installation

1. Copy the `omni_referral_base` folder into your Odoo addons directory.
2. Restart the Odoo server.
3. Go to **Apps** menu and search for `Omni Referral Base`.
4. Click **Install**.

---

## Configuration

After installation:

1. Go to **Referral > Configuration > Commission Rules**.
2. Define commission percentage for each depth level.
3. Configure additional settings via **Settings > Referral**.

---

## Module Structure

```
omni_referral_base/
├── data/               # Sequence data
├── models/             # Business logic (Commission Rules, Members, etc.)
├── reports/            # Member card report template
├── security/           # Access control rules
├── static/             # Assets (icons, images)
├── views/              # UI views and menus
├── wizard/             # Import wizard
├── __manifest__.py
└── __init__.py
```

---

## Author

**Sel Studio**  
🌐 [https://selstudio.id](https://selstudio.id)

---

## License

This module is licensed under the [GNU Lesser General Public License v3 (LGPL-3)](https://www.gnu.org/licenses/lgpl-3.0.html).
