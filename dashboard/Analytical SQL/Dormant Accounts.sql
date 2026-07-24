SELECT 
    a.AccountID,
    a.AccountNumber,
    c.FirstName || ' ' || c.LastName AS OwnerName,
    a.Balance,
    MAX(t.TransactionDate) AS LastTransactionDate
FROM Accounts a
JOIN Customers c ON a.CustomerID = c.CustomerID
LEFT JOIN Transactions t ON a.AccountID = t.AccountID
GROUP BY a.AccountID, a.AccountNumber, OwnerName, a.Balance
HAVING MAX(t.TransactionDate) < CURRENT_DATE - INTERVAL '6 months' 
   OR MAX(t.TransactionDate) IS NULL;
