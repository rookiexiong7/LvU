DROP SCHEMA IF EXISTS LvU;
CREATE SCHEMA LvU;
USE LvU;

-- 创建 team 表
CREATE TABLE `team`  (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '主键',
  `destination` varchar(150) NOT NULL COMMENT '目的地',
  `departure_location` varchar(150) NOT NULL COMMENT '出发地点',
  `travel_mode` varchar(100) COMMENT '出行方式',
  `team_type` varchar(100) COMMENT '队伍类型',
  `travel_time` varchar(100) NOT NULL COMMENT '游玩时间',
  `travel_budget` int UNSIGNED NOT NULL COMMENT '旅游预算',  -- 将字段类型改为非负整数
  `max_members` int NULL DEFAULT 0 COMMENT '组队人数',
  `current_members` int NOT NULL DEFAULT 0 COMMENT '当前组队人数',
  `public_id` int NOT NULL COMMENT '发起人id（关联user表的id）',
  `admin_id` int NULL DEFAULT 1 COMMENT '管理员id（关联user表的id）',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB;

-- 插入 team 表的示例数据
INSERT INTO `team` VALUES (1, '北京', '上海', '飞机', '家庭游', '2024-06-10', '5000', 5, 2, 1, 1);
INSERT INTO `team` VALUES (2, '南京', '广州', '私家车', '自驾游', '2024-06-15', '3000', 4, 1, 1, 2);
INSERT INTO `team` VALUES (3, '重庆', '深圳', '大巴', '跟团游', '2024-06-20', '2000', 7, 1, 1, 3);

-- 创建 user 表
CREATE TABLE `user`  (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '主键',
  `username` varchar(150) NOT NULL COMMENT '用户名',
  `password` varchar(150) NOT NULL COMMENT '密码',
  `id_code` varchar(100) DEFAULT NULL COMMENT '身份证号',
  `phone` varchar(100) DEFAULT NULL COMMENT '手机号',
  `character` varchar(100) DEFAULT NULL COMMENT '性格',
  `travel_hobby` varchar(150) DEFAULT NULL COMMENT '旅游爱好',
  `residence` varchar(150) DEFAULT NULL COMMENT '居住地',
  `gender` varchar(10) DEFAULT NULL COMMENT '性别',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `username`(`username` ASC) USING BTREE
) ENGINE = InnoDB;

-- 插入 user 表的示例数据
INSERT INTO `user` VALUES (1, 'zwxx', '123456', '111111111111111111', '17612341234', '外向', '登山', '北京', '男');
INSERT INTO `user` VALUES (2, 'hcyy', '123456', '111111111111111112', '17612341235', '内向', '阅读', '上海', '女');
INSERT INTO `user` VALUES (3, 'zzxx', '123456', '111111111111111113', '17612341236', '活泼', '摄影', '广州', '男');
INSERT INTO `user` VALUES (4, 'user4', '123456', '111111111111111114', '17612341237', '安静', '美食', '深圳', '女');
INSERT INTO `user` VALUES (5, 'user5', '123456', '111111111111111115', '17612341238', '冒险', '旅行', '重庆', '男');

-- 创建 user_team 表
CREATE TABLE `user_team`  (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '主键',
  `team_id` int NOT NULL COMMENT '组队id（关联team表的id）',
  `join_user_id` int NOT NULL COMMENT '参与者id（关联user表的id）',
  `audit_status` int NOT NULL DEFAULT 0 COMMENT '审核状态：0待审核 1审核通过 2审核不通过',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB;

-- 插入 user_team 表的示例数据
INSERT INTO `user_team` VALUES (1, 1, 1, 1);
INSERT INTO `user_team` VALUES (2, 1, 2, 0);
INSERT INTO `user_team` VALUES (3, 1, 3, 1);
INSERT INTO `user_team` VALUES (4, 1, 4, 2);
INSERT INTO `user_team` VALUES (5, 2, 2, 1);
INSERT INTO `user_team` VALUES (6, 2, 3, 2);
INSERT INTO `user_team` VALUES (7, 3, 3, 1);
