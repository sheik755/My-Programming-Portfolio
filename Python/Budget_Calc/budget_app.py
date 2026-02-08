import jsonpickle
import os

# Enable ANSI on Windows if supported
if os.name == 'nt':
    os.system('color')

class Category:
    """
    Represents a budget category.
    Tracks deposits, withdrawals, transfers, and total spending.
    """

    def __init__(self, name):
        self.name = name
        self.ledger = []
        self.balance = 0
        self.total_exp = 0

    def deposit(self, amount, description=""):
        """Add funds to the category."""
        if amount < 0:  # Prevent negative deposits
            return False
        self.balance += amount
        self.ledger.append({"amount": amount, "description": description})
        return True

    def withdraw(self, amount, description=""):
        """
        Withdraw funds if sufficient balance exists.
        Tracks total spending for chart calculations.
        """
        if amount < 0:  # Prevent negative withdrawals
            return False
        if not self.check_funds(amount):
            return False
        else:
            self.balance -= amount
            self.ledger.append({"amount": -amount, "description": description})
            self.total_exp += amount
            return True

    def get_balance(self):
        """Return current balance."""
        return self.balance

    def transfer(self, amount, other_cat):
        """
        Transfer funds to another category.
        Uses withdraw/deposit to ensure ledger consistency.
        """
        if amount < 0:  # Prevent negative transfers
            return False
        if not self.check_funds(amount):
            return False
        else:
            # Use descriptions that clearly state the transfer
            withdraw_desc = f'Transfer to {other_cat.name}'
            deposit_desc = f'Transfer from {self.name}'

            if self.withdraw(amount, withdraw_desc) and other_cat.deposit(amount, deposit_desc):
                return True
            else:  # Should ideally not happen if checks pass, but good practice
                return False

    def check_funds(self, amount):
        """Check if enough balance exists for a transaction."""
        if amount > self.balance:
            return False
        else:
            return True

    def display_cat(self):
        """
        Return formatted string showing category ledger and total balance.
        Now with color!
        """
        descr = ''

        # Color header: Blue
        descr += f"\033[94m{self.name.center(30, '*')}\033[0m\n"

        for lines in self.ledger:
            # Truncate description to 22 characters for consistent alignment
            desc = lines["description"][:22]
            # Format amount to 2 decimal places, ensuring it fits 8 characters width
            amount_str = f"{lines['amount']:.2f}"

            # Deposit: Green
            if lines["amount"] >= 0:  # Include 0 if it's a deposit, though unlikely
                descr += f'{desc:<22}\033[92m{amount_str:>8}\033[0m\n'
            # Withdrawal: Red
            else:
                descr += f'{desc:<22}\033[91m{amount_str:>8}\033[0m\n'

        # Total balance: Bold + Green
        descr += f"\033[1mTotal: \033[92m{self.balance:.2f}\033[0m"
        return descr

    def __str__(self):
        return str(self.display_cat())


def create_spend_chart(categories):
    """
    Creates an ASCII bar chart showing percentage spent by category.
    Percentages are rounded down to the nearest 10.
    """
    # Filter out categories with no spending for chart calculation
    active_categories = [cat for cat in categories if cat.total_exp > 0]

    if not active_categories:
        return "\033[93mNo spending data yet to create a chart.\033[0m"

    chart = '\033[94mPercentage spent by category\033[0m\n'

    # Calculate total spending across all ACTIVE categories
    grand_tot_exp = sum(cat.total_exp for cat in active_categories)

    # Build percentage bars from 100 down to 0
    for i in range(100, -10, -10):
        line = f'\033[97m{i:>3}| \033[0m'  # Gray percentage label

        for cat in active_categories:
            # Calculate percentage rounded down to nearest 10
            # Handle division by zero if grand_tot_exp is 0 (though filtered above)
            cur_percent = int(cat.total_exp / grand_tot_exp * 10) * 10 if grand_tot_exp > 0 else 0

            if cur_percent >= i:
                # Color by depth: darker as more spending
                if i >= 60:
                    color = '\033[91m'  # Red (high spend)
                elif i >= 30:
                    color = '\033[93m'  # Yellow (medium spend)
                else:
                    color = '\033[92m'  # Green (low spend)
                line += f'{color} o \033[0m'
            else:
                line += '   '
        chart += line + '\n'

    # Horizontal axis
    chart += '    ' + '---' * len(active_categories) + '-\n'

    # Vertical category names
    list_cat = [cat.name for cat in active_categories]
    max_length = max(len(s) for s in list_cat) if list_cat else 0
    num_cat = len(list_cat)

    for i in range(0, max_length):
        line = '     '
        for j in range(0, num_cat):
            try:
                char = list_cat[j][i]
                line += f'\033[97m {char} \033[0m'
            except IndexError:
                line += '   '
        chart += line
        if i != max_length - 1:
            chart += '\n'

    return chart


