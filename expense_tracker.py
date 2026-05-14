import os
import json
import datetime
import calendar
import matplotlib.pyplot as plt
import numpy as np

class Expense:
    total_spending = 0

    def __init__(self, amount, category, description, date):
        self.amount = amount
        self.category = category
        self.description = description
        self.date = date  
        Expense.total_spending += self.amount

    def __contains__(self, keyword):
        return keyword in self.date or keyword in self.description
    
    def to_dict(self):
        return {
            "amount": self.amount,
            "category": self.category,
            "description": self.description,
            "date": self.date
        }

DEFAULT_CATEGORIES = {"Food": 0,
                      "Transport": 0,
                      "Bills": 0,
                      "Discretionary": 0,
                      "Others": 0
                    }
    
def load_expensesfile():
    file_path = os.path.join(os.path.dirname(__file__), "expenses_record.json")

    if not os.path.exists(file_path):
        return []
    
    with open(file_path, "r") as file:
        try:
            temp = json.load(file) #temp is now a list of dictionaries
            expenses = [] #this list would store objects and will be returned later on
            for dict_ in temp:
                expense = Expense(dict_["amount"], dict_["category"], dict_["description"], dict_["date"])
                expenses.append(expense)
            return expenses
        except json.JSONDecodeError:
            return []

def load_dailyExpenditures():
    file_path = os.path.join(os.path.dirname(__file__), "dailyExpendituresRecord.json")
    if not os.path.exists(file_path):
        return {}
    
    with open(file_path, "r") as file:
        try:
            return json.load(file)
        except json.JSONDecodeError:
            return {}

def load_spending_per_category():
    file_path = os.path.join(os.path.dirname(__file__), "ExpendituresPerCategoryRecord.json")
    if not os.path.exists(file_path):
        return DEFAULT_CATEGORIES.copy()
    
    with open(file_path, "r") as file:
        try:
            return json.load(file)
        except json.JSONDecodeError:
            return DEFAULT_CATEGORIES.copy()

def load_monthlyRecords():
    file_path = os.path.join(os.path.dirname(__file__), "monthlyRecords.json")
    if not os.path.exists(file_path):
        return []
    
    with open(file_path, "r") as file:
        try:
            return json.load(file)
        except json.JSONDecodeError:
            return []

def update(expenses, spending_eachday, spending_percategory, monthly_stats):
    file_path = os.path.join(os.path.dirname(__file__), "expenses_record.json")
    temp = []
    for expense in expenses:
        data = expense.to_dict()
        temp.append(data)
    
    with open(file_path, "w") as expenses_file:
        json.dump(temp, expenses_file, indent=4)
    
    file_path1 = os.path.join(os.path.dirname(__file__), "dailyExpendituresRecord.json")
    with open(file_path1, "w") as daily_record_file:
        json.dump(spending_eachday, daily_record_file, indent=4)
    
    file_path2 = os.path.join(os.path.dirname(__file__), "ExpendituresPerCategoryRecord.json")
    with open(file_path2, "w") as category_spending_file:
        json.dump(spending_percategory, category_spending_file, indent=4)
    
    file_path3 = os.path.join(os.path.dirname(__file__), "monthlyRecords.json")
    with open(file_path3, "w") as monthlyRecords_file:
        json.dump(monthly_stats, monthlyRecords_file, indent=4)

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

def add(expenses, spending_eachday, spending_percategory, monthly_stats):
    clear_screen()
    try:
        amount = float(input("Enter amount: "))
    except ValueError:
        print("Invalid Input!")
        input("Press Enter to Continue")
        return
    
    if amount <= 0:
        print("Invalid Input!")
        input("Press Enter to Continue")
        return
    
    print("1. Food")
    print("2. Transport")
    print("3. Bills")
    print("4. Leisure/Entertainment/wants")
    print("5. Others")

    category = input("Please select category: ")
    if not category.isdigit():
        print("Invalid Input!")
        input("Press Enter to continue...")
        return
    
    match category:
        case "1":
            category = "Food"
        case "2":
            category = "Transport"
        case "3":
            category = "Bills"
        case "4":
            category = "Discretionary"
        case "5":
            category = "Others"
        case _:
            print("Invalid Input")
            input("Press Enter to continue...")
            return
    
    date = datetime.date.today().isoformat()
    
    if date in spending_eachday:
        spending_eachday[date] += amount
    else:
        spending_eachday[date] = amount
    
    spending_percategory[category] += amount

    current_month = datetime.datetime.now().strftime("%m")
    current_month = int(current_month)
    alr_exists = False
    for month in monthly_stats: #month is a dictionary
        if current_month == month["month"]:
            month["total_exp"] += amount
            month[category] += amount
            alr_exists = True
            break
    if not alr_exists:
        this_month = {"month": current_month,
                      "total_exp": 0,
                      "Food": 0,
                      "Transport": 0,
                      "Bills": 0,
                      "Discretionary": 0,
                      "Others": 0}
        this_month["total_exp"] += amount
        this_month[category] += amount
        monthly_stats.append(this_month)

    Description = input("Enter description: ")
    for expense in expenses: #expense is an object/instance
        while expense.description == Description:
            print("Your description must be unique among all your purchases")
            Description = input("Enter description: ")
            if expense.description != Description:
                break
    
    expense = Expense(amount, category, Description, date)
    expenses.append(expense)
    update(expenses, spending_eachday, spending_percategory, monthly_stats)
    print("Expense Added Successfuly!")
    input("Press Enter to continue...")

