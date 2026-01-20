#!/usr/bin/env python3
"""
Audit script to verify expense data integrity and find potential issues.
"""

import csv
from collections import defaultdict

PEOPLE = ['Hayley', 'Antonio', 'Alex', 'Bruna', 'Estella', 'Nick', 'David', 'Tyler', 'Joseph', 'Diego', 'Kalle', 'Olga', 'Jade', 'Carol']

def load_expenses(filepath):
    """Load expenses from CSV."""
    expenses = []
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, start=2):  # Start at 2 for CSV line numbers
            row['_line'] = i
            expenses.append(row)
    return expenses

def audit_row_balance(expenses):
    """Check that each expense row sums to zero (balanced)."""
    print("\n=== AUDIT 1: Row Balance Check ===")
    issues = []
    
    for exp in expenses:
        total = 0
        for person in PEOPLE:
            if person in exp and exp[person]:
                try:
                    total += float(exp[person])
                except ValueError:
                    pass
        
        if abs(total) > 0.10:  # Allow small rounding errors
            issues.append({
                'line': exp['_line'],
                'expense': exp.get('Expense', 'Unknown'),
                'total': exp.get('Total (R$)', '?'),
                'row_sum': total
            })
            print(f"  ⚠️  Line {exp['_line']}: '{exp.get('Expense', 'Unknown')}' - Row sum: {total:.2f} (should be ~0)")
    
    if not issues:
        print("  ✅ All rows balanced!")
    return issues

def audit_payer_amounts(expenses):
    """Check that payer's negative amount matches total - their share."""
    print("\n=== AUDIT 2: Payer Amount Check ===")
    issues = []
    
    for exp in expenses:
        payer = exp.get('Payer', '')
        total_str = exp.get('Total (R$)', '')
        
        if not payer or not total_str:
            continue
            
        try:
            total = float(total_str)
        except ValueError:
            continue
        
        if payer not in PEOPLE:
            continue
            
        payer_amount = 0
        if payer in exp and exp[payer]:
            try:
                payer_amount = float(exp[payer])
            except ValueError:
                pass
        
        # Count how many people have non-zero shares
        participants = []
        for person in PEOPLE:
            if person in exp and exp[person]:
                try:
                    val = float(exp[person])
                    if val != 0:
                        participants.append((person, val))
                except ValueError:
                    pass
        
        # Payer should have negative value (they're owed money)
        if payer_amount >= 0:
            issues.append({
                'line': exp['_line'],
                'expense': exp.get('Expense', 'Unknown'),
                'payer': payer,
                'payer_amount': payer_amount,
                'issue': 'Payer has non-negative amount'
            })
            print(f"  ⚠️  Line {exp['_line']}: '{exp.get('Expense', 'Unknown')}' - Payer {payer} has {payer_amount:.2f} (should be negative)")
    
    if not issues:
        print("  ✅ All payer amounts look correct!")
    return issues

def audit_split_math(expenses):
    """Check that per-person amounts are reasonable given total and split count."""
    print("\n=== AUDIT 3: Split Math Check ===")
    issues = []
    
    for exp in expenses:
        total_str = exp.get('Total (R$)', '')
        notes = exp.get('Notes', '')
        
        if not total_str:
            continue
            
        try:
            total = float(total_str)
        except ValueError:
            continue
        
        # Count participants (people with non-zero amounts)
        participant_count = 0
        amounts = []
        for person in PEOPLE:
            if person in exp and exp[person]:
                try:
                    val = float(exp[person])
                    if val != 0:
                        participant_count += 1
                        amounts.append(abs(val))
                except ValueError:
                    pass
        
        # Check if split count in notes matches actual count
        if 'Split' in notes:
            import re
            match = re.search(r'Split\s*(\d+)', notes)
            if match:
                stated_split = int(match.group(1))
                if stated_split != participant_count:
                    issues.append({
                        'line': exp['_line'],
                        'expense': exp.get('Expense', 'Unknown'),
                        'stated_split': stated_split,
                        'actual_count': participant_count,
                        'issue': 'Split count mismatch'
                    })
                    print(f"  ⚠️  Line {exp['_line']}: '{exp.get('Expense', 'Unknown')}' - Notes say Split {stated_split} but {participant_count} people have amounts")
    
    if not issues:
        print("  ✅ Split counts match!")
    return issues

def audit_duplicate_amounts(expenses):
    """Look for potential duplicate expenses based on amount and payer."""
    print("\n=== AUDIT 4: Potential Duplicates Check ===")
    
    # Group by (amount, payer)
    by_amount_payer = defaultdict(list)
    for exp in expenses:
        total_str = exp.get('Total (R$)', '')
        payer = exp.get('Payer', '')
        source = exp.get('Source', '')
        
        if total_str:
            try:
                total = float(total_str)
                key = (total, payer)
                by_amount_payer[key].append({
                    'line': exp['_line'],
                    'expense': exp.get('Expense', 'Unknown'),
                    'source': source
                })
            except ValueError:
                pass
    
    found = False
    for (amount, payer), items in by_amount_payer.items():
        if len(items) > 1:
            # Check if they're from different sources (potential dup)
            sources = set(item['source'] for item in items)
            if len(sources) > 1:
                found = True
                print(f"  ⚠️  R$ {amount:.2f} paid by {payer} appears {len(items)} times from different sources:")
                for item in items:
                    print(f"      Line {item['line']}: '{item['expense']}' (source: {item['source']})")
    
    if not found:
        print("  ✅ No obvious cross-source duplicates found!")

