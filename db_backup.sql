-- MySQL dump 10.13  Distrib 5.7.27, for Linux (x86_64)
--

-- ------------------------------------------------------
-- Server version	5.7.34-log

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `allign_at_to_clo_m_to_m`
--

DROP TABLE IF EXISTS `allign_at_to_clo_m_to_m`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `allign_at_to_clo_m_to_m` (
  `id_allign_at_to_clo_m_to_m` int(11) NOT NULL AUTO_INCREMENT,
  `clo_name` varchar(100) NOT NULL,
  `assessment_name` varchar(45) NOT NULL,
  `course_id` varchar(45) NOT NULL,
  `assessment_auto_increment` int(11) DEFAULT NULL,
  `clo_auto_increment` int(11) DEFAULT NULL,
  PRIMARY KEY (`id_allign_at_to_clo_m_to_m`),
  KEY `assessment_auto_idx` (`assessment_auto_increment`),
  KEY `clo_auto_idx` (`clo_auto_increment`),
  KEY `course_fk_idx` (`course_id`),
  CONSTRAINT `assessment_auto` FOREIGN KEY (`assessment_auto_increment`) REFERENCES `assessment` (`auto_increment`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `clo_auto` FOREIGN KEY (`clo_auto_increment`) REFERENCES `clo` (`auto_increment`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `course_fk` FOREIGN KEY (`course_id`) REFERENCES `course` (`course_id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=151 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `allign_tla_to_at_m_to_m`
--

DROP TABLE IF EXISTS `allign_tla_to_at_m_to_m`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `allign_tla_to_at_m_to_m` (
  `id_allign_tla_to_at_m_to_m` int(11) NOT NULL AUTO_INCREMENT,
  `assessment_name` varchar(45) NOT NULL,
  `tla_id` int(11) NOT NULL,
  `course_id` varchar(45) NOT NULL,
  `assessment_auto_inc` int(11) DEFAULT NULL,
  PRIMARY KEY (`id_allign_tla_to_at_m_to_m`),
  KEY `assessment_auto_inc_idx` (`assessment_auto_inc`),
  KEY `course_id_fk_idx` (`course_id`),
  KEY `tla_fk_m_idx` (`tla_id`),
  CONSTRAINT `assessment_auto_inc` FOREIGN KEY (`assessment_auto_inc`) REFERENCES `assessment` (`auto_increment`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `course_id_fk` FOREIGN KEY (`course_id`) REFERENCES `course` (`course_id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `tla_fk_m` FOREIGN KEY (`tla_id`) REFERENCES `tla` (`tla_id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=411 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `allign_tla_to_clo_m_to_m`
--

DROP TABLE IF EXISTS `allign_tla_to_clo_m_to_m`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `allign_tla_to_clo_m_to_m` (
  `id_allign_tla_to_clo_m_to_m` int(11) NOT NULL AUTO_INCREMENT,
  `clo_name` varchar(100) NOT NULL,
  `tla_id` int(11) NOT NULL,
  `course_id` varchar(45) NOT NULL,
  `clo_auto_increment` int(11) DEFAULT NULL,
  PRIMARY KEY (`id_allign_tla_to_clo_m_to_m`),
  KEY `tla_course_fk_idx` (`course_id`),
  KEY `tla_fk_idx` (`tla_id`),
  KEY `clo_auto_fk_idx` (`clo_auto_increment`),
  CONSTRAINT `clo_auto_fk` FOREIGN KEY (`clo_auto_increment`) REFERENCES `clo` (`auto_increment`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `tla_course_fk` FOREIGN KEY (`course_id`) REFERENCES `course` (`course_id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `tla_fk` FOREIGN KEY (`tla_id`) REFERENCES `tla` (`tla_id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=342 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `assessment`
--

DROP TABLE IF EXISTS `assessment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `assessment` (
  `assessment_name` varchar(45) NOT NULL,
  `course_course_id` varchar(45) NOT NULL,
  `auto_increment` int(11) NOT NULL AUTO_INCREMENT,
  `mark_out` int(11) DEFAULT NULL,
  `mark_worth` int(11) DEFAULT NULL,
  PRIMARY KEY (`assessment_name`,`course_course_id`),
  UNIQUE KEY `auto_increment_UNIQUE` (`auto_increment`),
  KEY `fk_kcourse_assessment` (`course_course_id`),
  CONSTRAINT `fk_kcourse_assessment` FOREIGN KEY (`course_course_id`) REFERENCES `course` (`course_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=544 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `assessment_std`
--

DROP TABLE IF EXISTS `assessment_std`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `assessment_std` (
  `assessment_std_id` int(11) NOT NULL AUTO_INCREMENT,
  `assessment_assessment_name` varchar(45) DEFAULT NULL,
  `assessment_course_course_id` varchar(45) DEFAULT NULL,
  `student_student_id` int(11) DEFAULT NULL,
  `mark` int(11) DEFAULT NULL,
  PRIMARY KEY (`assessment_std_id`),
  KEY `fk_student_student_id_idx` (`student_student_id`),
  CONSTRAINT `fk_student_id` FOREIGN KEY (`student_student_id`) REFERENCES `student` (`student_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=228755 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `at_map_to_tla`
--

DROP TABLE IF EXISTS `at_map_to_tla`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `at_map_to_tla` (
  `assessment_name` varchar(45) NOT NULL,
  `course_course_id` varchar(45) NOT NULL,
  `assessment_part` int(11) DEFAULT NULL,
  `assessment_task` int(11) DEFAULT NULL,
  `tla_id` int(11) NOT NULL,
  `auto_increment` int(11) NOT NULL AUTO_INCREMENT,
  `userName` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`assessment_name`,`course_course_id`,`tla_id`),
  UNIQUE KEY `auto_increment_UNIQUE` (`auto_increment`),
  KEY `fk_course_AT_map_to_TLA_idx` (`course_course_id`),
  KEY `fk_TLA_AT_map_to_TLA_idx` (`tla_id`),
  KEY `fk_assessment_AT_map_to_TLA_idx` (`assessment_name`),
  CONSTRAINT `fk_TLA_TLA_AT_map` FOREIGN KEY (`tla_id`) REFERENCES `tla` (`tla_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_course_AT_map_to_TLA` FOREIGN KEY (`course_course_id`) REFERENCES `course` (`course_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_course_map_to_TLA` FOREIGN KEY (`assessment_name`) REFERENCES `assessment` (`assessment_name`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `clo`
--

DROP TABLE IF EXISTS `clo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `clo` (
  `clo_name` varchar(200) NOT NULL,
  `course_course_id` varchar(45) NOT NULL,
  `clo_level` int(11) DEFAULT NULL,
  `auto_increment` int(11) NOT NULL AUTO_INCREMENT,
  `parent_clo` varchar(100) DEFAULT NULL,
  `userName` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`clo_name`,`course_course_id`),
  UNIQUE KEY `auto_increment_UNIQUE` (`auto_increment`),
  KEY `fk_course_clo_idx` (`course_course_id`),
  CONSTRAINT `fk_course_clo` FOREIGN KEY (`course_course_id`) REFERENCES `course` (`course_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=170 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `course`
--

DROP TABLE IF EXISTS `course`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `course` (
  `course_id` varchar(45) NOT NULL,
  `course_name` varchar(45) DEFAULT NULL,
  `course_description` longtext,
  `userName` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`course_id`),
  KEY `userName` (`userName`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `course_and_models`
--

DROP TABLE IF EXISTS `course_and_models`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `course_and_models` (
  `course_id` varchar(45) NOT NULL,
  `course_name` varchar(45) DEFAULT NULL,
  `userName` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`course_id`),
  KEY `userName_idx` (`userName`),
  CONSTRAINT `course_model_user` FOREIGN KEY (`userName`) REFERENCES `users` (`userName`) ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `current_student`
--

DROP TABLE IF EXISTS `current_student`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `current_student` (
  `student_id` varchar(45) NOT NULL,
  `student_name` varchar(45) DEFAULT NULL,
  `course_id` varchar(45) NOT NULL,
  PRIMARY KEY (`student_id`,`course_id`),
  KEY `current_std_course_idx` (`course_id`),
  CONSTRAINT `current_std_course` FOREIGN KEY (`course_id`) REFERENCES `course` (`course_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `models_performance`
--

DROP TABLE IF EXISTS `models_performance`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `models_performance` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `course_id` varchar(45) DEFAULT NULL,
  `Features` int(11) DEFAULT NULL,
  `ML_Algorithm` varchar(45) DEFAULT NULL,
  `Binary_Multiclass` varchar(45) DEFAULT NULL,
  `accuracy` float DEFAULT NULL,
  `f1` float DEFAULT NULL,
  `recall` float DEFAULT NULL,
  `precision_1` float DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_course_and_models_idx` (`course_id`),
  CONSTRAINT `fk_course_and_models` FOREIGN KEY (`course_id`) REFERENCES `course_and_models` (`course_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=4755 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `std_intervention_table`
--

DROP TABLE IF EXISTS `std_intervention_table`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `std_intervention_table` (
  `student_id` varchar(45) NOT NULL,
  `student_name` varchar(45) DEFAULT NULL,
  `course_id` varchar(45) NOT NULL,
  `assessment_name` varchar(45) NOT NULL,
  `intervention_message` longtext,
  PRIMARY KEY (`student_id`,`assessment_name`,`course_id`),
  KEY `std_intervention_table_to_student_grade_course_id_idx` (`course_id`),
  KEY `std_intervention_table_to_student_grade_assessment_name_idx` (`assessment_name`),
  CONSTRAINT `std_intervention_table_to_student_grade_std_id` FOREIGN KEY (`student_id`) REFERENCES `student_grade` (`student_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `student`
--

DROP TABLE IF EXISTS `student`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `student` (
  `student_id` int(11) NOT NULL AUTO_INCREMENT,
  `course_course_id` varchar(45) DEFAULT NULL,
  `total` int(11) DEFAULT NULL,
  `grade` varchar(45) DEFAULT NULL,
  `pass_or_fail` int(11) DEFAULT NULL,
  `multiclass_levels` varchar(45) DEFAULT NULL,
  `year` varchar(45) DEFAULT NULL,
  `semester_or_trimester` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`student_id`),
  KEY `fk_course_course_id_idx` (`course_course_id`),
  CONSTRAINT `fk_course_course_id` FOREIGN KEY (`course_course_id`) REFERENCES `course` (`course_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=46875 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `student_grade`
--

DROP TABLE IF EXISTS `student_grade`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `student_grade` (
  `student_id` varchar(45) NOT NULL,
  `assessment_name` varchar(45) NOT NULL,
  `course_id` varchar(45) NOT NULL,
  `mark` float DEFAULT NULL,
  `unconverted_mark` float DEFAULT NULL,
  `lost_mark` float DEFAULT NULL,
  PRIMARY KEY (`student_id`,`assessment_name`,`course_id`),
  KEY `std_id_current_std_idx` (`student_id`),
  KEY `std_grade_course_idx` (`course_id`),
  CONSTRAINT `std_grade_course` FOREIGN KEY (`course_id`) REFERENCES `course` (`course_id`),
  CONSTRAINT `std_grade_current_std` FOREIGN KEY (`student_id`) REFERENCES `current_student` (`student_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `student_prediction_results`
--

DROP TABLE IF EXISTS `student_prediction_results`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `student_prediction_results` (
  `student_id` varchar(45) NOT NULL,
  `course_id` varchar(45) NOT NULL,
  `assessment_name` varchar(45) NOT NULL,
  `Binary_prediction_results` varchar(45) DEFAULT NULL,
  `Multiclass_prediction_results` varchar(45) DEFAULT NULL,
  `number_of_assessment_in_prediction` int(11) DEFAULT NULL,
  PRIMARY KEY (`student_id`,`course_id`,`assessment_name`),
  KEY `course_id_course_idx` (`course_id`),
  CONSTRAINT `course_id_course` FOREIGN KEY (`course_id`) REFERENCES `course` (`course_id`) ON DELETE CASCADE,
  CONSTRAINT `std_prediction_result_current_std` FOREIGN KEY (`student_id`) REFERENCES `current_student` (`student_id`) ON DELETE CASCADE ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tla`
--

DROP TABLE IF EXISTS `tla`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tla` (
  `tla_id` int(11) NOT NULL AUTO_INCREMENT,
  `course_course_id` varchar(45) NOT NULL,
  `lecture_or_lab` varchar(45) NOT NULL,
  `lecture_lab_number` varchar(45) NOT NULL,
  `tla_topic` varchar(250) NOT NULL,
  `parent_tla` varchar(100) DEFAULT NULL,
  `userName` varchar(45) DEFAULT NULL,
  `tla_Resources` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`tla_id`),
  UNIQUE KEY `auto_increment_UNIQUE` (`tla_id`),
  KEY `fk_course_clo_idx` (`course_course_id`),
  CONSTRAINT `fk_course_tla` FOREIGN KEY (`course_course_id`) REFERENCES `course` (`course_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=317 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `users` (
  `userName` varchar(45) NOT NULL,
  `password` varchar(45) NOT NULL,
  `teacher_or_std` varchar(45) NOT NULL,
  PRIMARY KEY (`userName`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2022-12-10  6:46:09
