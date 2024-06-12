-- drop schema if exists app;

-- create schema if not exists app;

use app;

-- Create Event table
CREATE TABLE IF NOT exists Event (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    date DATE NOT NULL,
    time TIME NOT NULL,
    venue VARCHAR(100) NOT NULL,
    n_of_sits INT NOT NULL,
    standard_ticket_price DECIMAL(10, 2),
    vip_ticket_price DECIMAL(10, 2),
    num_vip_tickets INT DEFAULT 0
);

-- Create User table
CREATE TABLE IF NOT exists user (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL,
    surname VARCHAR(50) NOT NULL
);

-- Create Performer table
CREATE TABLE IF NOT exists Performer (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    surname VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT exists ticket (
    id INT PRIMARY KEY AUTO_INCREMENT,
    event_id INT,
    price DECIMAL(10 , 2 ) NOT NULL,
    type VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL,
    ticket_n INT,
    user_id INT,
    FOREIGN KEY (event_id)
        REFERENCES Event (id)
);

CREATE TABLE IF NOT EXISTS Contract (
    id INT AUTO_INCREMENT PRIMARY KEY,
    event_id INT,
    performer_id INT,
    FOREIGN KEY (event_id)
        REFERENCES Event (id),
    FOREIGN KEY (performer_id)
        REFERENCES Performer (id)
);
