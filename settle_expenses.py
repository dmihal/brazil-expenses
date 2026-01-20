#!/usr/bin/env python3
"""
Brazil Trip Expense Settlement Calculator
Reads complete_expense_list.csv, calculates net balances, and generates optimal settlement plan.
"""

import csv
from collections import defaultdict
from datetime import datetime

PEOPLE = ['Hayley', 'Antonio', 'Alex', 'Bruna', 'Estella', 'Nick', 'David', 'Tyler', 'Joseph', 'Diego', 'Kalle', 'Olga', 'Jade', 'Carol']

def load_expenses(filepath):
    """Load expenses from CSV and return list of expense dicts."""
    expenses = []
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            expenses.append(row)
    return expenses

def calculate_net_balances(expenses):
    """
    Calculate net balance for each person.
    Positive = owes money (debtor)
    Negative = is owed money (creditor)
    """
    balances = defaultdict(float)
    
    for exp in expenses:
        for person in PEOPLE:
            if person in exp and exp[person]:
                try:
                    val = float(exp[person])
                    balances[person] += val
                except ValueError:
                    pass
    
    # Filter out people with zero balance
    return {p: round(b, 2) for p, b in balances.items() if abs(b) > 0.01}

def calculate_optimal_settlements(balances):
    """
    Calculate optimal settlement using greedy algorithm.
    Matches largest debtor with largest creditor to minimize transactions.
    """
    # Separate into debtors (positive balance = owes money) and creditors (negative = owed money)
    debtors = [(p, b) for p, b in balances.items() if b > 0]
    creditors = [(p, -b) for p, b in balances.items() if b < 0]  # Convert to positive for easier math
    
    # Sort by amount (largest first)
    debtors.sort(key=lambda x: x[1], reverse=True)
    creditors.sort(key=lambda x: x[1], reverse=True)
    
    settlements = []
    
    # Convert to mutable lists
    debtors = [[p, b] for p, b in debtors]
    creditors = [[p, b] for p, b in creditors]
    
    while debtors and creditors:
        # Get largest debtor and creditor
        debtor = debtors[0]
        creditor = creditors[0]
        
        # Amount to transfer
        amount = min(debtor[1], creditor[1])
        
        if amount > 0.01:  # Only record meaningful transactions
            settlements.append({
                'from': debtor[0],
                'to': creditor[0],
                'amount': round(amount, 2)
            })
        
        # Update balances
        debtor[1] -= amount
        creditor[1] -= amount
        
        # Remove settled parties
        if debtor[1] < 0.01:
            debtors.pop(0)
        if creditor[1] < 0.01:
            creditors.pop(0)
    
    return settlements

def generate_markdown(balances, settlements, expenses):
    """Generate markdown output for settlement."""
    
    total_spend = sum(float(exp['Total (R$)']) for exp in expenses if exp.get('Total (R$)'))
    
    # Separate creditors and debtors
    creditors = {p: -b for p, b in balances.items() if b < 0}
    debtors = {p: b for p, b in balances.items() if b > 0}
    
    md = []
    md.append("# Brazil Trip Expense Settlement")
    md.append(f"\n**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    md.append(f"\n**Total Group Spend:** R$ {total_spend:,.2f}")
    md.append(f"\n**Total Expenses:** {len(expenses)}")
    
    md.append("\n---\n")
    md.append("## 💰 Net Balances\n")
    md.append("| Person | Net Balance (R$) | Status |")
    md.append("|--------|----------------:|--------|")
    
    # Sort by balance
    sorted_balances = sorted(balances.items(), key=lambda x: x[1])
    for person, balance in sorted_balances:
        if balance < 0:
            status = "🟢 Owed money"
            md.append(f"| **{person}** | {balance:,.2f} | {status} |")
        else:
            status = "🔴 Owes money"
            md.append(f"| {person} | +{balance:,.2f} | {status} |")
    
    md.append("\n---\n")
    md.append("## 📊 Summary\n")
    md.append("### Creditors (Owed Money)\n")
    md.append("| Person | Amount Owed (R$) |")
    md.append("|--------|----------------:|")
    for person, amount in sorted(creditors.items(), key=lambda x: x[1], reverse=True):
        md.append(f"| **{person}** | R$ {amount:,.2f} |")
    md.append(f"\n**Total Owed:** R$ {sum(creditors.values()):,.2f}")
    
    md.append("\n### Debtors (Owe Money)\n")
    md.append("| Person | Amount Owed (R$) |")
    md.append("|--------|----------------:|")
    for person, amount in sorted(debtors.items(), key=lambda x: x[1], reverse=True):
        md.append(f"| {person} | R$ {amount:,.2f} |")
    md.append(f"\n**Total Debt:** R$ {sum(debtors.values()):,.2f}")
    
    md.append("\n---\n")
    md.append("## 💸 Settlement Plan\n")
    md.append(f"**{len(settlements)} transactions** required to settle all debts:\n")
    md.append("| # | From | To | Amount (R$) |")
    md.append("|---|------|-----|------------:|")
    
    for i, s in enumerate(settlements, 1):
        md.append(f"| {i} | {s['from']} | **{s['to']}** | R$ {s['amount']:,.2f} |")
    
    md.append("\n---\n")
    md.append("## 📱 Payment Instructions\n")
    md.append("Copy-paste messages for each person:\n")
    
    # Group settlements by debtor
    by_debtor = defaultdict(list)
    for s in settlements:
        by_debtor[s['from']].append(s)
    
    for debtor, payments in sorted(by_debtor.items()):
        total = sum(p['amount'] for p in payments)
        md.append(f"\n### {debtor}")
        md.append(f"**Total to pay:** R$ {total:,.2f}\n")
        for p in payments:
            md.append(f"- Pay **{p['to']}**: R$ {p['amount']:,.2f}")
    
    md.append("\n---\n")
    md.append("## ✅ Verification\n")
    md.append(f"- Sum of creditor balances: R$ {sum(creditors.values()):,.2f}")
    md.append(f"- Sum of debtor balances: R$ {sum(debtors.values()):,.2f}")
    md.append(f"- Difference: R$ {abs(sum(creditors.values()) - sum(debtors.values())):.2f}")
    
    if abs(sum(creditors.values()) - sum(debtors.values())) < 0.10:
        md.append("\n✅ **Ledger is balanced!**")
    else:
        md.append("\n⚠️ **Warning: Ledger may have rounding discrepancies**")
    
    return "\n".join(md)

def main():
    print("Loading expenses...")
    expenses = load_expenses('complete_expense_list.csv')
    print(f"Loaded {len(expenses)} expenses")
    
    print("Calculating net balances...")
    balances = calculate_net_balances(expenses)
    
    print("\nNet balances:")
    for person, balance in sorted(balances.items(), key=lambda x: x[1]):
        status = "owes" if balance > 0 else "is owed"
        print(f"  {person}: R$ {balance:,.2f} ({status} R$ {abs(balance):,.2f})")
    
    print("\nCalculating optimal settlement...")
    settlements = calculate_optimal_settlements(balances)
    
    print(f"\nSettlement plan ({len(settlements)} transactions):")
    for s in settlements:
        print(f"  {s['from']} → {s['to']}: R$ {s['amount']:,.2f}")
    
    print("\nGenerating markdown...")
    md_content = generate_markdown(balances, settlements, expenses)
    
    output_file = 'SETTLEMENT.md'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(md_content)
    
    print(f"\n✅ Settlement plan written to {output_file}")

if __name__ == '__main__':
    main()
