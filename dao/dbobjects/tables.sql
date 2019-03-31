CREATE TABLE `trade_bot`.`pump` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `ticker_symbol` VARCHAR(255) NULL,
  `start_time` DATETIME NULL,
  `quantity` FLOAT NULL,
  `initial_price` FLOAT NULL,
  `first_pump_price` FLOAT NULL,
  `buy_price` FLOAT NULL,
  `initial_volume` FLOAT NULL,
  `first_pump_volume` FLOAT NULL,
  `stop_loss` FLOAT NULL,
  `end_time` DATETIME NULL,
  `end_price` FLOAT NULL,
  `profit_pct` FLOAT NULL,
  `status` VARCHAR(50) NULL,
  PRIMARY KEY (`id`));

CREATE TABLE `trade_bot`.`pump_history` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `pump_id` INT NULL,
  `timestamp` DATETIME NULL,
  `price` FLOAT NULL,
  `volume` FLOAT NULL,
  PRIMARY KEY (`id`));
