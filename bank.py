from abc import ABC, abstractmethod
from datetime import datetime
import textwrap
from typing import (
    List,
    Optional,
    Generator,
)


class AccountsIterator:
    def __init__(self, accounts: List['Account']):
        self.accounts = accounts
        self._index = 0

    def __iter__(self) -> 'AccountsIterator':
        return self

    def __next__(self) -> str:
        if self._index < len(self.accounts):
            account = self.accounts[self._index]
            self._index += 1
            return f"""\
                Agency:\t{account.agency}
                Number:\t\t{account.number}
                Holder:\t{account.client.name}
                Balance:\t\t${account.balance:.2f}
            """
        else:
            raise StopIteration


def make_transaction(account: 'Account', transaction: 'Transaction'):
    transaction.register(account)


class Client:
    def __init__(self, address: str):
        self.address = address
        self.accounts: List[Account] = []

    def add_account(self, account: 'Account'):
        self.accounts.append(account)


class Individual(Client):
    def __init__(self, name: str, birth_date: str, cpf: str, address: str):
        super().__init__(address)
        self.name = name
        self.birth_date = birth_date
        self.cpf = cpf


class Account:
    def __init__(self, number: int, client: Client):
        self._balance = 0
        self._number = number
        self._agency = "0001"
        self._client = client
        self._history = History(client)

    @classmethod
    def new_account(cls, client: Client, number: int) -> 'Account':
        return cls(number, client)

    @property
    def balance(self) -> float:
        return self._balance

    @property
    def number(self) -> int:
        return self._number

    @property
    def agency(self) -> str:
        return self._agency

    @property
    def client(self) -> Client:
        return self._client

    @property
    def history(self) -> 'History':
        return self._history

    def withdraw(self, amount: float) -> bool:
        if amount > self._balance:
            print("\n@@@ Operation failed! You do not have sufficient balance. @@@")
            return False

        if amount > 0:
            self._balance -= amount
            print("\n=== Withdrawal successful! ===")
            return True

        print("\n@@@ Operation failed! The entered value is invalid. @@@")
        return False

    def deposit(self, amount: float) -> bool:
        if amount > 0:
            self._balance += amount
            print("\n=== Deposit successful! ===")
            return True

        print("\n@@@ Operation failed! The entered value is invalid. @@@")
        return False


class CheckingAccount(Account):
    def __init__(self, number: int, client: Client, limit: float = 500, withdraw_limit: int = 3):
        super().__init__(number, client)
        self.limit = limit
        self.withdraw_limit = withdraw_limit

    def withdraw(self, amount: float) -> bool:
        withdraw_count = len(
            [transaction for transaction in self.history.transactions if transaction["type"] == Withdraw.__name__]
        )

        if amount > self.limit:
            print("\n@@@ Operation failed! The withdrawal amount exceeds the limit. @@@")
            return False

        if withdraw_count >= self.withdraw_limit:
            print("\n@@@ Operation failed! Maximum number of withdrawals exceeded. @@@")
            return False

        return super().withdraw(amount)

    def __str__(self) -> str:
        return f"""\
            Agency:\t{self.agency}
            C/C:\t\t{self.number}
            Holder:\t{self.client.name}
        """


class History:
    def __init__(self, client: Client):
        self._transactions: List[dict] = []
        self.client = client

    @property
    def transactions(self) -> List[dict]:
        return self._transactions

    def add_transaction(self, transaction: 'Transaction'):
        self._transactions.append(
            {
                "type": transaction.__class__.__name__,
                "amount": transaction.amount,
                "date": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
            }
        )

    def generate_report(self, transaction_type: Optional[str] = None) -> Generator[dict, None, None]:
        for transaction in self._transactions:
            if transaction_type is None or transaction["type"].lower() == transaction_type.lower():
                yield transaction


class Transaction(ABC):
    @property
    @abstractmethod
    def amount(self) -> float:
        pass

    @abstractmethod
    def register(self, account: Account):
        pass


class Withdraw(Transaction):
    def __init__(self, amount: float):
        self._amount = amount

    @property
    def amount(self) -> float:
        return self._amount

    def register(self, account: Account):
        if account.withdraw(self.amount):
            account.history.add_transaction(self)


class Deposit(Transaction):
    def __init__(self, amount: float):
        self._amount = amount

    @property
    def amount(self) -> float:
        return self._amount

    def register(self, account: Account):
        if account.deposit(self.amount):
            account.history.add_transaction(self)


