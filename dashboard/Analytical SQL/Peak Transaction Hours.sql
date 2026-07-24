SELECT 
    c.CustomerID,
    c.FirstName || ' ' || c.LastName AS CustomerName,
    SUM(a.Balance) AS TotalBalance,
    CASE 
        WHEN SUM(a.Balance) >= 100000 THEN 'VIP'
        WHEN SUM(a.Balance) >= 50000 THEN 'High Value'
        WHEN SUM(a.Balance) >= 10000 THEN 'Medium Value'
        ELSE 'Low Value'
    END AS CustomerSegment
FROM Customers c
JOIN Accounts a ON c.CustomerID = a.CustomerID
GROUP BY c.CustomerID, CustomerName;
