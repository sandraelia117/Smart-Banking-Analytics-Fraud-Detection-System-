-- =====================================================
-- SMART BANKING ANALYTICS & FRAUD DETECTION SYSTEM
-- Database Schema - CREATE TABLE Statements
-- =====================================================

-- Drop tables if they exist (in correct order due to FK dependencies)
DROP TABLE IF EXISTS Transactions CASCADE;
DROP TABLE IF EXISTS MobileBanking CASCADE;
DROP TABLE IF EXISTS Beneficiaries CASCADE;
DROP TABLE IF EXISTS CreditCards CASCADE;
DROP TABLE IF EXISTS Loans CASCADE;
DROP TABLE IF EXISTS Accounts CASCADE;
DROP TABLE IF EXISTS ATMs CASCADE;
DROP TABLE IF EXISTS Employees CASCADE;
DROP TABLE IF EXISTS Customers CASCADE;
DROP TABLE IF EXISTS Branches CASCADE;

-- =====================================================
-- 1) Branches
-- =====================================================
CREATE TABLE Branches (
    BranchID     SERIAL PRIMARY KEY,
    BranchName   VARCHAR(100) NOT NULL,
    City         VARCHAR(50),
    Region       VARCHAR(50),
    Address      VARCHAR(200),
    Phone        VARCHAR(20)
);

-- =====================================================
-- 2) Employees
-- =====================================================
CREATE TABLE Employees (
    EmployeeID   SERIAL PRIMARY KEY,
    BranchID     INT,
    FirstName    VARCHAR(50) NOT NULL,
    LastName     VARCHAR(50) NOT NULL,
    Position     VARCHAR(50),
    HireDate     DATE,
    Phone        VARCHAR(20),
    Email        VARCHAR(100),
    CONSTRAINT FK_Employees_Branches
        FOREIGN KEY (BranchID) REFERENCES Branches(BranchID)
);

-- =====================================================
-- 3) Customers
-- =====================================================
CREATE TABLE Customers (
    CustomerID   SERIAL PRIMARY KEY,
    FirstName    VARCHAR(50) NOT NULL,
    LastName     VARCHAR(50) NOT NULL,
    DateOfBirth  DATE,
    Gender       VARCHAR(10),
    Email        VARCHAR(100),
    Phone        VARCHAR(20),
    Address      VARCHAR(200),
    City         VARCHAR(50),
    JoinDate     DATE
);

-- =====================================================
-- 4) Accounts
-- =====================================================
CREATE TABLE Accounts (
    AccountID     SERIAL PRIMARY KEY,
    CustomerID    INT NOT NULL,
    BranchID      INT NOT NULL,
    AccountNumber VARCHAR(30) UNIQUE NOT NULL,
    AccountType   VARCHAR(30),
    OpenDate      DATE,
    Balance       DECIMAL(15,2) DEFAULT 0,
    Status        VARCHAR(20),
    CONSTRAINT FK_Accounts_Customers
        FOREIGN KEY (CustomerID) REFERENCES Customers(CustomerID),
    CONSTRAINT FK_Accounts_Branches
        FOREIGN KEY (BranchID) REFERENCES Branches(BranchID)
);

-- =====================================================
-- 5) ATMs
-- =====================================================
CREATE TABLE ATMs (
    ATMID       SERIAL PRIMARY KEY,
    BranchID    INT,
    Location    VARCHAR(200),
    Status      VARCHAR(20),
    CONSTRAINT FK_ATMs_Branches
        FOREIGN KEY (BranchID) REFERENCES Branches(BranchID)
);

-- =====================================================
-- 6) Transactions
-- =====================================================
CREATE TABLE Transactions (
    TransactionID   SERIAL PRIMARY KEY,
    AccountID       INT NOT NULL,
    ATMID           INT NULL,
    EmployeeID      INT NULL,
    TransactionDate TIMESTAMP,
    TransactionType VARCHAR(30),
    Amount          DECIMAL(15,2),
    Channel         VARCHAR(30),
    Status          VARCHAR(20),
    IsFraud         SMALLINT DEFAULT 0,
    CONSTRAINT FK_Transactions_Accounts
        FOREIGN KEY (AccountID) REFERENCES Accounts(AccountID),
    CONSTRAINT FK_Transactions_ATMs
        FOREIGN KEY (ATMID) REFERENCES ATMs(ATMID),
    CONSTRAINT FK_Transactions_Employees
        FOREIGN KEY (EmployeeID) REFERENCES Employees(EmployeeID)
);

-- =====================================================
-- 7) Loans
-- =====================================================
CREATE TABLE Loans (
    LoanID        SERIAL PRIMARY KEY,
    CustomerID    INT NOT NULL,
    EmployeeID    INT,
    LoanType      VARCHAR(30),
    Amount        DECIMAL(15,2),
    InterestRate  DECIMAL(5,2),
    TermMonths    INT,
    EndDate       DATE,
    Status        VARCHAR(20),
    CONSTRAINT FK_Loans_Customers
        FOREIGN KEY (CustomerID) REFERENCES Customers(CustomerID),
    CONSTRAINT FK_Loans_Employees
        FOREIGN KEY (EmployeeID) REFERENCES Employees(EmployeeID)
);

-- =====================================================
-- 8) CreditCards
-- =====================================================
CREATE TABLE CreditCards (
    CardID        SERIAL PRIMARY KEY,
    CustomerID    INT NOT NULL,
    CardNumber    VARCHAR(30) UNIQUE,
    CardType      VARCHAR(30),
    IssueDate     DATE,
    ExpiryDate    DATE,
    CreditLimit   DECIMAL(15,2),
    Status        VARCHAR(20),
    CONSTRAINT FK_CreditCards_Customers
        FOREIGN KEY (CustomerID) REFERENCES Customers(CustomerID)
);

-- =====================================================
-- 9) Beneficiaries
-- =====================================================
CREATE TABLE Beneficiaries (
    BeneficiaryID  SERIAL PRIMARY KEY,
    CustomerID     INT NOT NULL,
    CustomerName   VARCHAR(100),
    AccountNumber  VARCHAR(30),
    BankName       VARCHAR(50),
    Relationship   VARCHAR(50),
    Status         VARCHAR(20),
    CONSTRAINT FK_Beneficiaries_Customers
        FOREIGN KEY (CustomerID) REFERENCES Customers(CustomerID)
);

-- =====================================================
-- 10) MobileBanking
-- =====================================================
CREATE TABLE MobileBanking (
    MobileID       SERIAL PRIMARY KEY,
    CustomerID     INT NOT NULL,
    AppUserID      VARCHAR(50),
    DeviceID       VARCHAR(50),
    RegisteredDate DATE,
    Status         VARCHAR(20),
    CONSTRAINT FK_MobileBanking_Customers
        FOREIGN KEY (CustomerID) REFERENCES Customers(CustomerID)
);