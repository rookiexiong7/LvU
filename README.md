# HIT软件工程大项目：LvU-驴友辅助系统

实现一个驴友辅助系统，可以按照以下功能模块和部分进行设计和开发：

>  题目描述：功能实现驴友注册，注册后可以自行发布组队邀请，设置目的度和组队人数，并能设置队伍管理员。也可以参加其他驴友组队。队伍管理员收到组队申请后可以对驴友审核，审核通过后驴友就自动加入队伍中，队伍达到人数限制自动关闭。

目前在我们的平台上，已经完成完整的团队管理功能，包括账号注册、登录、首页展示、用户资料修改、账号密码修改、队伍管理、队伍信息查看、创建队伍、加入队伍、申请审核、邀请推荐等一系列功能并**部署到服务器**上。

## 功能清单

- **用户注册与登录**
  - **注册账号**：提供用户注册页面，支持邮箱和自定义用户名注册。
  - **登录账号**：提供用户登录页面，支持邮箱和用户名登录。

- **创建队伍**
  - **创建队伍**：用户可以创建队伍并设置队伍名称、目的地、总人数等信息。

- **队伍搜索、推荐与加入**

  - **队伍搜索**：用户可以根据景点、时间和预算等条件搜索队伍。

  - **队伍推荐**：系统根据用户兴趣和需求推荐合适的队伍。

  - **加入队伍**：用户可以申请加入队伍并查看申请状态。

- **审核入队**
  - **审核入队申请**：管理员可以查看并批准或拒绝驴友的入队申请。

- **退出队伍**
  - **退出队伍**：用户可以选择退出当前所在的队伍。

- **队伍管理**

  - **修改队伍信息**：管理员可以更改队伍的出发时间、人数和目的地等信息。

  - **移除队伍成员**：管理员可以移除不合适的队伍成员。

  - **移交管理员权限**：管理员可以将管理权限移交给其他队员。

- **组队邀请发送与接收**

  - **发送组队邀请**：用户可以向其他驴友发送组队邀请。

  - **接收组队邀请**：用户可以接收并管理来自其他驴友的组队邀请。

- **景点推荐**

  - **景点推荐**：系统根据队伍特点和用户喜好推荐旅游景点。

- **用户管理**

  - **修改用户信息**：用户可以修改密码、年龄、性别和爱好等个人信息。

  - **展示用户信息**：系统展示用户的个人信息以供查看。

- **通知与提醒**

  - **通知管理**：用户可以收到组队申请的相关通知。

  - **队伍变动通知**：系统通知用户队伍信息的变动。

  - **重要消息提醒**：用户可以收到系统的重要消息提醒。

- **流量统计**

  - **队伍数据统计**：用户可以查看队伍的相关数据统计信息。

## 系统开发技术

- **编程语言：****Python****，****HTML****，****JavaScript**

- **开发环境：**

  - 轻量级 Web 框架 **Flask**

  - 数据库交互 **SQLAlchemy**

  - HTML模板引擎 **Jinja2**

- **运行环境：**

  - **Flask** 本地开发服务器

  - **MySQL** 数据库
  - **阿里云**服务器

- **主要技术：**

  - 前端页面与后端服务器的数据交互 **Ajax**(JavaScript)

  - 前端 UI 框架 **Layui**

  - 简化DOM 操作和事件处理 **jQuery**(JavaScript)

  - 样式设计和页面布局的层叠样式表 **CSS**

## 运行

通过`requirements_conda.txt`或者`requirements_pip.txt`配置python环境，运行`lvu.sql`初始化后端数据库，最后运行`app.py`即可执行本系统~



注意：当前主分支为本地运行版，部署至阿里云服务器上的版本略有区别（主要是SQL的登录），详见`LvU_Aliyun`分支

