-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Apr 02, 2026 at 05:42 PM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `account18_db`
--

-- --------------------------------------------------------

--
-- Table structure for table `account_items`
--

CREATE TABLE `account_items` (
  `account_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `site` varchar(150) NOT NULL,
  `account_username` varchar(150) NOT NULL,
  `account_password` varchar(255) NOT NULL,
  `account_image` varchar(255) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `account_items`
--

INSERT INTO `account_items` (`account_id`, `user_id`, `site`, `account_username`, `account_password`, `account_image`, `created_at`, `updated_at`) VALUES
(2, 4, 'facebook.com', 'anthony', '12345678', '/uploads/account/20260402173031281549.jpg', '2026-03-27 13:42:23', '2026-04-02 09:30:31');

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `user_id` int(11) NOT NULL,
  `username` varchar(100) NOT NULL,
  `fullname` varchar(150) NOT NULL,
  `email` varchar(150) NOT NULL,
  `password` varchar(255) NOT NULL,
  `profile_image` varchar(255) DEFAULT NULL,
  `token` text DEFAULT NULL,
  `is_verified` tinyint(1) NOT NULL DEFAULT 0,
  `verification_token` varchar(255) DEFAULT NULL,
  `reset_token` varchar(255) DEFAULT NULL,
  `reset_token_expires` datetime DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`user_id`, `username`, `fullname`, `email`, `password`, `profile_image`, `token`, `is_verified`, `verification_token`, `reset_token`, `reset_token_expires`, `created_at`, `updated_at`) VALUES
(4, 'anthonyjames.nabasca', 'Anthony Nabasca', 'anthonyjames.nabasca001@deped.gov.ph', 'scrypt:32768:8:1$qkThME6jrxUm1bF0$ebb4726cfa3c7cbfc63a17a08455b65c6efd187d540a69296b34ad650eb5856f2a2ab1e2ece2eb17234cc7f10d446af7730cdf8afccc16a035ef5f75b84f1bdd', NULL, 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjo0LCJ1c2VybmFtZSI6ImFudGhvbnlqYW1lcy5uYWJhc2NhIiwiZW1haWwiOiJhbnRob255amFtZXMubmFiYXNjYTAwMUBkZXBlZC5nb3YucGgiLCJleHAiOjE3NzUyMDc4ODF9.3ctiST9qXk0jAqYoCEja7bQxFW_JEuWIU2f9LlcbdnI', 1, NULL, NULL, NULL, '2026-03-27 13:30:14', '2026-04-02 09:18:01'),
(5, 'anthony.nabasca', 'Anthony  Biador Nabasca', 'anthonyjames.nabasca@deped.gov.ph', 'scrypt:32768:8:1$95Txb1RwP4JMOatf$8710d22030055847152e988e34a1e1bd9acff86e1c06afe4fd79cfe926494e23b92f01c9c48a665ff8d04eba2e5505e39676b00a5d2ead625b78af110664566e', '/uploads/profile/20260402233655971085.jpg', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjo1LCJ1c2VybmFtZSI6ImFudGhvbnkubmFiYXNjYSIsImVtYWlsIjoiYW50aG9ueWphbWVzLm5hYmFzY2FAZGVwZWQuZ292LnBoIiwiZXhwIjoxNzc1MjMwNTQzfQ.RCIIH6xfun0Srr129Xu_syyy2b5Dxlv4YI2pe8Sr1DY', 1, NULL, NULL, NULL, '2026-04-02 15:34:12', '2026-04-02 15:36:55');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `account_items`
--
ALTER TABLE `account_items`
  ADD PRIMARY KEY (`account_id`),
  ADD KEY `fk_account_items_user` (`user_id`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`user_id`),
  ADD UNIQUE KEY `username` (`username`),
  ADD UNIQUE KEY `email` (`email`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `account_items`
--
ALTER TABLE `account_items`
  MODIFY `account_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `user_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `account_items`
--
ALTER TABLE `account_items`
  ADD CONSTRAINT `fk_account_items_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE ON UPDATE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
