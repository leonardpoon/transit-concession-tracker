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

CREATE USER IF NOT EXISTS 'transit_user'@'localhost' IDENTIFIED BY  '';

GRANT SELECT, INSERT, UPDATE, DELETE ON transit_tracker.* to 'transit_user'@'localhost';
FLUSH PRIVILEGES;

SELECT 'Setup complete!' AS status;