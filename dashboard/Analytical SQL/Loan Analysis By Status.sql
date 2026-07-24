SELECT 
    LoanType,
    Status,
    COUNT(LoanID) AS TotalLoans,
    SUM(Amount) AS TotalLoanAmount,
    AVG(InterestRate) AS AvgInterestRate
FROM Loans
GROUP BY LoanType, Status
ORDER BY TotalLoanAmount DESC;
