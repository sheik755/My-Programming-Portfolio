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
        self.balance += amount
        self.ledger.append({"amount": amount, "description": description})

    def withdraw(self, amount, description=""):
        """
        Withdraw funds if sufficient balance exists.
        Tracks total spending for chart calculations.
        """
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
        if not self.check_funds(amount):
            return False
        else:
            self.withdraw(amount, f'Transfer to {other_cat.name}')
            other_cat.deposit(amount, f'Transfer from {self.name}')
            return True

    def check_funds(self, amount):
        """Check if enough balance exists for a transaction."""
        if amount > self.balance:
            return False
        else:
            return True

    def display_cat(self):
        """
        Return formatted string showing category ledger and total balance.
        """
        descr = ''
        tot_amount = 0
        descr += f"{self.name.center(30, '*')}\n"
        for lines in self.ledger:
            descr += f'{lines["description"][:22]:<22}' + f'{str("%.2f" % lines["amount"])[:8]:>8}' + '\n'
        descr += "Total: " + str("%.2f" % self.balance)
        return descr

    def __str__(self):
        return str(self.display_cat())


def create_spend_chart(categories):
    """
    Creates an ASCII bar chart showing percentage spent by category.
    Percentages are rounded down to the nearest 10.
    """
    chart = 'Percentage spent by category\n'
    # Calculate total spending across all categories
    grand_tot_exp = sum(cat.total_exp for cat in categories)
    
    descr = ''
    list_cat = []
    # Build percentage bars from 100 down to 0
    for i in range(100, -10, -10):
        descr = f'{str(i):>3}|'
        for cat in categories:
            cur_percent = int(cat.total_exp / grand_tot_exp * 10) * 10
            if cur_percent >= i:
                descr += ' o '
            else:
                descr += '   '
        chart += descr + ' \n'
     
    # Add horizontal axis
    chart += '    ' + '---' * len(categories) + '-\n'

    # Prepare category names vertically
    list_cat = [cat.name for cat in categories]
    max_length = max(len(s) for s in list_cat)
    num_cat = len(list_cat)
    for i in range(0, max_length):
        descr = '   '
        for j in range(0, num_cat):
            try:
                descr += '  ' + list_cat[j][i]
            except IndexError:
                descr += '   '
        chart += descr + '  '
        if i != max_length - 1:
            chart += '\n'
    return chart

food = Category("Food")
clothing = Category("Clothing")
home = Category("Home")
auto = Category("Auto")

food.deposit(1000, "deposit")
food.withdraw(300, "groceries")
food.withdraw(250, "restaurant and more food for dessert")
food.transfer(50, clothing)
print(food)

clothing.deposit(200, "deposit")
clothing.withdraw(100, "Winter wear")
print(clothing)

home.deposit(1500, "deposit")
home.withdraw(1000, "Mortgage")
print(home)

auto.deposit(700, "deposit")
auto.withdraw(400, "Insurance")
print(auto)

categories = [food, clothing, home, auto]
print(create_spend_chart(categories))