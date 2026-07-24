-- =====================================================
-- DATA WAREHOUSE (dw) - STAR SCHEMA
-- Fact Table: Fact_Transactions | Grain: One transaction record
-- PostgreSQL
-- =====================================================

CREATE SCHEMA IF NOT EXISTS dw;

-- Drop tables if they exist (fact first, then dimensions)
DROP TABLE IF EXISTS Fact_Transactions CASCADE;
DROP TABLE IF EXISTS DimCustomer CASCADE;
DROP TABLE IF EXISTS DimDate CASCADE;
DROP TABLE IF EXISTS DimBranch CASCADE;
DROP TABLE IF EXISTS DimAccount CASCADE;
DROP TABLE IF EXISTS DimEmployee CASCADE;
DROP TABLE IF EXISTS DimLoan CASCADE;

-- =====================================================
-- 1) DimCustomer
-- =====================================================
CREATE TABLE DimCustomer (
    CustomerKey   SERIAL PRIMARY KEY,
    CustomerID    INT NOT NULL UNIQUE,        -- Natural Key
    FirstName     VARCHAR(50),
    LastName      VARCHAR(50),
    DateOfBirth   DATE,
    Gender        VARCHAR(10),
    Email         VARCHAR(100),
    Phone         VARCHAR(20),
    Address       VARCHAR(200),
    City          VARCHAR(50),
    JoinDate      DATE
);

-- =====================================================
-- 2) DimDate
-- =====================================================
CREATE TABLE DimDate (
    DateKey       SERIAL PRIMARY KEY,
    FullDate      DATE NOT NULL UNIQUE,
    Day           INT,
    DayName       VARCHAR(15),
    Week          INT,
    Month         INT,
    MonthName     VARCHAR(15),
    Quarter       INT,
    Year          INT,
    IsWeekend     BOOLEAN DEFAULT FALSE,
    IsHoliday     BOOLEAN DEFAULT FALSE
);

-- =====================================================
-- 3) DimBranch
-- =====================================================
CREATE TABLE DimBranch (
    BranchKey     SERIAL PRIMARY KEY,
    BranchID      INT NOT NULL UNIQUE,        -- Natural Key
    BranchName    VARCHAR(100),
    City          VARCHAR(50),
    Region        VARCHAR(50),
    ManagerName   VARCHAR(100),
    OpeningDate   DATE
);

-- =====================================================
-- 4) DimAccount
-- =====================================================
CREATE TABLE DimAccount (
    AccountKey    SERIAL PRIMARY KEY,
    AccountID     INT NOT NULL UNIQUE,        -- Natural Key
    AccountNumber VARCHAR(30),
    AccountType   VARCHAR(30),
    OpenDate      DATE,
    Status        VARCHAR(20)
);

-- =====================================================
-- 5) DimEmployee
-- =====================================================
CREATE TABLE DimEmployee (
    EmployeeKey   SERIAL PRIMARY KEY,
    EmployeeID    INT NOT NULL UNIQUE,        -- Natural Key
    FirstName     VARCHAR(50),
    LastName      VARCHAR(50),
    Position      VARCHAR(50),
    HireDate      DATE,
    Status        VARCHAR(20)
);

-- =====================================================
-- 6) DimLoan
-- =====================================================
CREATE TABLE DimLoan (
    LoanKey       SERIAL PRIMARY KEY,
    LoanID        INT NOT NULL UNIQUE,        -- Natural Key
    LoanType      VARCHAR(30),
    AmountRange   VARCHAR(30),
    InterestRate  DECIMAL(5,2),
    TermMonths    INT,
    Status        VARCHAR(20)
);

-- =====================================================
-- 7) Fact_Transactions
-- =====================================================
CREATE TABLE Fact_Transactions (
    TransactionKey          SERIAL PRIMARY KEY,
    DateKey                 INT NOT NULL,
    CustomerKey             INT NOT NULL,
    BranchKey               INT NOT NULL,
    AccountKey              INT NOT NULL,
    EmployeeKey             INT,
    LoanKey                 INT,

    -- Measures
    TransactionCount        INT DEFAULT 1,
    TransactionAmount       DECIMAL(15,2) DEFAULT 0,
    DepositAmount           DECIMAL(15,2) DEFAULT 0,
    WithdrawalAmount        DECIMAL(15,2) DEFAULT 0,
    TransferAmount          DECIMAL(15,2) DEFAULT 0,
    LoanDisbursementAmount  DECIMAL(15,2) DEFAULT 0,
    LoanRepaymentAmount     DECIMAL(15,2) DEFAULT 0,
    InterestAmount          DECIMAL(15,2) DEFAULT 0,
    FeeAmount               DECIMAL(15,2) DEFAULT 0,
    FraudAmount             DECIMAL(15,2) DEFAULT 0,

    CONSTRAINT FK_Fact_DimDate
        FOREIGN KEY (DateKey) REFERENCES DimDate(DateKey),
    CONSTRAINT FK_Fact_DimCustomer
        FOREIGN KEY (CustomerKey) REFERENCES DimCustomer(CustomerKey),
    CONSTRAINT FK_Fact_DimBranch
        FOREIGN KEY (BranchKey) REFERENCES DimBranch(BranchKey),
    CONSTRAINT FK_Fact_DimAccount
        FOREIGN KEY (AccountKey) REFERENCES DimAccount(AccountKey),
    CONSTRAINT FK_Fact_DimEmployee
        FOREIGN KEY (EmployeeKey) REFERENCES DimEmployee(EmployeeKey),
    CONSTRAINT FK_Fact_DimLoan
        FOREIGN KEY (LoanKey) REFERENCES DimLoan(LoanKey)
);

-- Helpful indexes on FK columns of the fact table (common in star schemas)
CREATE INDEX idx_fact_datekey     ON Fact_Transactions(DateKey);
CREATE INDEX idx_fact_customerkey ON Fact_Transactions(CustomerKey);
CREATE INDEX idx_fact_branchkey   ON Fact_Transactions(BranchKey);
CREATE INDEX idx_fact_accountkey  ON Fact_Transactions(AccountKey);
CREATE INDEX idx_fact_employeekey ON Fact_Transactions(EmployeeKey);
CREATE INDEX idx_fact_loankey     ON Fact_Transactions(LoanKey);