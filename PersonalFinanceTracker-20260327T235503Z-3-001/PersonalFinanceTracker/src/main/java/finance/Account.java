// Account.java
package finance;

import java.util.ArrayList;
import java.util.List;

public abstract class Account implements FinancialAccount {
    private String name;
    private double balance;
    private List<FinancialTransaction> transactions;

    public Account(String name, double initialBalance) {
        this.name = name;
        this.balance = initialBalance;
        this.transactions = new ArrayList<>();
    }

    @Override
    public String getName() {
        return name;
    }

    @Override
    public double getBalance() {
        return balance;
    }

    @Override
    public List<FinancialTransaction> getTransactions() {
        return transactions;
    }

    @Override
    public void addExpense(String description, double amount) {
        Expense expense = new Expense(description, amount);
        transactions.add(expense);
        balance -= amount;
    }

    @Override
    public void addIncome(String description, double amount) {
        Income income = new Income(description, amount);
        transactions.add(income);
        balance += amount;
    }
}
