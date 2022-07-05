/*
* Script 1 
*/

CREATE DATABASE `db_signals` ;

/*
* Script 2
*/
CREATE TABLE `measures` (
  `idPatient` int(11) NOT NULL,
  `sessionNum` varchar(250) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL,
  `instrumentId` varchar(250) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL,
  `signalType` varchar(250) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL,
  `value` double NOT NULL,
  `timeMeasure` double NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci

/*
* Script 3
*/

CREATE TABLE `variables_mesure` (
  `idPatient` int(11) NOT NULL,
  `sessionNum` varchar(250) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL,
  `instrumentId` varchar(250) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL,
  `signalName` varchar(250) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL,
  `signalNameTreaded` varchar(250) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci

SHOW GLOBAL VARIABLES where variable_name like'%packet%';
SET GLOBAL connect_timeout=300;
SET GLOBAL max_allowed_packet=1073741824;