SELECT 
    CardType,
    COUNT(CardID) AS TotalCards,
    SUM(CreditLimit) AS TotalCreditLimit,
    AVG(CreditLimit) AS AvgCreditLimit
FROM CreditCards
WHERE Status = 'Active'
GROUP BY CardType;