def audit_hayley_vs_everyone(expenses):
    """Check if Hayley is correctly excluded from boat/late expenses."""
    print("\n=== AUDIT 5: Hayley Exclusion Check ===")
    
    boat_expenses = [exp for exp in expenses if 'boat' in exp.get('Expense', '').lower() or 'boat' in exp.get('Notes', '').lower()]
    
    for exp in boat_expenses:
        hayley_val = exp.get('Hayley', '')
        if hayley_val:
            try:
                val = float(hayley_val)
                if val != 0:
                    print(f"  ⚠️  Line {exp['_line']}: '{exp.get('Expense', 'Unknown')}' - Hayley has {val:.2f} but might not have been on boat")
            except ValueError:
                pass
    
    print("  ℹ️  Manual check recommended for boat-related exclusions")

def audit_net_balances(expenses):
    """Calculate and display net balances."""
    print("\n=== AUDIT 6: Net Balance Summary ===")
    
    balances = defaultdict(float)
    for exp in expenses:
        for person in PEOPLE:
            if person in exp and exp[person]:
                try:
                    val = float(exp[person])
                    balances[person] += val
                except ValueError:
                    pass
    
    # Filter active participants
    active = {p: round(b, 2) for p, b in balances.items() if abs(b) > 0.01}
    
    total_positive = sum(b for b in active.values() if b > 0)
    total_negative = sum(b for b in active.values() if b < 0)
    
    print(f"\n  Total debtors owe: R$ {total_positive:,.2f}")
    print(f"  Total creditors owed: R$ {abs(total_negative):,.2f}")
    print(f"  Difference: R$ {total_positive + total_negative:.2f}")
    
    if abs(total_positive + total_negative) > 1.0:
        print("  ⚠️  WARNING: Ledger is unbalanced by more than R$ 1.00!")
    else:
        print("  ✅ Ledger is balanced!")
    
    print("\n  Per-person balances:")
    for person, balance in sorted(active.items(), key=lambda x: x[1]):
        status = "owes" if balance > 0 else "is owed"
        print(f"    {person}: R$ {balance:,.2f} ({status} R$ {abs(balance):,.2f})")

def check_dinner_expense(expenses):
    """Specifically check the early dinner expense for correct split."""
    print("\n=== AUDIT 7: Early Dinner (R$ 1388.80) Check ===")
    
    for exp in expenses:
        if 'Dinner (early trip)' in exp.get('Expense', '') or exp.get('Total (R$)') == '1388.8':
            print(f"  Found: Line {exp['_line']} - {exp.get('Expense')}")
            print(f"    Total: R$ {exp.get('Total (R$)')}")
            print(f"    Payer: {exp.get('Payer')}")
            print(f"    Notes: {exp.get('Notes')}")
            
            # Check who has amounts
            participants = []
            for person in PEOPLE:
                if person in exp and exp[person]:
                    try:
                        val = float(exp[person])
                        if val != 0:
                            participants.append((person, val))
                    except ValueError:
                        pass
            
            print(f"    Participants ({len(participants)}):")
            for p, v in participants:
                print(f"      {p}: R$ {v:.2f}")
            
            # Per chat, dinner should be split 8 ways (no Tyler, no Diego)
            # and paid by Joseph
            if len(participants) != 8:
                print(f"    ⚠️  Expected 8 participants but found {len(participants)}")

def check_splitwise_balances():
    """Check Splitwise final balances against our calculations."""
    print("\n=== AUDIT 8: Splitwise Final Balance Comparison ===")
    
    # From splitwise.csv line 37 (Total balance row)
    splitwise_balances = {
        'Antonio': 25500.68,
        'Joseph': -11022.95,
        'David': -11054.28,
        'Bruna': -3320.04,
        'Nick': 12138.27,
        'Hayley': -1892.18,
        'Tyler': -2234.41,
        'Alex': -2700.75,
        'Diego': -2954.74,
        'Estella': -2459.60
    }
    
    print("  Splitwise-only final balances (from their export):")
    for person, balance in sorted(splitwise_balances.items(), key=lambda x: x[1], reverse=True):
        status = "is owed" if balance > 0 else "owes"
        print(f"    {person}: R$ {balance:,.2f} ({status} R$ {abs(balance):,.2f})")
    
    total = sum(splitwise_balances.values())
    print(f"\n  Splitwise sum: R$ {total:.2f}")

def main():
    print("=" * 60)
    print("EXPENSE LEDGER AUDIT")
    print("=" * 60)
    
    expenses = load_expenses('complete_expense_list.csv')
    print(f"\nLoaded {len(expenses)} expenses")
    
    audit_row_balance(expenses)
    audit_payer_amounts(expenses)
    audit_split_math(expenses)
    audit_duplicate_amounts(expenses)
    audit_hayley_vs_everyone(expenses)
    check_dinner_expense(expenses)
    check_splitwise_balances()
    audit_net_balances(expenses)
    
    print("\n" + "=" * 60)
    print("AUDIT COMPLETE")
    print("=" * 60)

if __name__ == '__main__':
    main()
