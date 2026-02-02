CREATE DATABASE personal_finance;
USE personal_finance;

CREATE TABLE transactions (
    transaction_id INT AUTO_INCREMENT PRIMARY KEY,
    transaction_date DATE NOT NULL,
    transaction_type ENUM('Income', 'Expense') NOT NULL,
    category VARCHAR(50) NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    payment_mode ENUM('Cash', 'UPI', 'Card', 'Bank Transfer') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP
);

DELIMITER $$

CREATE TRIGGER trg_amount_check_insert
BEFORE INSERT ON transactions
FOR EACH ROW
BEGIN
    IF NEW.amount <= 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Amount must be greater than zero';
    END IF;
END$$

DELIMITER ;

DELIMITER $$

CREATE TRIGGER trg_date_check_insert
BEFORE INSERT ON transactions
FOR EACH ROW
BEGIN
    IF NEW.transaction_date > CURDATE() THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Future dates are not allowed';
    END IF;
END$$

DELIMITER ;

DELIMITER $$

CREATE TRIGGER trg_validate_update
BEFORE UPDATE ON transactions
FOR EACH ROW
BEGIN
    IF NEW.amount <= 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Amount must be greater than zero';
    END IF;

    IF NEW.transaction_date > CURDATE() THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Future dates are not allowed';
    END IF;
END$$

DELIMITER ;

INSERT INTO transactions(transaction_date, transaction_type, category, amount, payment_mode)
VALUES('2024-04-10', 'Expense', 'Food', 250.00, 'UPI');

INSERT INTO transactions(transaction_date, transaction_type, category, amount, payment_mode)
VALUES('2026-01-01', 'Expense', 'Rent', -5000, 'Cash');
