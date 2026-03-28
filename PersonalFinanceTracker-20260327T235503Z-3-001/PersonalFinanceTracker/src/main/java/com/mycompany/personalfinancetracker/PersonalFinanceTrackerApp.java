/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 */

package com.mycompany.personalfinancetracker;

import finance.Account;
import finance.FinancialAccount;
import finance.FinancialTransaction;

/**
 *
 * @author Acer
 */
public class PersonalFinanceTrackerApp {
    public static void main(String[] args) {
        // Create an account with an initial balance
        FinancialAccount myAccount = new Account("My Personal Account", 1000.0) {};

        // Record expenses and income
        myAccount.addExpense("Groceries", 50.0);
        myAccount.addExpense("Utilities", 100.0);
        myAccount.addIncome("Salary", 2000.0);

        // Display account balance and transactions
        System.out.println("Account Name: " + myAccount.getName());
        System.out.println("Current Balance: $" + myAccount.getBalance());
        System.out.println("Transactions:");

        for (FinancialTransaction transaction : myAccount.getTransactions()) {
            System.out.println(transaction.getDescription() + ": $" + transaction.getAmount());
        }
    }
}
