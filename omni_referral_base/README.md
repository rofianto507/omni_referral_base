# Omni Referral Base

**Version:** 19.0.2.0.0  
**Category:** Sales / Sales  
**License:** OPL-1  
**Author:** [Sel Studio](https://selstudio.id)

---

## Overview

**Omni Referral Base** is the core module for building a multi-tier referral network and sales commission system in Odoo 19. It provides intelligent **gross profit-based commission calculation** to ensure business profitability while managing referral networks and automated commission distributions across multiple referral levels.

The module ensures business profitability by calculating commissions from actual gross profit (Unit Price - Cost Price) rather than total transaction amount, protecting margins across products with different profit levels.

---

## ✨ Features

### Core Features
- 📊 **Multi-Level Commission Rules** — Define commission percentages for each referral depth level based on gross profit
- 👥 **Referral Member Management** — Complete member lifecycle (Draft, Active, Suspended, Terminated) with sponsor hierarchy and member code tracking
- 💰 **Commission Tracking** — Record and monitor commissions generated from referral transactions
- 🔢 **Auto Numbering** — Automatic sequence generation for referral members
- 🪪 **Member Card Report** — Printable member card for each referral member
- ⚙️ **Settings Integration** — Configurable options via Odoo General Settings

### New: Gross Profit-Based Commission (v19.0.2.0.0+)
- 💡 **Gross Profit Commission Calculation** — Commissions calculated from actual gross profit instead of transaction total
- 📈 **Profit Margin Tracking** — Track and monitor profit margin percentage for each transaction
- 💎 **Net Profit Analysis** — View net profit remaining after commission payout
- 🔍 **Advanced Filtering** — Filter commissions by profit margin ranges (High/Medium/Low margin)
- 📊 **Commission Analysis** — Detailed fields showing profit margin % and net profit calculations

### Advanced Features
- 🎯 **Configurable Commission Behavior** — Control how commissions are handled for inactive uplines
- 📱 **Interactive Dashboard** — Real-time KPI cards, commission/member growth charts, top members leaderboard, and pending withdrawal management
- 🌳 **Referral Tree Visualization** — Interactive expandable network tree with member hierarchy
- 💸 **Commission Withdrawal** — Complete workflow: draft → submitted → approved → paid
- ✅ **Auto-Approval Logic** — Automatic commission approval for active uplines based on activity metrics
- 🔄 **Sales Order Integration** — Automatic commission generation/cancellation on SO confirmation/cancellation

---

## Why Gross Profit-Based Calculation?

### Problem with Transaction-Based Commission

Traditional MLM/referral systems calculate commissions as a percentage of total transaction amount, which can be problematic:

```
Commission = Transaction Total × Commission %

Example - Problem:
- Premium Product: Rp 100K (Margin 40%) → Commission 5% = Rp 5K (Profit: Rp 35K) ✅
- Economy Product: Rp 100K (Margin 5%) → Commission 5% = Rp 5K (Profit: Rp 0K) ❌ BREAK-EVEN!
```

This approach doesn't account for different product margins and can result in unprofitable sales.

### Solution: Gross Profit-Based Commission

Calculate commissions from actual profit earned on each sale:

```
Commission = Gross Profit × Commission %
Gross Profit = Unit Price - Cost Price

Example - Solution:
- Premium Product: Profit Rp 40K → Commission 15% = Rp 6K (Net: Rp 34K) ✅
- Standard Product: Profit Rp 15K → Commission 15% = Rp 2.25K (Net: Rp 12.75K) ✅
- Economy Product: Profit Rp 5K → Commission 15% = Rp 750 (Net: Rp 4.25K) ✅
```

**Result:** Every sale remains profitable, regardless of product margin.

---

## Commission Calculation Example

### Scenario: Multiple Products in One Sales Order

| Product | Unit Price | Cost | Qty | Gross Profit | Margin % |
|---------|-----------|------|-----|-------------|----------|
| Premium | Rp 100K | Rp 60K | 1 | Rp 40K | 40% |
| Standard | Rp 100K | Rp 85K | 1 | Rp 15K | 15% |
| Economy | Rp 100K | Rp 95K | 1 | Rp 5K | 5% |
| **TOTAL** | | | | **Rp 60K** | **20%** |

### Commission Distribution (Level 1: 15%, Level 2: 8%)

**Level 1 Commission (Direct Sponsor):**
```
Gross Profit Amount = Rp 60K
Commission Rate = 15%
Commission = Rp 60K × 15% = Rp 9K
Net Profit After Commission = Rp 60K - Rp 9K = Rp 51K
Profit Margin % = (Rp 60K / Rp 300K) × 100 = 20%
```

**Level 2 Commission (Sponsor's Sponsor):**
```
Gross Profit Amount = Rp 60K
Commission Rate = 8%
Commission = Rp 60K × 8% = Rp 4.8K
Net Profit After Commission = Rp 60K - Rp 4.8K = Rp 55.2K
Profit Margin % = (Rp 60K / Rp 300K) × 100 = 20%
```

**Key Insights:**
- ✅ All uplines get appropriate commissions
- ✅ Business maintains healthy profit margin
- ✅ Transparent calculation based on actual profitability

---

## Requirements

- **Odoo Version:** 19.0 (Community or Enterprise)
- **Dependencies:**
  - `base`
  - `sale_management`
  - `mail`
  - `account`

---

## Installation

1. Copy the `omni_referral_base` folder into your Odoo addons directory.
2. Restart the Odoo server.
3. Go to **Apps** menu and search for `Omni Referral Base`.
4. Click **Install**.

---

## Configuration

### Post-Installation Setup

#### A. Configure Product Cost Prices
- Go to **Products** menu
- For each product, ensure **Cost Price** (standard_price) is set correctly
- Cost Price = Sum of material costs, labor, overhead, etc.
- **Important:** Accurate cost pricing is crucial for gross profit calculation

**Example:**
```
Product: Laptop Pro
- Selling Price: Rp 10.000.000
- Cost Price: Rp 6.000.000 (60% COGS)
- Gross Profit: Rp 4.000.000 (40% margin)
```

#### B. Set Up Commission Rules
- Go to **Referral > Configuration > Commission Rules**
- Define commission percentage for each referral depth level
- **Example:**
  - Level 1: 15% (Direct Sponsor)
  - Level 2: 8% (Sponsor's Sponsor)
  - Level 3: 3% (Up to 3 levels deep)

#### C. Configure Referral Settings
- Go to **Settings > General Settings > Referral**
- Set member code prefix (e.g., "REF")
- Configure auto-approval rules for active uplines
- Set active upline check period (days)
- Configure behavior for inactive uplines

#### D. Create Referral Members
- Go to **Referral > Members > Create**
- Link to existing Odoo contact
- Assign sponsor (upline)
- Change state from Draft to Active

---

## Module Structure

```
omni_referral_base/
├── data/
│   ├── sequence.xml              # Auto-numbering for members
│   └── demo.xml                  # Demo data
├── models/
│   ├── __init__.py
│   ├── sale_order.py             # [UPDATED] Enhanced with gross profit calculation
│   ├── commission.py             # [UPDATED] Commission records with profit tracking
│   ├── commission_rule.py        # Commission rules definition
│   ├── commission_withdraw.py    # Withdrawal workflow
│   ├── member.py                 # Referral member management
│   ├── dashboard.py              # Dashboard analytics
│   └── res_config_settings.py    # Configuration
├── views/
│   ├── commission_views.xml      # [UPDATED] Commission list/form/search
│   ├── commission_rule_views.xml # Rules configuration
│   ├── commission_withdraw_views.xml
│   ├── member_views.xml          # Member management
│   ├── sale_order_views.xml      # SO integration
│   ├── dashboard_views.xml       # Dashboard
│   ├── referral_tree_views.xml   # Network tree
│   ├── res_config_settings_views.xml
│   ├── res_partner_views.xml
│   └── menu.xml                  # Menu structure
├── reports/
│   └── member_card_report.xml    # Member card printable report
├── security/
│   ├── security.xml              # Record rules
│   └── ir.model.access.csv       # Model permissions
├── static/
│   ├── description/
│   │   ├── banner.png            # Module banner
│   │   ├── icon.png              # Module icon
│   │   └── index.html            # Module description
│   ├── lib/
│   │   └── echarts.min.js        # Chart library
│   └── src/
│       ├── css/
│       │   ├── dashboard.css
│       │   └── referral_tree.css
│       ├── js/
│       │   ├── dashboard.js
│       │   └── referral_tree_widget.js
│       └── xml/
│           ├── dashboard.xml
│           └── referral_tree_widget.xml
├── wizard/
│   └── withdraw_wizard_views.xml # Withdrawal wizard
├── __manifest__.py               # Module metadata
├── __init__.py
└── README.md
```

---

## Database Models

### Core Models

#### `referral.member`
**Purpose:** Store referral network members

**Key Fields:**
- `name` — Member full name
- `partner_id` — Link to Odoo contact
- `sponsor_id` — Member's upline/sponsor
- `member_code` — Auto-generated unique member code
- `state` — Status (Draft, Active, Suspended, Terminated)
- `commission_balance` — Total approved commissions

#### `referral.commission` ⭐ [UPDATED]
**Purpose:** Track individual commission records

**Key Fields:**
- `sale_order_id` — Link to sales order
- `source_member_id` — Member who made the sale
- `beneficiary_member_id` — Upline receiving commission
- `level_depth` — Referral depth (1, 2, 3, etc.)
- `base_amount` — Total transaction amount (reference)
- `gross_profit_amount` — **[NEW]** Gross profit used for calculation
- `commission_pct` — Commission percentage applied
- `commission_amount` — Final commission amount
- `profit_margin_percent` — **[NEW]** Transaction profit margin %
- `net_profit_after_commission` — **[NEW]** Profit after commission
- `state` — Commission status (Pending, Approved, Rejected, Cancelled)

#### `commission.rule`
**Purpose:** Define commission percentages per level

**Key Fields:**
- `level_depth` — Referral level (1, 2, 3, etc.)
- `commission_pct` — Commission percentage from gross profit
- `name` — Auto-generated name (e.g., "Level 1")

#### `commission.withdraw`
**Purpose:** Manage member withdrawal requests

**Key Fields:**
- `member_id` — Member requesting withdrawal
- `amount` — Withdrawal amount
- `state` — Status (Draft, Submitted, Approved, Paid, Rejected)
- `date_request` — Request date
- `date_paid` — Payment date (if paid)
- `commission_balance_before` — Balance snapshot at request time
- `commission_balance_after` — Balance after withdrawal (computed)

---

## How It Works

### Complete Workflow

1. **Configure Settings** — Set commission rules, product costs, member code prefix
2. **Set Product Costs** — Ensure each product has accurate cost price
3. **Build Network** — Create referral members and assign sponsors
4. **Sales Order Created** — System calculates gross profit from line items
5. **Order Confirmed** — Commissions automatically distributed to upline chain based on gross profit
6. **Dashboard Review** — View pending commissions, top members, withdrawal requests
7. **Approve/Reject** — Manage commissions from dashboard or list view
8. **Process Withdrawals** — Handle member withdrawal requests
9. **Order Cancelled** — Pending commissions automatically cancelled

---

## New Commission Fields (v19.0.2.0.0+)

### Computed Fields

#### `total_gross_profit` (sale.order)
**Formula:** `SUM((unit_price - cost_price) × quantity)`  
**Purpose:** Base amount for all commission calculations

#### `profit_margin_percent` (referral.commission)
**Formula:** `(gross_profit_amount / base_amount) × 100`  
**Purpose:** Transaction profit margin percentage for analytics

#### `net_profit_after_commission` (referral.commission)
**Formula:** `gross_profit_amount - commission_amount`  
**Purpose:** Actual profit remaining for business after commission

---

## Dashboard Features

### KPI Cards
- Total Members (All time)
- Active Members (All time)
- Commission Approved (Period-based)
- Withdrawal Paid (Period-based)

### Charts
- Commission Trend (Bar chart)
- Member Growth (Line chart)

### Sections
- Top 5 Members (by commission balance)
- Pending Withdrawals (with approve/reject buttons)

### Period Selection
- This Month
- Last 3 Months
- Last 6 Months
- This Year

---

## Version History

### v19.0.2.0.0 (Latest)
**Release Date:** 2026-06-03

**New Features:**
- ✨ Gross profit-based commission calculation
- ✨ Profit margin tracking & analysis
- ✨ Net profit after commission calculation
- ✨ Advanced commission filtering by margin
- ✨ Dashboard with pending withdrawals panel

**Enhancements:**
- 🔧 Enhanced sale_order.py with gross profit computation
- 🔧 Enhanced commission.py with profit tracking fields
- 🔧 Updated commission_views.xml with new columns
- 🔧 Improved dashboard with withdrawal management

### v19.0.1.0.0
**Release Date:** 2026-05-29

**Initial Features:**
- ✅ Referral member management with lifecycle states
- ✅ Multi-level commission rules
- ✅ Auto-numbering for member codes
- ✅ Commission tracking and approval workflow
- ✅ Commission withdrawal management
- ✅ Interactive dashboard with KPIs
- ✅ Referral network tree visualization
- ✅ Member card printable report

---

## Troubleshooting

### Products showing zero profit
**Solutions:**
- Check product **Cost Price** (standard_price) is set
- Ensure Cost Price < Selling Price
- For multi-variant products, set cost on variant level

### Commissions not generating
**Solutions:**
- Check **Commission Rules** are defined
- Check referral member is **Active** state
- Check sponsor hierarchy is set correctly
- Check sale order is **Confirmed** state

### Incorrect profit margin percentages
**Solutions:**
- Verify product cost prices are accurate
- Check line item calculations in sales order
- Verify gross profit amount displays correctly

---

## Support & Contact

For support, bug reports, or feature requests:

📧 **Email:** [support@selstudio.id](mailto:support@selstudio.id)  
🌐 **Website:** [https://selstudio.id](https://selstudio.id)

---

## License

This module is licensed under the **Odoo Proprietary License (OPL-1)**.

For full license details: [OPL-1 License](https://www.odoo.com/documentation/19.0/licenses/licenses.html#opl-1)

---

## Author

**Sel Studio**  
Building business automation solutions for Odoo  
📧 support@selstudio.id  
🌐 https://selstudio.id

---

**Last Updated:** June 3, 2026  
**Version:** 19.0.2.0.0
