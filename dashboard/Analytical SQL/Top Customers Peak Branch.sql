WITH RankedCustomers AS (
    SELECT 
        b.BranchName,
        c.CustomerID,
        c.FirstName || ' ' || c.LastName AS CustomerName,
        SUM(t.Amount) AS TotalSpent,
        DENSE_RANK() OVER (
            PARTITION BY b.BranchID 
            ORDER BY SUM(t.Amount) DESC
        ) AS RankInBranch
    FROM Branches b
    JOIN Accounts a ON b.BranchID = a.BranchID
    JOIN Customers c ON a.CustomerID = c.CustomerID
    JOIN Transactions t ON a.AccountID = t.AccountID
    GROUP BY b.BranchID, b.BranchName, c.CustomerID, CustomerName
)
SELECT 
    BranchName,
    CustomerName,
    TotalSpent,
    RankInBranch
FROM RankedCustomers
WHERE RankInBranch = 1;
