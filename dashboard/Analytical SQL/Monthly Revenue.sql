SELECT 
    DATE_TRUNC('month', TransactionDate) AS TransactionMonth,
    COUNT(TransactionID) AS TransactionCount,
    SUM(Amount) AS TotalMonthlyAmount
FROM Transactions
GROUP BY TransactionMonth
ORDER BY TransactionMonth ASC;
