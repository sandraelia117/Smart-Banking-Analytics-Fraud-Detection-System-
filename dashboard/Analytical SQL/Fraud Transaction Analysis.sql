WITH FraudStats AS (
    SELECT 
        Channel,
        COUNT(*) AS TotalTxns,
        SUM(CASE WHEN IsFraud = 1 THEN 1 ELSE 0 END) AS FraudTxns,
        SUM(CASE WHEN IsFraud = 1 THEN Amount ELSE 0 END) AS FraudAmount
    FROM Transactions
    GROUP BY Channel
)
SELECT 
    Channel,
    TotalTxns,
    FraudTxns,
    FraudAmount,
    ROUND((FraudTxns::NUMERIC / TotalTxns) * 100, 2) AS FraudPercentage
FROM FraudStats
ORDER BY FraudPercentage DESC;