# --- End of Category class and create_spend_chart function ---


def get_category_by_name(categories, name):
    """Helper to find a category by name, case-insensitive."""
    return next((c for c in categories if c.name.lower() == name.lower()), None)


def get_float_input(prompt):
    """Helper to get valid float input from user."""
    while True:
        try:
            value = float(input(prompt).strip())
            if value < 0:
                print("\033[91m❌ Amount cannot be negative. Please try again.\033[0m")
            else:
                return value
        except ValueError:
            print("\033[91m❌ Invalid input. Please enter a number.\033[0m")


def save_data(categories, filename="budget_data.json"):
    """Save all categories to a JSON file."""
    try:
        # Serialize the list of Category objects
        serialized = jsonpickle.encode(categories)
        with open(filename, "w") as f:
            f.write(serialized)
        print(f"\033[92m✅ Data saved successfully to '{filename}'.\033[0m")
        return True
    except Exception as e:
        print(f"\033[91m❌ Failed to save data: {e}\033[0m")
        return False


def load_data(filename="budget_data.json"):
    """Load categories from a JSON file. Returns list of Category objects."""
    if not os.path.exists(filename):
        print(f"\033[93mℹ️ No saved data found at '{filename}'. Starting fresh.\033[0m")
        return []

    try:
        with open(filename, "r") as f:
            content = f.read()
        if not content.strip():
            print(f"\033[93mℹ️ File '{filename}' is empty. Starting fresh.\033[0m")
            return []

        # Deserialize the data back into Category objects
        categories = jsonpickle.decode(content)
        print(f"\033[92m✅ Loaded {len(categories)} category(ies) from '{filename}'.\033[0m")
        return categories
    except Exception as e:
        print(f"\033[91m❌ Failed to load data: {e}\033[0m")
        return []


