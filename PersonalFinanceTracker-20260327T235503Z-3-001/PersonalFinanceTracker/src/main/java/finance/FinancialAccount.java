/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/Classes/Interface.java to edit this template
 */
// FinancialAccount.java
package finance;

import java.util.List;

public interface FinancialAccount {
    String getName();
    double getBalance();
    List<FinancialTransaction> getTransactions();
    void addExpense(String description, double amount);
    void addIncome(String description, double amount);
}
