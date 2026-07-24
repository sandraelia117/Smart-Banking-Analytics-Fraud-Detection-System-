SELECT 
    c.CustomerID,
    c.FirstName || ' ' || c.LastName AS CustomerName,
    COUNT(t.TransactionID) AS TotalTransactions,
    SUM(t.Amount) AS TotalSpentAmount
FROM Customers c
JOIN Accounts a ON c.CustomerID = a.CustomerID
JOIN Transactions t ON a.AccountID = t.AccountID
GROUP BY c.CustomerID, CustomerName
ORDER BY TotalSpentAmount DESC
LIMIT 10;
