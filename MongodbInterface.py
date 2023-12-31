from pymongo import MongoClient

def calculate_balance(income, expenses):
    total_income = sum(item["amount"] for item in income)
    total_expenses = sum(item["amount"] for item in expenses)
    balance = total_income - total_expenses
    return balance

def update_balance(account, amount):
    # Assume each account has a document in the collection
    account_doc = collection.find_one({"account_name": account})
    if account_doc:
        current_balance = account_doc.get("balance", 0)
        new_balance = current_balance + amount
        collection.update_one({"account_name": account}, {"$set": {"balance": new_balance}})
    else:
        # Create a new account document if not exists
        collection.insert_one({"account_name": account, "balance": amount})

def update_expense_category(date, amount, category):
    # Update the category for expenses on the specified date
    collection.update_many({"date": date, "amount": amount, "category": None}, {"$set": {"category": category}})

def update_income_category(date, amount, category):
    # Update the category for income on the specified date
    collection.update_many({"date": date, "amount": amount, "category": None}, {"$set": {"category": category}})

def handle_get_purchases(entities):
    purchases = collection.find({"date": {"$gte": entities.get("start_date"), "$lte": entities.get("end_date")}})
    return purchases

def handle_add_purchase(entities):
    data = {"amount": entities["amount"], "date": entities["date"], "category": entities["category"]}
    collection.insert_one(data)
    return "Purchase added successfully."

def handle_get_credits(entities):
    credits = collection.find({"year": entities.get("year"), "source": entities.get("source")})
    return credits

def handle_add_credit(entities):
    data = {"amount": entities["amount"], "sender": entities["sender"], "date": entities["date"]}
    collection.insert_one(data)
    return "Credit added successfully."

def handle_get_balance(entities):
    income = collection.find({"source": entities.get("source"), "year": entities.get("year")})
    expenses = collection.find({"category": entities.get("category"), "date": entities.get("date")})
    balance = calculate_balance(income, expenses)
    
    # Update or create a document for the user's intent
    user_intent_doc = collection.find_one({"user_id": entities.get("user_id"), "intent": "GetBalance"})
    if user_intent_doc:
        collection.update_one({"user_id": entities.get("user_id"), "intent": "GetBalance"}, {"$set": {"balance": balance}})
    else:
        collection.insert_one({"user_id": entities.get("user_id"), "intent": "GetBalance", "balance": balance})
    
    return f"Your current balance is {balance}."

def handle_transfer_funds(entities):
    amount = entities["amount"]
    source_account = entities["source_account"]
    destination_account = entities["destination_account"]
    
    update_balance(source_account, -amount)
    update_balance(destination_account, amount)
    
    return f"Transfer of {amount} from {source_account} to {destination_account} completed."

def handle_categorize_expense(entities):
    amount = entities["amount"]
    date = entities["date"]
    
    update_expense_category(date, amount, entities["category"])
    
    return f"Expense of {amount} on {date} categorized as {entities['category']}."

def handle_categorize_income(entities):
    amount = entities["amount"]
    date = entities["date"]
    
    update_income_category(date, amount, entities["category"])
    
    return f"Income of {amount} on {date} categorized as {entities['category']}."

def handle_get_uncategorized_transactions(entities):
    uncategorized_transactions = collection.find({"category": None})
    return uncategorized_transactions

def handle_intent(intent, entities):
    if intent == "GetPurchases":
        return handle_get_purchases(entities)
    elif intent == "AddPurchase":
        return handle_add_purchase(entities)
    elif intent == "GetCredits":
        return handle_get_credits(entities)
    elif intent == "AddCredit":
        return handle_add_credit(entities)
    elif intent == "GetBalance":
        return handle_get_balance(entities)
    elif intent == "TransferFunds":
        return handle_transfer_funds(entities)
    elif intent == "CategorizeExpense":
        return handle_categorize_expense(entities)
    elif intent == "CategorizeIncome":
        return handle_categorize_income(entities)
    elif intent == "GetUncategorizedTransactions":
        return handle_get_uncategorized_transactions(entities)
    # Add more cases for other intents...

if __name__ == "__main__":
    client = MongoClient('mongodb://localhost:27017/')
    print("Connected successfully!!!")
    db = client['magicstep']
    collection = db['magicstep']
    # Example usage
    # user_input = "Display transactions from January to March."
    # intent = "GetPurchases"
    # entities = {"start_date": "January", "end_date": "March"}

    # result = handle_intent(intent, entities)
    # for item in result:
    #     print(item)
    # user_input = "I made a purchase of 150 USD on 10th January for Electronics. Add it as an expense."
    # intent = "AddPurchase"
    # entities = {"amount": "150 USD", "date": "10th January", "category": "Electronics"}

    # result = handle_intent(intent, entities)
    # print(result)
    user_input = "Give me the sum of all my purchases."
    intent = "GetPurchases"
    entities = {"operation": "sum"}

    result = handle_intent(intent, entities)
    # Convert the cursor to a list
    result_list = list(result)
    print(result_list)
    # Print or process the list of results
    for item in result_list:
        print(item)

