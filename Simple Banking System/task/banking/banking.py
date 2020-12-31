# banking / credit card
import random
import sqlite3


# I will treat the bank card number as a string containing numeric digits
# thus I can extract the needed portions by slicing
# and then turning them into numbers as needed.


# ============= create account ===========
def create_pin():  # returns the pin as a 4 char string
    return str(int(random.random() * 1e4)).zfill(4)


def create_checksum(string):
    accum = 0  # add up the string digits with odd positions doubled
    for i in reversed(range(len(string))):
        val = int(string[i]) * (1 if i % 2 else 2)
        accum += val if val <= 9 else val - 9  # reduce to single digit then add
    return (10 - accum % 10) if accum % 10 > 0 else 0  # this is subtle but rare


def create_account():  # returns an account number as a 16 char string
    bank_id_st = '400000'  # 6 characters, as a string
    act_st = str(int(random.random() * 1e6)).zfill(9)  # some leading 0s for fun
    checksum_st = str(create_checksum(bank_id_st + act_st))
    return bank_id_st + act_st + checksum_st


def enter_acct():  # dbtable
    acct = input('Enter your card number:\n')
    if len(acct) != 16 or not acct.isnumeric():
        print('Invalid card number')
        return False
    lpin = input('Enter your PIN:\n')  # so as not to be confused with a global pin
    print()
    if len(lpin) != 4 or not lpin.isnumeric():
        print('Invalid PIN')
        return False
    cmd = "SELECT pin FROM card WHERE  number = '{}'".format(acct)
    cursor.execute(cmd)
    results = cursor.fetchone()
    if results is None:
        print('Wrong card number or PIN')  # card number not found
        print()
        return False
    if lpin != results[0]:  # first and only item in returned tuple
        print('Wrong card number or PIN')  # pin doesn't match
        print()
        return False
    print('You have successfully logged in!')
    print()
    return acct  # this is the validated card number string which will be as a True


def check_luhn(tmp_str):
    if len(tmp_str) != 16:
        return False
    should_be = create_checksum(tmp_str[0:15])
    if str(should_be) == str(tmp_str[-1]):
        return True
    else:
        return False


# ============= MAIN =========
# database stuff do this once at the beginning of the program
connection = sqlite3.connect('card.s3db')  # creates the database or re opens it?
cursor = connection.cursor()
# cursor.execute('DROP TABLE card')
command1 = '''CREATE TABLE IF NOT EXISTS card 
(id INTEGER, number TEXT, pin TEXT, balance INTEGER DEFAULT 0)'''
# if id is PRIMARY KEY it must be unique
cursor.execute(command1)

while True:
    # ============= User input ============
    print('1. Create an account\n'
          '2. Log into account\n'
          '0. Exit')

    choice = int(input())
    print()
    if choice == 0:
        print('Bye!')
        connection.commit()  # save the database for later use
        break

    if choice == 1:
        try:
            card_num = create_account()
            print('Your card has been created')
            print('Your card number:\n{}'.format(card_num))
            pin = create_pin()
            print('Your card PIN:\n{}'.format(pin))
            print()
            cmd = "INSERT INTO card (number, pin) VALUES('{}', '{}')".format(card_num, pin)
            cursor.execute(cmd)
            # worry about auto-incrementing the id field as Primary Key later
        except sqlite3.OperationalError:
            print('invalid attempt to append to database ----------')
            print('attempting to add {} with pin {} to\n'.format(card_num, pin))
            cursor.execute('SELECT * FROM card')  # show the whole table
            results = cursor.fetchall()
            print(results)

    elif choice == 2:
        c_num = enter_acct()  # card number (True) or False
        if c_num:  # if True I have logged in, and this is the card number
            while True:
                connection.commit()
                print('1. Balance\n'  # now I have more choices
                      '2. Add income\n'
                      '3. Do transfer\n'
                      '4. Close account\n'
                      '5. Log out\n'
                      '0. Exit')
                choice2 = int(input())
                print()

                if choice2 == 1:
                    cmd = "SELECT balance FROM card WHERE number = '{}'".format(c_num)
                    cursor.execute(cmd)
                    results = cursor.fetchone()
                    if results is None:
                        print('something strange happened during data lookup')
                        # break
                    else:
                        print('Balance: {}'.format(results[0]))

                elif choice2 == 2:
                    cmd = "SELECT balance FROM card WHERE number = '{}'".format(c_num)
                    cursor.execute(cmd)
                    results = cursor.fetchone()
                    print("Enter income:")
                    deposit = int(input())
                    deposit += results[0]
                    cmd = "UPDATE card SET balance = '{}' WHERE number = '{}'".format(deposit, c_num)
                    cursor.execute(cmd)
                    print("Income was added!")
                    print()

                elif choice2 == 3:
                    print("Transfer")
                    print("Enter card number:")
                    c_num2 = input()
                    print()

                    if not check_luhn(c_num2):
                        print("Probably you made a mistake in the card number. Please try again!")
                        print()
                        continue

                    cmd = "SELECT pin FROM card WHERE  number = '{}'".format(c_num2)
                    cursor.execute(cmd)
                    results = cursor.fetchone()
                    if results is None:
                        print("Such a card does not exist")
                        print()
                        continue

                    if str(c_num2) == str(c_num):
                        print("You can't transfer money to the same account!")
                        print()
                        continue

                    print("Enter how much money you want to transfer:")
                    transaction = input()
                    cmd = "SELECT balance FROM card WHERE number = '{}'".format(c_num)
                    cursor.execute(cmd)
                    results = cursor.fetchone()

                    if float(transaction) > float(results[0]):
                        print("Not enough money!")
                        print()
                        continue

                    cmd = "UPDATE card SET balance = balance - '{}' WHERE number = '{}'".format(transaction, c_num)
                    cursor.execute(cmd)
                    cmd = "UPDATE card SET balance = balance + '{}' WHERE number = '{}'".format(transaction, c_num2)
                    cursor.execute(cmd)
                    print("Success!")
                    print()

                elif choice2 == 4:
                    cmd = "DELETE FROM card WHERE number = '{}'".format(c_num)
                    cursor.execute(cmd)
                    print("The account has been closed!")
                    print()
                    connection.commit()
                    break

                elif choice2 == 5:
                    print('You have successfully logged out!')
                    connection.commit()
                    break

                elif choice2 == 0:
                    print('Bye!')
                    connection.commit()  # save the database for later use
                    exit()
