CREATE DATABASE IF NOT EXISTS smart_tafel;
USE smart_tafel;

CREATE TABLE IF NOT EXISTS `scan` (
  `id` INT unsigned NOT NULL AUTO_INCREMENT,
  `timestamp` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `language` ENUM('nl', 'en') DEFAULT NULL,
  `name` TINYTEXT DEFAULT NULL,
  `email` TINYTEXT DEFAULT NULL,
  `phone` TINYTEXT DEFAULT NULL,
  `date` TINYTEXT DEFAULT NULL,
  `bedrijf` TINYTEXT DEFAULT NULL,
  `teelt` TINYTEXT DEFAULT NULL,
  `fotographer` TINYTEXT DEFAULT NULL,
  `desc` TINYTEXT DEFAULT NULL,
  `audio` BOOLEAN DEFAULT 0,
  `location` GEOMETRY,
  `state` ENUM('ready_audio', 'ready_loc', 'done', 'canceled', 'removed') DEFAULT 'ready_audio',
  `vector` TEXT DEFAULT NULL,
  `aes_score` FLOAT DEFAULT NULL,
  `sim_score` FLOAT DEFAULT NULL,
  `loc_score` FLOAT DEFAULT NULL,
  `total_score` FLOAT DEFAULT NULL,
  PRIMARY KEY (`id`)
);

COMMIT;
