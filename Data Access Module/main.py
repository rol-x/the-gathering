from __init__ import *
from func import *
import sys
from datamining import *
from decimal import Decimal

connection = None

def mainscreen(old):

    old.close()
    win = QMainWindow()
    sizentitle(win)
    label1 = label(win, "Please choose from the methods bellow:", ['Arial', 16], 80, 150, 1)

    button1 = button(win, "Cheapest Buy", first_function, 45, 300, 100, 30)
    button2 = button(win, "Mass Buy", second_function, 195, 300, 100, 30)
    button3 = button(win, "Set Buy", third_function, 345, 300, 100, 30)
    button4 = button(win, "Lowest Average", fourth_function, 495, 300, 100, 30)
    exitbutton = button(win, "Exit", exitapp, 270, 400, 100, 30)

    win.show()

def first_function(old):
    old.close()
    win = QMainWindow()
    sizentitle(win)
    label1 = label(win, "Cheapest Card - Finds the best offer", ['Arial', 16], 80, 150, 1)

    #label and dropdown box for card language
    languagelabel = label(win, "Card Language:", None, 150, 220, 1)

    query = f"""select distinct(language) from sale_offers"""
    language_choice = combobox(win, connection, query, 150, 260)

    # label and dropdown box for card foil state
    foillabel = label(win, "Foil State:", None, 270, 220, 1)

    query = f"""select distinct(is_foiled) from sale_offers"""
    foil_choice = combobox(win, connection, query, 270, 260)

    # label and dropdown box for card condition
    conditionlabel = label(win, "Card Condition:", None, 390, 220, 1)

    query = f"""select distinct(card_condition) from sale_offers"""
    condition_choice = combobox(win, connection, query, 390, 260)

    # label and dropdown box for card condition
    cardlabel = label(win, "Card Name:", None, 220, 320, 1)

    query = f"""select card_name from cards"""
    cards_choice = combobox(win, connection, query, 220, 350)
    cards_choice.resize(cards_choice.sizeHint())

    checkbutton = button(win, "Check", None, 270, 400, 100, 30)
    checkbutton.clicked.connect(lambda: first_function_result(win, cards_choice.currentText(),language_choice.currentText(), \
        foil_choice.currentText(),condition_choice.currentText()) if cards_choice.currentText() != "" else None)

    backbutton = button(win, "Back", mainscreen, 270, 440, 100, 30)

    win.show()

def first_function_result(old, card_name, language, is_foiled, condition):
    old.close()
    win = QMainWindow()
    sizentitle(win)
    label1 = label(win, "First Function Results \n     With given criteria:", ['Arial', 14], 200, 50, 1)

    # ///////////////////////////////////////////////////////////////////////////////////////

    query = f"""select card_id from cards where card_name = "{card_name}" """
    results = read_query(connection, query)
    for i in results:
        card_id = i[0]

    solution = execute_task_1(connection, condition, is_foiled, language, card_id)

    text = f"The best price for {card_name} is from \nseller {solution[0]} for {str(solution[1])}."
    resultlabel = label(win, text, ['Arial', 14], 140, 200, 1)

    # ///////////////////////////////////////////////////////////////////////////////////////

    backbutton = button(win, "Back", mainscreen, 270, 400, 100, 30)

    win.show()

def second_function(old):
    old.close()
    win = QMainWindow()
    sizentitle(win)

    #lael with description
    labe1l = label(win, "For Bulk Buyers - Find seller that can sell you \nmost amount of cards within given cost limitation",\
        ['Arial', 14], 80, 150, 1)

    #label and dropdown box for card language
    languagelabel = label(win, "Card Language:", None, 90, 260, 1)

    query = f"""select distinct(language) from sale_offers"""
    language_choice = combobox(win, connection, query, 90, 300)

    #label and dropdown box for card foil state
    foillabel = label(win, "Foil State:", None, 210, 260, 1)

    query = f"""select distinct(is_foiled) from sale_offers"""
    foil_choice = combobox(win, connection, query, 210, 300)

    #label and dropdown box for card condition
    conditionlabel = label(win, "Card Condition:", None, 330, 260, 1)

    query = f"""select distinct(card_condition) from sale_offers"""
    condition_choice = combobox(win, connection, query, 330, 300)

    #label and input field for budget
    budgetlabel = label(win, "Budget:", None, 450, 260, 1)

    budgetfield = QLineEdit(win)
    budgetfield.move(450,300)
    budgetfield.setValidator(QDoubleValidator(bottom = 1, decimals = 2, notation=QDoubleValidator.StandardNotation))

    #go on with querry
    backbutton = button(win, "Check", None, 270, 360, 100, 30)
    backbutton.clicked.connect(lambda: second_function_result(win,budgetfield.text(),language_choice.currentText(),\
        foil_choice.currentText(), condition_choice.currentText()) if budgetfield.text() != "" else None)

    #go back button
    backbutton = button(win, "Back", mainscreen, 270, 410, 100, 30)

    win.show()