def log_transaction(func):
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        print(f"{datetime.now()}: {func.__name__.upper()}")
        return result
    return wrapper


def menu() -> str:
    menu_text = """\n
    ================ MENU ================
    [d]\tDeposit
    [w]\tWithdraw
    [e]\tExtract
    [na]\tNew account
    [la]\tList accounts
    [nu]\tNew user
    [q]\tQuit
    => """
    return input(textwrap.dedent(menu_text))


def filter_client(cpf: str, clients: List[Individual]) -> Optional[Individual]:
    for client in clients:
        if client.cpf == cpf:
            return client
    return None


def get_client_account(client: Individual) -> Optional[Account]:
    if not client.accounts:
        print("\n@@@ Client does not have an account! @@@")
        return None

    print("\n=== Choose the account ===")
    for i, account in enumerate(client.accounts, start=1):
        print(f"[{i}] Account {account.number}")

    index = int(input("Enter the account number: ")) - 1

    if 0 <= index < len(client.accounts):
        return client.accounts[index]

    print("\n@@@ Invalid account! @@@")
    return None


@log_transaction
def deposit(clients: List[Individual]):
    cpf = input("Enter the client's CPF: ")
    client = filter_client(cpf, clients)

    if not client:
        print("\n@@@ Client not found! @@@")
        return

    amount = float(input("Enter the deposit amount: "))
    transaction = Deposit(amount)

    account = get_client_account(client)
    if not account:
        return

    make_transaction(account, transaction)


@log_transaction
def withdraw(clients: List[Individual]):
    cpf = input("Enter the client's CPF: ")
    client = filter_client(cpf, clients)

    if not client:
        print("\n@@@ Client not found! @@@")
        return

    amount = float(input("Enter the withdrawal amount: "))
    transaction = Withdraw(amount)

    account = get_client_account(client)
    if not account:
        return

    make_transaction(account, transaction)


@log_transaction
def extract(clients: List[Individual]):
    cpf = input("Enter the client's CPF: ")
    client = filter_client(cpf, clients)

    if not client:
        print("\n@@@ Client not found! @@@")
        return

    account = get_client_account(client)
    if not account:
        return

    print("\n================ EXTRACT ================")
    extract_text = ""
    has_transaction = False
    for transaction in account.history.generate_report(''):
        has_transaction = True
        extract_text += f"\n{transaction['type']}:\n\t${transaction['amount']:.2f}"

    if not has_transaction:
        extract_text = "No transactions have been made"

    print(extract_text)
    print(f"\nBalance:\n\t${account.balance:.2f}")
    print("=========================================")


@log_transaction
def create_client(clients: List[Individual]):
    cpf = input("Enter the client's CPF (numbers only): ")
    client = filter_client(cpf, clients)

    if client:
        print("\n@@@ Client with this CPF already exists! @@@")
        return

    name = input("Enter the full name: ")
    birth_date = input("Enter the birth date (dd-mm-yyyy): ")
    address = input("Enter the address (street, number - neighborhood - city/state): ")

    client = Individual(
        name=name,
        birth_date=birth_date,
        cpf=cpf,
        address=address
    )

    clients.append(client)
    print("\n === Client created successfully! ===")


@log_transaction
def create_account(account_number: int, clients: List[Individual], accounts: List[CheckingAccount]):
    cpf = input("Enter the client's CPF: ")
    client = filter_client(cpf, clients)

    if not client:
        print("\n@@@ Client not found, account creation flow terminated! @@@")
        return

    account = CheckingAccount.new_account(
        client=client,
        number=account_number
    )
    accounts.append(account)
    client.add_account(account)

    print("\n+++++ Account created successfully! +++++")


@log_transaction
def list_accounts(accounts: List[Account]):
    for account in AccountsIterator(accounts):
        print("=" * 100)
        print(textwrap.dedent(str(account)))


def main():
    clients: List[Individual] = []
    accounts: List[CheckingAccount] = []

    while True:
        option = menu()

        if option == "d":
            deposit(clients)

        elif option == "w":
            withdraw(clients)

        elif option == "e":
            extract(clients)

        elif option == "nu":
            create_client(clients)

        elif option == "na":
            account_number = len(accounts) + 1
            create_account(account_number, clients, accounts)

        elif option == "la":
            list_accounts(accounts)

        elif option == "q":
            break

        else:
            print("\n@@@ Invalid operation, please select the desired operation again. @@@")
            continue


if __name__ == "__main__":
    main()
