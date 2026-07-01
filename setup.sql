CREATE DATABASE IF NOT EXISTS transit_tracker;
USE transit_tracker;

CREATE TABLE IF NOT EXISTS TRIPS (
    id INT AUTO_INCREMENT PRIMARY KEY,
    mode_of_transport ENUM('Bus', 'Train') NOT NULL,
    starting_location VARCHAR(255) NOT NULL,
    ending_location VARCHAR(255) NOT NULL,
    total_price DECIMAL(10, 2) NOT NULL,
    date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_date (date),
    INDEX idx_mode (mode_of_transport),
    INDEX idx_starting_location (starting_location),
    INDEX idx_ending_location (ending_location)
);

CREATE TABLE IF NOT EXISTS concession_periods (
    id INT AUTO_INCREMENT PRIMARY KEY,
    start_date DATE NOT NULL,
    end_date DATE NULL,
    cycle_reset_day INT NOT NULL,
    threshold_amount DECIMAL(10, 2) NOT NULL,
    label VARCHAR(255) NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_period_dates (start_date, end_date)
);

INSERT INTO concession_periods (
    start_date,
    end_date,
    cycle_reset_day,
    threshold_amount,
    label
)
SELECT COALESCE((SELECT MIN(date) FROM trips), CURRENT_DATE()), NULL, 3, 81.00, 'Legacy concession'
WHERE NOT EXISTS (SELECT 1 FROM concession_periods);

CREATE USER IF NOT EXISTS 'transit_user'@'localhost' IDENTIFIED BY  '';

GRANT SELECT, INSERT, UPDATE, DELETE ON transit_tracker.* to 'transit_user'@'localhost';
FLUSH PRIVILEGES;

SELECT 'Setup complete!' AS status;
