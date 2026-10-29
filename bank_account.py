class BankAccount:
    def __init__(self, owner, balance=0):
        self.owner = owner
        self._balance = balance
        self._history = []

    @property
    def owner(self):
        return self._owner

    @owner.setter
    def owner(self, owner):
        if owner.strip() == '':
            raise ValueError("Owner name can't be empty")
        else:
            self._owner = owner.strip()

    @property
    def balance(self):
        return self._balance

    @staticmethod
    def is_valid_amount(amount):
        return isinstance(amount, (int, float)) and amount > 0

    def deposit(self, amount):
        if not self.is_valid_amount(amount):
            raise ValueError('Amount must be positive')
        self._balance += amount
        self._history.append(("deposit", amount))
        return self._balance

    def withdraw(self, amount):
        if not self.is_valid_amount(amount):
            raise ValueError('Amount must be positive')
        elif amount > self._balance:
            raise ValueError(f'Insufficient funds: balance {self._balance}, requested {amount}')
        self._balance -= amount
        self._history.append(("withdraw", amount))
        return self._balance

    @property
    def history(self):
        return tuple(self._history)

    @classmethod
    def from_string(cls, line):
        owner, balance = line.split(':')
        return cls(owner, int(balance))

    def __repr__(self):
        return f"BankAccount(owner={self.owner!r}, balance={self.balance})"


if __name__ == "__main__":
    acc = BankAccount.from_string(" Ihor :250")
    print(acc)
    print(acc.deposit(50))
    print(acc.withdraw(100))

    try:
        acc.withdraw(1000)
    except ValueError as e:
        print(f"Error: {e}")

    try:
        acc.deposit(-5)
    except ValueError as e:
        print(f"Error: {e}")

    try:
        acc.balance = 1_000_000
    except AttributeError as e:
        print(f"Error: {e}")

    try:
        BankAccount("   ")
    except ValueError as e:
        print(f"Error: {e}")

    print(acc.history)
    print(BankAccount.is_valid_amount(0), BankAccount.is_valid_amount(10))