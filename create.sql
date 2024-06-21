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
  `max_members` int NULL DEFAULT 0 COMMENT '最大组队人数',
  `current_members` int NOT NULL DEFAULT 0 COMMENT '当前组队人数',
  `public_id` int NOT NULL COMMENT '发起人id（关联user表的id）',
  `admin_id` int NULL DEFAULT 1 COMMENT '管理员id（关联user表的id）',
  `travel_plan` text COMMENT '旅游计划',  -- 新增旅游计划景点字段
  `popularity` int NOT NULL DEFAULT 0 COMMENT '队伍热度统计', -- 新增热度统计字段
  `view_count` int NOT NULL DEFAULT 0 COMMENT '查看次数',
  `apply_count` int NOT NULL DEFAULT 0 COMMENT '入队申请次数',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB;

-- 插入 team 表的示例数据
INSERT INTO `team` VALUES (1, '北京', '上海', '飞机', '家庭游', '2024-06-10', '5000', 5, 2, 1, 1, '', 7, 0, 4);
INSERT INTO `team` VALUES (2, '南京', '广州', '私家车', '自驾游', '2024-06-15', '3000', 4, 2, 1, 2, '', 6, 0, 3);
INSERT INTO `team` VALUES (3, '厦门', '深圳', '大巴', '跟团游', '2024-06-20', '2000', 7, 2, 1, 3, '', 5, 0, 2);

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
INSERT INTO `user_team` VALUES (8, 2, 1, 1);
INSERT INTO `user_team` VALUES (9, 3, 1, 1);

-- 创建 attractions 表
CREATE TABLE attractions (
    `id` int NOT NULL AUTO_INCREMENT COMMENT '主键',
    `城市` VARCHAR(50),
    `景点名称` VARCHAR(100),
    `攻略数量` VARCHAR(50),
    `评论数量` VARCHAR(50),
    `星级` FLOAT,
    `排名` VARCHAR(50),
    `简介` TEXT,
    `链接` VARCHAR(255),
    `图片` VARCHAR(255),
     PRIMARY KEY (`id`) USING BTREE
);

-- 创建 Invitations 表
CREATE TABLE `invitation` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '主键',
  `team_id` int NOT NULL COMMENT '队伍id（关联team表的id）',
  `inviter_id` int NOT NULL COMMENT '邀请人id（关联user表的id）',
  `invitee_id` int NOT NULL COMMENT '被邀请人id（关联user表的id）',
  `status` varchar(50) NOT NULL DEFAULT 'pending' COMMENT '邀请状态：pending, accepted, declined',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB;

-- 创建 notification 表
CREATE TABLE `notification` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '主键',
  `user_id` int NOT NULL COMMENT '用户id（关联user表的id）',
  `message` varchar(500) NOT NULL COMMENT '消息内容',
  `timestamp` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '时间戳',
  `is_read` boolean NOT NULL DEFAULT FALSE COMMENT '是否已读',
  `link` varchar(200) DEFAULT NULL COMMENT '链接',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB;

-- 添加 team 表的外键约束
ALTER TABLE `team`
ADD CONSTRAINT `fk_team_public_user`
FOREIGN KEY (`public_id`) REFERENCES `user` (`id`),
ADD CONSTRAINT `fk_team_admin_user`
FOREIGN KEY (`admin_id`) REFERENCES `user` (`id`);

-- 添加 user_team 表的外键约束
ALTER TABLE `user_team`
ADD CONSTRAINT `fk_user_team_team`
FOREIGN KEY (`team_id`) REFERENCES `team` (`id`),
ADD CONSTRAINT `fk_user_team_user`
FOREIGN KEY (`join_user_id`) REFERENCES `user` (`id`);

-- 添加 invitation 表的外键约束
ALTER TABLE `invitation`
ADD CONSTRAINT `fk_invitation_team`
FOREIGN KEY (`team_id`) REFERENCES `team` (`id`),
ADD CONSTRAINT `fk_invitation_inviter_user`
FOREIGN KEY (`inviter_id`) REFERENCES `user` (`id`),
ADD CONSTRAINT `fk_invitation_invitee_user`
FOREIGN KEY (`invitee_id`) REFERENCES `user` (`id`);

-- 添加 notification 表的外键约束
ALTER TABLE `notification`
ADD CONSTRAINT `fk_notification_user`
FOREIGN KEY (`user_id`) REFERENCES `user` (`id`);