def remove(expenses, spending_eachday, spending_percategory, monthly_stats):
    clear_screen()
    if len(expenses) == 0:
        print("You currently have no expenses added yet")
        input("Press Enter to continue...")
        return

    description = input("Please enter the description of the expense to remove: ")

    for expense in expenses:
        if expense.description == description:
            spending_percategory[expense.category] -= expense.amount
            spending_eachday[expense.date] -= expense.amount
            if spending_eachday[expense.date] == 0:
                del spending_eachday[expense.date]
            for m in monthly_stats: #m is a dict
                if expense.date.month == m["month"]:
                    m["total_exp"] -= expense.amount
                    m[expense.category] -= expense.amount
            Expense.total_spending -= expense.amount    
            expenses.remove(expense)
            update(expenses, spending_eachday, spending_percategory, monthly_stats)
            print("Expense successfully deleted from your list!")
            return
        
    print("No expense found with such description")
    input("Press Enter to continue...")

def view_history(expenses):
    clear_screen()
    if len(expenses) == 0:
        print("You currently have no expenses added yet")
        input("Press Enter to continue...")
        return
    
    print("Purchase History: ")
    print()
    for expense in expenses:
        print(f"Purchase Description: {expense.description}")
        print(f"Category: {expense.category}")
        print(f"Date: {expense.date}")
        print(f"Amount: ${expense.amount:.2f}")
        print()

    input("Press Enter to continue...")

def analytics(expenses, spending_eachday, spending_percategory):
    clear_screen()
    print(f"Total Spending: ${Expense.total_spending:.2f}")
    average_spending = Expense.total_spending / len(spending_eachday) #on a daily basis
    print(f"Average Spending (On a Daily Basis): ${average_spending:.2f}")

    highest_spendingday = " "
    max = 0
    for day, spending in spending_eachday.items():
        if spending > max:
            max = spending
            highest_spendingday = day

    print(f"Your highest spending day was on {highest_spendingday} totaling to ${max:.2f}")
    print()
    print("Total Spending by Category: ")
    sorted_totals = sorted(spending_percategory.items(), #list of tuples
                           key=lambda x: x[1],
                           reverse=True)

    for pair in sorted_totals:
        print(f"{pair[0]}: ${pair[1]:.2f}")
    
    input("Press Enter to continue...")

def search_purchases(expenses): #search by date or search the product
    clear_screen()
    keyword = input("Enter the date or the description: ")
    print("Search Results: ")
    print()
    for expense in expenses:
        if keyword in expense:
            print(f"Purchase Description: {expense.description}")
            print(f"Category: {expense.category}")
            print(f"Date: {expense.date}")
            print(f"Amount: {expense.amount:.2f}")
            print()

    input("Press Enter to continue...")

def monthly_summary(monthly_stats):
    clear_screen()
    month = input("Enter month number: ")
    if not month.isdigit():
        print("Invalid Input")
        input("Press any key to continue...")
        return
    
    month = int(month)
    if month < 1 or month > 12:
        print("Invalid Input")
        input("Press any key to continue...")
        return
    
    categories = ["Food", "Transport", "Bills", "Discretionary", "Others"]
    month_name = calendar.month_name[month]
    for monthly_rec in monthly_stats:
        if month == monthly_rec["month"]:
            print(f"Total Spending: ${monthly_rec['total_exp']:.2f}")
            print()
            x = np.array(categories)
            y = np.array([monthly_rec.get(cat, 0) for cat in categories])
            plt.bar(x,y)
            plt.title(f"{month_name} Spending Summary")
            plt.xlabel("Category")
            plt.ylabel("Amount")
            plt.show()
            input("Press any key to continue...")
            return

    print(f"No records found for the month of {month_name}")
    input("Press any key to continue...")

def main():
    expenses = load_expensesfile()
    spending_eachday = load_dailyExpenditures()
    spending_percategory = load_spending_per_category()
    monthly_stats = load_monthlyRecords()

    while True:
        clear_screen()
        print("1. Add Expense")
        print("2. Remove an Expense")
        print("3. View Expenses History")
        print("4. View Analytics")
        print("5. Search by date or description")
        print("6. Monthly Summary")
        print("7. Exit")

        choice = input("Enter the number beside your choice: ")

        if not choice.isdigit():
            print("Invalid Input!")
            continue

        choice = int(choice)

        match choice:
            case 1:
                add(expenses, spending_eachday, spending_percategory, monthly_stats)
            case 2:
                remove(expenses, spending_eachday, spending_percategory, monthly_stats)
            case 3:
                view_history(expenses)
            case 4:
                analytics(expenses, spending_eachday, spending_percategory)
            case 5:
                search_purchases(expenses)
            case 6:
                monthly_summary(monthly_stats)
            case 7:
                break
            case _:
                print("Invalid Input!")
                continue

if __name__ == "__main__":
    main()