def second_function_result(old, budget ,language, is_foiled, condition):
    old.close()
    win = QMainWindow()
    sizentitle(win)
    label1 = label(win, "Second Function Results \n     With given criteria:", ['Arial', 14], 200, 50, 1)

    if budget.find(',') > -1:
        budget = budget.replace(',','.')
    result = execute_task_2(connection, condition, is_foiled, language, Decimal(budget))
    query = f"""select seller_name from sellers where seller_ID = {result[0]}"""
    sellers = read_query(connection, query)
    for i in sellers:
       seller = i[0]
    text = "It is possible to buy " + str(result[1]) + " cards\nfrom " + seller + " for total " + str(result[2]) + " euros."
    resultlabel = label(win, text, ['Arial', 14], 140, 200, 1)

    backbutton = button(win, "Back", mainscreen, 270, 400, 100, 30)

    win.show()

def third_function(old):
    old.close()
    win = QMainWindow()
    sizentitle(win)
    label1 = label(win, "Cheapest Set - Finds the best offer", ['Arial', 14], 80, 50, 1)

    #label and dropdown box for card language
    languagelabel = label(win, "Card Language:", None, 150, 120, 1)

    query = f"""select distinct(language) from sale_offers"""
    language_choice = combobox(win, connection, query, 150, 160)

    # label and dropdown box for card foil state
    foillabel = label(win, "Foil State:", None, 270, 120, 1)

    query = f"""select distinct(is_foiled) from sale_offers"""
    foil_choice = combobox(win, connection, query, 270, 160)

    # label and dropdown box for card condition
    conditionlabel = label(win, "Card Condition:", None , 390, 120, 1)

    query = f"""select distinct(card_condition) from sale_offers"""
    condition_choice = combobox(win, connection, query, 390, 160)

    # label and dropdown box for card condition
    cardlabel = label(win, "Card Names:", None, 130, 220, 1)

    query = f"""select card_name from cards"""
    result = read_query(connection, query)
    cards = []
    for i in result:
        cards.append(i[0])
    cards_choice = QListWidget(win)
    cards_choice.setSelectionMode(QAbstractItemView.ExtendedSelection)
    for i in cards:
        cards_choice.addItem(i)
    cards_choice.move(130, 250)
    cards_choice.resize(400,130)

    checkbutton = button(win, "Check", None, 270, 400, 100, 30)
    checkbutton.clicked.connect(lambda: third_function_result(win, cards_choice.selectedItems(), language_choice.currentText(), \
        foil_choice.currentText(), condition_choice.currentText()) if len(cards_choice.selectedItems()) != 0 else None)

    backbutton = button(win, "Back", mainscreen, 270, 440, 100, 30)

    win.show()

def third_function_result(old, cards, language, is_foil, condition):
    old.close()
    win = QMainWindow()
    sizentitle(win)
    label1 = label(win, "Results of query with given criteria", ['Arial', 16], 80, 50, 1)
    cardlist = []
    for i in cards:
        cardlist.append(i.text())

    #result = execute_task_3(connection, condition,is_foil, language, cardlist)

    #print(result)

    backbutton = button(win, "Back", mainscreen, 270, 440, 100, 30)

    win.show()

def fourth_function(old):

    old.close()
    win = QMainWindow()
    sizentitle(win)
    name = execute_task_4(connection)
    text =  "Analyze all the sellers offers, based on their average \nprices, and \
        determine, which seller is the best one \nwhen browsing for cheap cards\
        \n\n Today it is best to buy bulk from " + str(name)
    label1 = label(win, text, ['Arial', 14], 70, 150, 1)

    backbutton = button(win, "Back", mainscreen, 270, 400, 100, 30)

    win.show()

if __name__ == "__main__":

    connection = create_db_connection("localhost", "root", "P@ssword", "gathering")
    data_app = QApplication(sys.argv)
    old = QMainWindow()
    mainscreen(old)
    sys.exit(data_app.exec_())
