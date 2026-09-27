# molanko-bot-commands

一组供聊天机器人宿主应用调用的命令模块。命令处理器使用平台无关的 `BotContext` 和 `UserInfo`，把命令逻辑与 Discord 等平台的交互对象隔开；宿主应用负责解析平台输入、实现上下文适配器并注册命令。
