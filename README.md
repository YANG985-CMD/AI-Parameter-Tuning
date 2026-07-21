# AI Parameter Tuning

面向嵌入式控制器的串口遥测与安全 AI 调参 Skill，提炼自 STM32H743 + FreeRTOS 实物工程。

## Skill

### `embedded-serial-vofa-ai-tuning`

- 用 VOFA+ JustFloat 实时显示角度、压力、PWM 等曲线。
- 用版本化遥测帧、串口命令和实验指标支持 AI 调参。
- 内置命令白名单、参数范围、故障停机、掉线保护和回退流程。
- 支持 STM32 HAL、UART DMA、FreeRTOS，以及 STM32H7 D-Cache 注意事项。
- 附带可复用的 Python 帧解析器、受限命令生成器和离线测试。

这个 Skill 不会默认控制实物，也不会允许 AI 直接发送任意 PWM/压力命令。实物调参必须由用户明确授权，并由固件独立执行安全限制。

## 使用

将 [`skills/embedded-serial-vofa-ai-tuning`](skills/embedded-serial-vofa-ai-tuning) 安装到 Codex Skills 目录，然后提出例如：

```text
使用 $embedded-serial-vofa-ai-tuning 给我的 STM32 控制器增加 VOFA+ 曲线遥测。
使用 $embedded-serial-vofa-ai-tuning 设计一个带参数边界和故障停机的 AI PID 调参流程。
```

运行离线测试：

```bash
python -m unittest discover -s tests -v
```

来源工程保持不变；仓库中保存的是通用化协议、工作流和工具，不是整套应用固件。
