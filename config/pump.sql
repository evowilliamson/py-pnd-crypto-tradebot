CREATE TABLE `pump` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `ticker_symbol` varchar(255) NOT NULL,
  `start_time` datetime NOT NULL,
  `quantity` float NOT NULL,
  `initial_price` float NOT NULL,
  `first_pump_price` float NOT NULL,
  `initial_volume` float NOT NULL,
  `first_pump_volume` float NOT NULL,
  `stop_loss` float NOT NULL,
  `end_time` datetime DEFAULT NULL,
  `end_price` float DEFAULT NULL,
  `profit_pct` float DEFAULT NULL,
  `status` varchar(50) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=latin1;