def main():
    categories = []  # Start with an empty list
    # Check if there's saved data
    print(r"""
   📊     BUDGET TRACKER CLI
  ┌──────────────────────────┐
  │   Manage your money      │
  │   wisely & visually      │
  └──────────────────────────┘
""")
    # Try to load existing data on startup
    loaded_categories = load_data()
    if loaded_categories:
        categories = loaded_categories
        print("\033[92m🔄 Previous session data loaded.\033[0m")
    else:
        print("\033[93m🆕 No previous data found. Let's create your first categories.\033[0m")
    while True:
        print("\n")
        print("┌─────────────────────────────┐")
        print("│       MAIN MENU             │")
        print("├─────────────────────────────┤")
        print("│ 1. Add Category             │")
        print("│ 2. View All Categories      │")
        print("│ 3. Deposit Money            │")
        print("│ 4. Withdraw Money           │")
        print("│ 5. Transfer Funds           │")
        print("│ 6. Show Spend Chart         │")
        print("│ 7. Save Data                │")
        print("│ 8. Load Data                │")
        print("│ 9. Exit                     │")
        print("└─────────────────────────────┘\n")
        choice = input("👉 Enter your choice (1–9): ").strip()
        if choice == '1':  # Add Category
            cat_name = input("Enter new category name: ").strip()
            if not cat_name:
                print("\033[91m❌ Category name cannot be empty.\033[0m")
            elif get_category_by_name(categories, cat_name):
                print(f"\033[91m❌ Category '{cat_name}' already exists.\033[0m")
            else:
                categories.append(Category(cat_name))
                print(f"\033[92m✅ Category '{cat_name}' added.\033[0m")
        elif choice == '2':  # View All Categories
            if not categories:
                print("\033[93mℹ️ You haven't added any categories yet.\033[0m")
            else:
                for cat in categories:
                    print(cat)
        elif choice == '3':  # Deposit Money
            if not categories:
                print("\033[93mℹ️ Please add categories first.\033[0m")
                continue
            name = input("Enter category name to deposit into: ").strip()
            cat = get_category_by_name(categories, name)
            if cat:
                amount = get_float_input("Enter deposit amount: $")
                desc = input("Description (optional): ").strip() or "Deposit"
                if cat.deposit(amount, desc):
                    print(f"\033[92m✅ Deposited ${amount:.2f} into {cat.name}.\033[0m")
                else:
                    print("\033[91m❌ Deposit failed.\033[0m")
            else:
                print(f"\033[91m❌ Category '{name}' not found.\033[0m")
        elif choice == '4':  # Withdraw Money
            if not categories:
                print("\033[93mℹ️ Please add categories first.\033[0m")
                continue
            name = input("Enter category name to withdraw from: ").strip()
            cat = get_category_by_name(categories, name)
            if cat:
                amount = get_float_input("Enter withdrawal amount: $")
                desc = input("Description (optional): ").strip() or "Withdrawal"
                if cat.withdraw(amount, desc):
                    print(f"\033[92m✅ Withdrew ${amount:.2f} from {cat.name}.\033[0m")
                else:
                    print(f"\033[91m❌ Insufficient funds in {cat.name}. Available: ${cat.balance:.2f}\033[0m")
            else:
                print(f"\033[91m❌ Category '{name}' not found.\033[0m")
        elif choice == '5':  # Transfer Funds
            if not categories:
                print("\033[93mℹ️ Please add categories first.\033[0m")
                continue
            from_cat_name = input("From which category? ").strip()
            to_cat_name = input("To which category? ").strip()

            from_cat = get_category_by_name(categories, from_cat_name)
            to_cat = get_category_by_name(categories, to_cat_name)
            if from_cat and to_cat:
                if from_cat == to_cat:
                    print("\033[91m❌ Cannot transfer to the same category.\033[0m")
                    continue
                amount = get_float_input("Amount to transfer: $")
                if from_cat.transfer(amount, to_cat):
                    print(f"\033[92m✅ Transferred ${amount:.2f} from {from_cat.name} to {to_cat.name}.\033[0m")
                else:
                    print(
                        f"\033[91m❌ Transfer failed: insufficient balance in {from_cat.name}. Available: ${from_cat.balance:.2f}\033[0m")
            else:
                if not from_cat:
                    print(f"\033[91m❌ Source category '{from_cat_name}' not found.\033[0m")
                if not to_cat:
                    print(f"\033[91m❌ Destination category '{to_cat_name}' not found.\033[0m")
        elif choice == '6':  # Show Spend Chart
            if not categories:
                print("\033[93mℹ️ You need categories and spending to show a chart.\033[0m")
            else:
                print(create_spend_chart(categories))
        elif choice == '7':  # Save Data
            filename = input("Enter filename (default: budget_data.json): ").strip()
            if not filename:
                filename = "budget_data.json"
            save_data(categories, filename)
        elif choice == '8':  # Load Data
            filename = input("Enter filename to load (default: budget_data.json): ").strip()
            if not filename:
                filename = "budget_data.json"
            loaded_cats = load_data(filename)
            if loaded_cats:
                categories = loaded_cats
                print(f"\033[92m✅ Successfully loaded {len(loaded_cats)} category(ies).\033[0m")
            else:
                print("\033[93mℹ️ No data was loaded.\033[0m")
        elif choice == '9':  # Exit
            # Auto-save before exit
            auto_save = input("Auto-save before exiting? (y/N): ").strip().lower()
            if auto_save in ['y', 'yes']:
                save_data(categories)
            print("\n👋 Thanks for using the Budget Tracker! See you next time.")
            break
        else:
            print("\033[91m❌ Invalid choice. Please enter a number from 1 to 9.\033[0m")


# --- Ensure this is at the end of your script ---
if __name__ == "__main__":
    main()

