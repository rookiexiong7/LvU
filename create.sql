DROP SCHEMA IF EXISTS LvU;
CREATE SCHEMA LvU;
USE LvU;


CREATE TABLE `team`  (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '主键',
  `destination` varchar(150) NOT NULL COMMENT '目的地',
  `max_members` int NULL DEFAULT 0 COMMENT '组队人数',
  `current_members` int NOT NULL DEFAULT 0 COMMENT '当前组队人数',
  `public_id` int NOT NULL COMMENT '发起人id（关联user表的id）',
  `admin_id` int NULL DEFAULT 1 COMMENT '管理员id（关联user表的id）',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB ;

INSERT INTO `team` VALUES (1, '北京', 5, 1, 1,1);
INSERT INTO `team` VALUES (2, '南京', 4, 1, 1,2);
INSERT INTO `team` VALUES (3, '重庆', 7, 1, 1,3);

CREATE TABLE `user`  (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '主键',
  `username` varchar(150) NOT NULL COMMENT '用户名',
  `password` varchar(150) NOT NULL COMMENT '密码',
  `id_code` varchar(100) DEFAULT NULL COMMENT '身份证号',
  `phone` varchar(100) DEFAULT NULL COMMENT '手机号',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `username`(`username` ASC) USING BTREE
) ENGINE = InnoDB ;


INSERT INTO `user` VALUES (1, 'user1', '123456', '111111111111111111', '17612341234');
INSERT INTO `user` VALUES (2, 'user2', '123456', '111111111111111112', '17612341235');
INSERT INTO `user` VALUES (3, 'user3', '123456', '111111111111111113', '17612341236');
INSERT INTO `user` VALUES (4, 'user4', '123456', '111111111111111114', '17612341237');
INSERT INTO `user` VALUES (5, 'user5', '123456', '111111111111111115', '17612341238');

CREATE TABLE `user_team`  (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '主键',
  `team_id` int NOT NULL COMMENT '组队id（关联team表的id）',
  `join_user_id` int NOT NULL COMMENT '参与者id（关联user表的id）',
  `audit_stutus` int NOT NULL DEFAULT 0 COMMENT '审核状态：0待审核 1审核通过 2审核不通过',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB ;


INSERT INTO `user_team` VALUES (1, 1, 2, 0);
INSERT INTO `user_team` VALUES (2, 1, 3, 1);
INSERT INTO `user_team` VALUES (3, 1, 4, 2);
INSERT INTO `user_team` VALUES (4, 2, 2, 1);
INSERT INTO `user_team` VALUES (5, 2, 3, 2);