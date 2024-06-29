DROP SCHEMA IF EXISTS LvU;
CREATE SCHEMA LvU;
USE LvU;

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for attractions
-- ----------------------------
DROP TABLE IF EXISTS `attractions`;
CREATE TABLE `attractions`  (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '主键',
  `城市` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `景点名称` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `攻略数量` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `评论数量` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `星级` float NULL DEFAULT NULL,
  `排名` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `简介` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `链接` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `图片` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of attractions
-- ----------------------------

-- ----------------------------
-- Table structure for invitation
-- ----------------------------
DROP TABLE IF EXISTS `invitation`;
CREATE TABLE `invitation`  (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '主键',
  `team_id` int NOT NULL COMMENT '队伍id（关联team表的id）',
  `inviter_id` int NOT NULL COMMENT '邀请人id（关联user表的id）',
  `invitee_id` int NOT NULL COMMENT '被邀请人id（关联user表的id）',
  `status` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT 'pending' COMMENT '邀请状态：pending, accepted, declined',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `fk_invitation_team`(`team_id` ASC) USING BTREE,
  INDEX `fk_invitation_inviter_user`(`inviter_id` ASC) USING BTREE,
  INDEX `fk_invitation_invitee_user`(`invitee_id` ASC) USING BTREE,
  CONSTRAINT `fk_invitation_invitee_user` FOREIGN KEY (`invitee_id`) REFERENCES `user` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `fk_invitation_inviter_user` FOREIGN KEY (`inviter_id`) REFERENCES `user` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `fk_invitation_team` FOREIGN KEY (`team_id`) REFERENCES `team` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 5 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of invitation
-- ----------------------------
INSERT INTO `invitation` VALUES (1, 4, 1, 6, 'accepted');
INSERT INTO `invitation` VALUES (2, 4, 1, 7, 'accepted');
INSERT INTO `invitation` VALUES (3, 5, 1, 4, 'pending');
INSERT INTO `invitation` VALUES (4, 5, 1, 5, 'accepted');

-- ----------------------------
-- Table structure for notification
-- ----------------------------
DROP TABLE IF EXISTS `notification`;
CREATE TABLE `notification`  (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '主键',
  `user_id` int NOT NULL COMMENT '用户id（关联user表的id）',
  `message` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '消息内容',
  `timestamp` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '时间戳',
  `is_read` tinyint(1) NOT NULL DEFAULT 0 COMMENT '是否已读',
  `link` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '链接',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `fk_notification_user`(`user_id` ASC) USING BTREE,
  CONSTRAINT `fk_notification_user` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 8 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of notification
-- ----------------------------
INSERT INTO `notification` VALUES (1, 6, '你收到来自 zwxx 的入队邀请。', '2024-06-28 13:53:55', 0, '/received_invitations');
INSERT INTO `notification` VALUES (2, 7, '你收到来自 zwxx 的入队邀请。', '2024-06-28 13:53:59', 0, '/received_invitations');
INSERT INTO `notification` VALUES (3, 4, '你收到来自 zwxx 的入队邀请。', '2024-06-28 13:55:17', 0, '/received_invitations');
INSERT INTO `notification` VALUES (4, 5, '你收到来自 zwxx 的入队邀请。', '2024-06-28 13:55:21', 0, '/received_invitations');
INSERT INTO `notification` VALUES (5, 1, '你的邀请被 user2 接受了。', '2024-06-28 13:55:56', 0, '/sent_invitations');
INSERT INTO `notification` VALUES (6, 1, '你的邀请被 user3 接受了。', '2024-06-28 13:56:17', 0, '/sent_invitations');
INSERT INTO `notification` VALUES (7, 1, '你的邀请被 user5 接受了。', '2024-06-28 13:56:49', 0, '/sent_invitations');

-- ----------------------------
-- Table structure for team
-- ----------------------------
DROP TABLE IF EXISTS `team`;
CREATE TABLE `team`  (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '主键',
  `destination` varchar(150) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '目的地',
  `departure_location` varchar(150) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '出发地点',
  `travel_mode` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '出行方式',
  `team_type` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '队伍类型',
  `travel_time` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '游玩时间',
  `travel_budget` int UNSIGNED NOT NULL COMMENT '旅游预算',
  `max_members` int NULL DEFAULT 0 COMMENT '最大组队人数',
  `current_members` int NOT NULL DEFAULT 0 COMMENT '当前组队人数',
  `public_id` int NOT NULL COMMENT '发起人id（关联user表的id）',
  `admin_id` int NULL DEFAULT 1 COMMENT '管理员id（关联user表的id）',
  `travel_plan` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL COMMENT '旅游计划',
  `popularity` int NOT NULL DEFAULT 0 COMMENT '队伍热度统计',
  `view_count` int NOT NULL DEFAULT 0 COMMENT '查看次数',
  `apply_count` int NOT NULL DEFAULT 0 COMMENT '入队申请次数',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `fk_team_public_user`(`public_id` ASC) USING BTREE,
  INDEX `fk_team_admin_user`(`admin_id` ASC) USING BTREE,
  CONSTRAINT `fk_team_admin_user` FOREIGN KEY (`admin_id`) REFERENCES `user` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `fk_team_public_user` FOREIGN KEY (`public_id`) REFERENCES `user` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 7 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of team
-- ----------------------------
INSERT INTO `team` VALUES (1, '北京', '上海', '飞机', '家庭游', '2024-06-10', 5000, 5, 2, 1, 1, '', 7, 0, 4);
INSERT INTO `team` VALUES (2, '南京', '广州', '私家车', '自驾游', '2024-06-15', 3000, 4, 2, 1, 2, '', 6, 0, 3);
INSERT INTO `team` VALUES (3, '厦门', '深圳', '大巴', '跟团游', '2024-06-20', 2000, 7, 2, 1, 3, '', 5, 0, 2);
INSERT INTO `team` VALUES (4, '大连', '哈尔滨', '火车', '跟团游', '2024-06-29', 4000, 5, 3, 1, 1, '', 5, 1, 0);
INSERT INTO `team` VALUES (5, '上海', '上虞', '私家车', '自驾游', '2024-6-30', 3000, 5, 2, 1, 1, '', 4, 1, 0);
INSERT INTO `team` VALUES (6, '衢州', '绍兴', '私家车', '家庭游', '2024-6-24', 5000, 5, 1, 3, 3, '', 2, 0, 0);

-- ----------------------------
-- Table structure for user
-- ----------------------------
DROP TABLE IF EXISTS `user`;
CREATE TABLE `user`  (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '主键',
  `username` varchar(150) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '用户名',
  `password` varchar(150) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '密码',
  `id_code` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '身份证号',
  `phone` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '手机号',
  `character` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '性格',
  `travel_hobby` varchar(150) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '旅游爱好',
  `residence` varchar(150) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '居住地',
  `gender` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '性别',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `username`(`username` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 10 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of user
-- ----------------------------
INSERT INTO `user` VALUES (1, 'zwxx', '123456', '111111111111111111', '17612341234', '外向', '登山', '北京', '男');
INSERT INTO `user` VALUES (2, 'hcyy', '123456', '111111111111111112', '17612341235', '内向', '阅读', '上海', '女');
INSERT INTO `user` VALUES (3, 'zzxx', '123456', '111111111111111113', '17612341236', '活泼', '摄影', '广州', '男');
INSERT INTO `user` VALUES (4, 'user4', '123456', '111111111111111114', '17612341237', '安静', '美食', '深圳', '女');
INSERT INTO `user` VALUES (5, 'user5', '123456', '111111111111111115', '17612341238', '冒险', '旅行', '重庆', '男');
INSERT INTO `user` VALUES (6, 'user2', '123456', NULL, NULL, NULL, NULL, NULL, NULL);
INSERT INTO `user` VALUES (7, 'user3', '123456', NULL, NULL, NULL, NULL, NULL, NULL);
INSERT INTO `user` VALUES (8, 'user6', '123456', NULL, NULL, NULL, NULL, NULL, NULL);
INSERT INTO `user` VALUES (9, 'user7', '123456', NULL, NULL, NULL, NULL, NULL, NULL);

-- ----------------------------
-- Table structure for user_team
-- ----------------------------
DROP TABLE IF EXISTS `user_team`;
CREATE TABLE `user_team`  (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '主键',
  `team_id` int NOT NULL COMMENT '组队id（关联team表的id）',
  `join_user_id` int NOT NULL COMMENT '参与者id（关联user表的id）',
  `audit_status` int NOT NULL DEFAULT 0 COMMENT '审核状态：0待审核 1审核通过 2审核不通过',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `fk_user_team_team`(`team_id` ASC) USING BTREE,
  INDEX `fk_user_team_user`(`join_user_id` ASC) USING BTREE,
  CONSTRAINT `fk_user_team_team` FOREIGN KEY (`team_id`) REFERENCES `team` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `fk_user_team_user` FOREIGN KEY (`join_user_id`) REFERENCES `user` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 16 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of user_team
-- ----------------------------
INSERT INTO `user_team` VALUES (1, 1, 1, 1);
INSERT INTO `user_team` VALUES (2, 1, 2, 0);
INSERT INTO `user_team` VALUES (3, 1, 3, 1);
INSERT INTO `user_team` VALUES (4, 1, 4, 2);
INSERT INTO `user_team` VALUES (5, 2, 2, 1);
INSERT INTO `user_team` VALUES (6, 2, 3, 2);
INSERT INTO `user_team` VALUES (7, 3, 3, 1);
INSERT INTO `user_team` VALUES (8, 2, 1, 1);
INSERT INTO `user_team` VALUES (9, 3, 1, 1);
INSERT INTO `user_team` VALUES (10, 4, 1, 1);
INSERT INTO `user_team` VALUES (11, 5, 1, 1);
INSERT INTO `user_team` VALUES (12, 4, 6, 1);
INSERT INTO `user_team` VALUES (13, 4, 7, 1);
INSERT INTO `user_team` VALUES (14, 5, 5, 1);
INSERT INTO `user_team` VALUES (15, 6, 3, 1);

SET FOREIGN_KEY_CHECKS = 1;
