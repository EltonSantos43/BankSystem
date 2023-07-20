menu = """
[d] Deposit
[w] Withdraw
[s] Statement
[e] Exit

=> """

balance = 0
limit = 500
statement = ""
number_checks = 0
LIMITS_CHECKS = 3

while True:

    option = input(menu)

    if option == "d":
        value = float(input('Enter the value of the expense: '))

        if value > 0:
            balance += value
            statement += f"Deposit: R$ {value:.2f}\n"

        else:
            print("Operation failed! The value entered is invalid.")

    elif option == "w":
        value = float(input('Enter the value of the withdraw: '))

        exceeded_balance = value > balance

        exceeded_limit = value > limit

        exceeded_checks = number_checks >= LIMITS_CHECKS

        if exceeded_balance:
            print('Operation failed! You do not have enough balance.')

        elif exceeded_limit:
            print('Operation failed! The withdrawal amount exceeds the limit.')

        elif exceeded_checks:
            print('Operation failed! Maximum number of withdraws exceeded.')

        elif value > 0:
            balance -= value
            statement += f'Checks: R$ {value:.2f}\n'
            number_checks += 1

        else:
            print('Operation failed! The value entered is valid.')

    elif option == "s":
        print('\n================ Statement ================')
        print('No transactions have been made.' if not statement else statement)
        print(f'\nBalance: R$ {balance:.2f}')
        print('=============================================')

    elif option == "e":
        break

    else:
        print('Invalid operation! Please select the desired operation.')
