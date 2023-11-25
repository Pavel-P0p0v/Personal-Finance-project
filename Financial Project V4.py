#!/usr/bin/env python
# coding: utf-8

# In[1]:


pip install matplotlib


# In[2]:


# Catagory visualization, with price and better placement 
from IPython.display import display, HTML

def display_expense_groups_table(expense_groups):
    # Sort the categories by total amount in descending order
    sorted_categories = sorted(expense_groups.items(), key=lambda x: -sum(amount for _, amount in x[1]))
    
    html_table = "<div style='display: flex; flex-wrap: wrap;'>"
    
    for group_name, group_expenses in sorted_categories:
        total_amount = sum(expense_amount for _, expense_amount in group_expenses)
        
        html_table += "<div style='border: 1px solid black; margin: 10px; padding: 10px; flex: 1 0 auto; width: calc(33% - 20px);'>"
        html_table += f"<p style='font-weight: bold; background-color: #f0f8ff; border-bottom: 1px solid #000;'>{group_name}</p>"
        
        for expense_name, expense_amount in group_expenses:
            html_table += f"<p>{expense_name}: ${expense_amount:.2f}</p>"
        
        html_table += f"<p style='font-weight: bold;'>Total Amount: ${total_amount:.2f}</p>"
        html_table += "</div>"

    html_table += "</div>"
    
    display(HTML(html_table))



# In[3]:


# pie chart
import matplotlib.pyplot as plt 
def display_expense_distribution_pie_chart(grouped_expenses):
    # Create a list of group names and their total amounts
    group_names = list(grouped_expenses.keys())
    total_amounts = [sum(amount for _, amount in items) for items in grouped_expenses.values()]

    # Calculate the total expenses
    total_expenses = sum(total_amounts)

    # Calculate the percentages
    percentages = [(amount / total_expenses) * 100 for amount in total_amounts]

    # Create labels for the pie chart
    labels = [f"{group_name}: {percent:.1f}%" if percent >= 3 else "" for group_name, percent in zip(group_names, percentages)]

    # Create a pie chart with custom labels
    plt.figure(figsize=(8, 8))
    plt.pie(total_amounts, labels=labels, startangle=140, autopct='', pctdistance=0.85)
    plt.axis('equal')  # Equal aspect ratio ensures that the pie chart is circular.

    # Display the pie chart
    #plt.title("Expense Distribution by Group")
    plt.show()


# In[4]:


import matplotlib.pyplot as plt

# Making line graph of the expenses
def extra_data(selected_data):
    # Copy the selected_data DataFrame for processing
    df = selected_data.copy()

    # Group expenses by date and sum them
    expense_by_date = df.groupby('Date')['Expense'].sum().reset_index()

    # Convert the 'Date' column to a datetime object (if it's not already)
    expense_by_date['Date'] = pd.to_datetime(expense_by_date['Date'])

    # Create the line graph
    plt.figure(figsize=(10, 6))
    plt.plot(expense_by_date['Date'], expense_by_date['Expense'], marker='o', linestyle='-')
    plt.xlabel('Date')
    plt.ylabel('Total Expenses')
    plt.title('Total Expenses Over Time')
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.tight_layout()

    # Display the line graph
    plt.show()

    # 5 Largest expenses
    df = df.sort_values(by='Expense', ascending=False)
    df1 = df.drop('Deposit', axis=1)
    print('Top 5 Largest Expenses')
    print(df1.head().to_string(index=False))
    total(selected_data)
    
# Calculate and display the total expenses for the selected data
def total(selected_data):
    total_exp = selected_data['Expense'].sum()
    print('The total Expenses for this month were:', total_exp)



# In[5]:


import os
import csv
from nltk.tokenize import word_tokenize
import json
from collections import defaultdict
from IPython.display import display, HTML
import pandas as pd
from calendar import month_name

# Define the file path for saving and loading categories
categories_file = "categories.json"

# Define a list to store the moved items during the session
moved_items = []

