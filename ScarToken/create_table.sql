CREATE TABLE `scar` (
	`id` BIGINT(20) NOT NULL AUTO_INCREMENT,
	`supply` FLOAT NOT NULL,
	`price` FLOAT NOT NULL,
	`storage_datetime` DATETIME NOT NULL,
	PRIMARY KEY (`id`)
)
COLLATE='utf32_bin'
ENGINE=InnoDB
AUTO_INCREMENT=0
;