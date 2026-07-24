SELECT 
    b.BranchID,
    b.BranchName,
    b.City,
    SUM(t.Amount) AS TotalBranchAmount,
    RANK() OVER (ORDER BY SUM(t.Amount) DESC) AS BranchRank
FROM Branches b
JOIN Accounts a ON b.BranchID = a.BranchID
JOIN Transactions t ON a.AccountID = t.AccountID
GROUP BY b.BranchID, b.BranchName, b.City;