def save_categories(categories):
    with open(categories_file, 'w') as file:
        json.dump(categories, file)

def load_categories():
    try:
        with open(categories_file, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def print_categories(categories):
    print("Categories:")
    for category in categories:
        print(category)

def tokenize_and_match(expense_name, categories):
    expense_tokens = word_tokenize(expense_name.lower())
    
    for category, keywords in categories.items():
        if expense_name.lower() in keywords:
            return category

    for category, keywords in categories.items():
        for keyword in keywords:
            keyword_tokens = word_tokenize(keyword.lower())
            if keyword.lower() in expense_name.lower() or any(word in expense_tokens for word in keyword_tokens):
                return category
    
    return "Uncategorized"

def move_expense(grouped_expenses, new_category, expense_name):
    moved_expenses = []
    expense_found = False
    
    for group_name, group_expenses in grouped_expenses.items():
        for expense in group_expenses:
            if expense[0] == expense_name:
                expense_found = True
                moved_expenses.append(expense)
                group_expenses.remove(expense)
    
    if not expense_found:
        print(f"'{expense_name}' was not found in any category.")
        while True:
            user_input = input("Enter a new name or type 'back' to go back: ")
            if user_input == 'back':
                return []
            elif user_input != expense_name:
                expense_name = user_input
                expense_found = False
                for group_name, group_expenses in grouped_expenses.items():
                    for expense in group_expenses:
                        if expense[0] == expense_name:
                            expense_found = True
                            moved_expenses.append(expense)
                            group_expenses.remove(expense)
                
                if expense_found:
                    break
            else:
                print("Please enter a new name that is different from the original name.")
                
    if new_category not in grouped_expenses:
        grouped_expenses[new_category] = moved_expenses
    else:
        grouped_expenses[new_category].extend(moved_expenses)
    
    for item in moved_expenses:
        moved_items.append((item[0], new_category))
        
    return moved_expenses

def read_and_combine_csv_files(folder_path):
    # Initialize an empty list to store DataFrames for each CSV file
    dfs = []

    # Loop through all CSV files in the folder
    for file in os.listdir(folder_path):
        if file.endswith('.csv'):
            file_path = os.path.join(folder_path, file)

            # actual column names
            column_names = ['Date', 'Description', 'Expense', 'Deposit', 'Total']

            df = pd.read_csv(file_path, header=None, names=column_names)
            dfs.append(df)

    # Combine all DataFrames into a single DataFrame
    combined_df = pd.concat(dfs, ignore_index=True)
    
    return combined_df


def process_bank_statement(selected_data):
    categories = load_categories()
    expense_groups = defaultdict(list)

    for _, row in selected_data.iterrows():
        expense_name = row['Description']
        expense_amount = float(row['Expense']) if not pd.isna(row['Expense']) else 0.0
        deposit_amount = float(row['Deposit']) if not pd.isna(row['Deposit']) else 0.0

        if expense_amount > 0 and deposit_amount == 0:
            matched_category = tokenize_and_match(expense_name, categories)
            if matched_category != "Uncategorized":
                expense_groups[matched_category].append((expense_name, expense_amount))
            else:
                expense_groups["Uncategorized"].append((expense_name, expense_amount))

    return expense_groups

def update_json_file_with_moves(moved_items, categories):
    for moved_item, new_category in moved_items:
        for category, items in categories.items():
            if category != new_category:
                lowercase_moved_item = moved_item.lower()
                if lowercase_moved_item in items:
                    items.remove(lowercase_moved_item)
    
    save_categories(categories)

def convert_keywords_to_lowercase(categories):
    for category, keywords in categories.items():
        categories[category] = [keyword.lower() for keyword in keywords]

def remove_category(categories):
    print_categories(categories)
    category_to_remove = input("Enter the category to remove: ")
    
    if category_to_remove in categories:
        del categories[category_to_remove]
        save_categories(categories)
        print(f"'{category_to_remove}' category has been removed.")
    else:
        print(f"'{category_to_remove}' does not exist in the categories.")
        
        
# Define the categories in the global scope
categories = load_categories()  
# Removes the need for scrolling 
display(HTML("<style>div.output_scroll { height: auto; max-height: none; }</style>"))        
        
        
def main():
    folder_path = "BankStatements"
    csv_files = [file for file in os.listdir(folder_path) if file.endswith(".csv")]
    combined_df = read_and_combine_csv_files(folder_path)
    
    while True:
        print("Options:")
        print("1. Choose a month to process")
        print("2. Exit")
        option = input("Select an option (1/2): ")
        
        if option == "1":
            print("Months:")
            for month in range(1, 13):
                print(f"{month}. {month_name[month]}")
            
            selected_month = input("Enter the month to process (e.g., '1' for January): ")
            
            if not (selected_month.isdigit() and 1 <= int(selected_month) <= 12):
                print("Invalid month. Please enter a valid month number.")
                continue
            
            selected_month = str(selected_month).zfill(2)
            
            # Convert 'Date' column to datetime type
            combined_df['Date'] = pd.to_datetime(combined_df['Date'])
            
            # Filter the data for the selected month (January in this case)
            selected_data = combined_df[combined_df['Date'].dt.month == int(selected_month)]
            '''
            # Display the contents of the selected data
            with pd.option_context('display.max_rows', None, 'display.max_columns', None):
                print(selected_data)
            print("\n" + "=" * 50 + "\n")
            '''
            grouped_expenses = defaultdict(list)

            for csv_file in csv_files:
                selected_csv_file = os.path.join(folder_path, csv_file)
                grouped_expenses.update(process_bank_statement(selected_data))

            if not grouped_expenses:
                print("No expenses found for the selected month.")
            else:
                display_expense_groups_table(grouped_expenses)
                done = False
                
                while not done:
                    print("Options:")
                    print("1. Move expense to a category")
                    print("2. Add a new category")
                    print("3. Remove a category")
                    print("4. Save and Exit")
                    option = input("Select an option (1/2/3/4): ")

                    if option == "1":
                        expenses_to_move = input("Enter the names of the expenses to move (comma-separated): ")
                        expense_names = [name.strip() for name in expenses_to_move.split(',')]

                        invalid_expenses = [name for name in expense_names if name not in [expense[0] for group in grouped_expenses.values() for expense in group]]

                        if invalid_expenses:
                            print(f"The following items do not exist: {', '.join(invalid_expenses)}")
                        else:
                            print_categories(categories)
                            to_category = input("Enter the category to move the expenses to: ")

                            moved_expenses = move_expense(grouped_expenses, to_category, expense_names)
                            if moved_expenses:
                                print(f"Moved the following expenses to '{to_category}': {', '.join([expense[0] for expense in moved_expenses])}")
                                if to_category not in categories:
                                    categories[to_category] = []
                                categories[to_category].extend(expense_names)
                                save_categories(categories)
                            display_expense_groups_table(grouped_expenses)

                    elif option == "2":
                        new_category_name = input("Enter the name of the new category: ")
                        keywords = input("Enter keywords for this category (comma-separated): ").split(',')
                        categories[new_category_name] = [keyword.strip() for keyword in keywords]

                    elif option == "3":
                        remove_category(categories)
                    
                    elif option == "4":
                        display_expense_distribution_pie_chart(grouped_expenses)
                        extra_data(selected_data)
                        convert_keywords_to_lowercase(categories)
                        save_categories(categories)
                        update_json_file_with_moves(moved_items, categories)
                        if moved_items:
                            print("Moved items in this session:")
                            for item in moved_items:
                                print(f"{item[0]} - To: {item[1]}")
                        else:
                            print("No items have been moved in this session yet.")
                        
                        done = True
                      
            continue

        elif option == "2":
            break

if __name__ == "__main__":
    main()


# In[ ]:




