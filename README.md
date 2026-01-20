# Brazil Trip Expense Tracker

Expense consolidation and settlement system for the Brazil group trip (Dec 2025 – Jan 2026).

## Summary

- **Total Group Spend:** R$ 72,798.09
- **Total Expenses:** 66
- **Participants:** 10 core + 4 extended

### Core Group
Hayley, Antonio, Alex, Bruna, Estella, Nick, David, Tyler, Joseph, Diego

### Extended (appeared in specific expenses)
Kalle, Olga, Jade, Carol

---

## Files

### Primary Data Files

| File | Description |
|------|-------------|
| **complete_expense_list.csv** | Master ledger with all 66 expenses merged from both sources. Sign convention: negative = owed money (creditor), positive = owes money (debtor). |
| **splitwise.csv** | Raw Splitwise export (29 expenses). Original sign convention differs from master ledger. |
| **merged_messages.md** | Chat history from the group expense tracking conversation (37 expenses extracted). |
| **ifood.md** | Detailed breakdown of the iFood lunch order with per-person meal assignments. |

### Output Files

| File | Description |
|------|-------------|
| **SETTLEMENT.md** | Final settlement plan with net balances and payment instructions (13 transactions). |
| **EXPENSE_ANALYSIS.md** | Comprehensive analysis including expense table, payer breakdown, splitting rules, and deduplication notes. |
| **expenses_by_person.csv** | Summary of expenses grouped by person. |

### Scripts

| File | Description |
|------|-------------|
| **settle_expenses.py** | Calculates net balances and generates optimal settlement plan. Outputs SETTLEMENT.md. |
| **audit_expenses.py** | Audits the expense ledger for issues (row balance, payer amounts, duplicates, split counts). |
| **fix_expenses.py** | Fixes Splitwise sign convention (negates person columns to match chat-ledger convention). |
| **run_curls_merge.py** | Merges curl output files. |
| **download_chatgpt_history.py** | Downloads ChatGPT conversation history. |

### Supporting Files

| File | Description |
|------|-------------|
| **chatgpt_state.json** | State file for ChatGPT history download. |
| **merged_messages.json** | JSON version of merged chat messages. |
| **curls.txt, curls2.txt** | Curl commands used for data extraction. |
| **chat-exports/** | Directory containing raw chat export files. |

---

## Sign Convention

The master ledger uses this convention for person columns:
- **Negative value** = Person is owed money (they paid more than their share)
- **Positive value** = Person owes money (they owe this amount)

Each expense row should sum to zero (balanced).

---

## Data Sources

1. **Chat-ledger (chatgpt):** 37 expenses tracked via group chat with ChatGPT
2. **Splitwise:** 29 expenses after removing 4 duplicates

### Deduplication
4 expenses appeared in both sources and were removed from Splitwise:
- BBQ groceries (R$ 2,025)
- Beach club lunch (R$ 1,870)
- Wine (R$ 272)
- Side expense (R$ 215)

---

## Usage

### Generate Settlement Plan
```bash
python3 settle_expenses.py
```

### Audit Expenses
```bash
python3 audit_expenses.py
```

---

## Final Settlement

**Creditors (owed money):**
- Antonio: R$ 27,177.33
- Nick: R$ 12,070.91
- Kalle, Olga, Carol, Jade: R$ 998.44 combined

**Debtors (owe money):**
- Alex: R$ 8,147.02
- David: R$ 7,418.16
- Diego: R$ 6,766.72
- Joseph: R$ 6,463.60
- Estella: R$ 4,178.87
- Tyler: R$ 3,900.42
- Bruna: R$ 2,890.35
- Hayley: R$ 481.54

See SETTLEMENT.md for the full payment plan.
