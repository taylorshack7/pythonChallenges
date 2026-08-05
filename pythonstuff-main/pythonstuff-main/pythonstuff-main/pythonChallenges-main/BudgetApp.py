#
#
#
#
#


class Category():
    def __init__(self, name):
        self.name = name
        self.ledger = []
    def deposit(self, amount, description = ''):
        self.ledger.append({'amount': amount, 'description': description})
    def withdraw(self, amount, description = ''):
        if self.check_funds(amount):
            self.ledger.append({'amount': -amount, 'description': description})
            return True
        else:
            return False
    def get_balance(self):
        ## loop thru list of dicts, add values up, and if sum positive return True. Else return False
        x = 0
        for dictionary in self.ledger:
            x += float(dictionary['amount'])
        return x
    def transfer(self, amount, idk):
        if self.withdraw(amount, f'Transfer to {idk.name}'):
            idk.deposit(amount, f'Transfer from {self.name}')
            return True
        else:
            return False
    def check_funds(self, amount):
        if self.get_balance() - amount >= 0:
            return True
        else:
            return False
    def __str__(self):
        transactions = f"{self.name[:30]:*^30}\n"
        for x in self.ledger:
            description = x['description'][:23]
            amount = x['amount']
            transactions += f'{description:<23}{amount:>7.2f}\n'
        transactions += f"Total: {self.get_balance():.2f}"
        return transactions
def create_spend_chart(categories):
    #Set title line
    title = 'Percentage spent by category\n'

    #calculate how much was spent per category
    spent_per_category = []
    for category in categories:
        spent = 0
        for dictionary in category.ledger:
            if dictionary['amount'] < 0:
                spent += dictionary['amount']
        spent_per_category.append(abs(spent))
    #print(spent_per_category)

    #calculate total spent
    total_spent = sum(spent_per_category)

    #calculate percentage spent
    percentages = []
    for money in spent_per_category:
        percent = ((money / total_spent) * 100) // 10 * 10
        percentages.append(int(percent))
    #print(percentages)

    #Create bar chart
    for counter in range(100, -1, -10):
        title += f"{counter:>3}|"
        for chart in percentages:
            if chart >= counter:
                title += f' o '
            else:
                title += f'   '
        title += ' \n'

    #create horizontal line
    title += '    ' + '-' * (len(categories) * 3 + 1) + '\n'

    #create vertical category names
    count = 0
    category_vertname = []
    for category in categories:
        category_vertname.append(category.name)
        if len(category.name) > count:
            count = len(category.name)


    for row in range(count):
        title += '     '
        for colum in range(len(category_vertname)):
            if row < len(category_vertname[colum]):
                title +=f'{category_vertname[colum][row]}  '
            else:
                title += '   '
        if row != count:
            title += '\n'
    return title


food = Category('Food')
food.deposit(100, 'deposit')
print(food.withdraw(10.15, 'groceries'))
print(food.withdraw(15.89, 'restaurant and more food for dessert'))
clothing = Category('Clothing')
print(food.transfer(50, clothing))
print(food)
print('\n')
print(clothing.withdraw(20, 'pants'))
print(create_spend_chart([food, clothing]))


