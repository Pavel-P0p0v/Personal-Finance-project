# Ben-project
This code will read all the CSV files in a folder called BandStatements within your Jupiter notebook. It will then combine all the files in one data base and allow you to examine them one month at a time. Once you select the month, it will sort your expenses based on the categories.json file and allow you to interact with them. You can move expenses from one category to another, add or remove categories. 

The categories.json file has the names of each category with their respective key words. The key words are used to scan the bank statement and categories the expenses. When you move an expenses to a folder, the program will read the expense name and save it as a key word in that folder, after which it will delete it from any other folders. The categorization algorithm puts priority on exact matches to insure more accurate categorization. For example, the food category has t he key word “restaurant” but if there is an expense with the name “IT restaurant” that you put in the technology folder, the system will recognize this and categorize it accordingly. 
