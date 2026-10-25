# BaiduNetdisk Clean UI Remove Ads
去广告脚本与指定提示窗口隐藏脚本的合集，适用Windows。仅提供脚本，不附带网盘程序或修改后的文件。

ai写的，在8.9.7.101版本测试运行，其他版本未知。

## 包含什么

- **去广告脚本**：修改本地 `core.asar` 中的部分广告数据写入与界面显示，关闭已确认的自动更新配置，并重命名独立更新程序。
- **提示隐藏脚本**：只匹配 `BaiduNetdiskUnite.exe` 的标准对话框，且正文包含“应用程序被修改”和“请重新安装”，请求隐藏它。不会点击确定、关闭窗口或终止进程。
- **恢复入口**：分别撤销文件补丁、重新显示提示。

本合集不包含修改 DLL 或跳过原生校验分支的实验补丁。去广告转换函数保持第一版不变；仅调整默认路径配置并新增通用启动入口。

## 适用范围

- Windows 桌面环境，Windows PowerShell 5.1。
- 去广告脚本需要 Python **3.11 或更高版本**，能通过 `python` 命令启动，无第三方 Python 依赖。
- 仅匹配当时分析的 **8.9.7.101** 资源；版本号相同也可能有不同文件，实际按以下 `core.asar` SHA-256 校验：

```text
280214b601b9dd28b932879c931d7bc9735bfd39b231e99412327aa3ea8c71c2
```

不匹配时脚本会拒绝修改。请勿删除版本校验。

## 使用顺序

1. 下载并解压本项目，等待传输结束，从托盘彻底退出网盘。
2. 双击 `Apply.cmd`，按提示输入网盘安装目录；包含 `BaiduNetdisk.exe` 的文件夹即安装目录。默认路径'C:\Program Files\BaiduNetdisk'，不匹配可在clean_netdisk.py里修改路径。
3. 也可复制 `install-path.example.txt` 为 `install-path.local.txt`，将其中的一行改为实际目录，之后无需重复输入。该本地文件被 Git 忽略。
4. 脚本输出写入项目根目录的 `last-run.log`。看到成功后启动网盘，再检查界面和上传下载。
5. 如果只出现“应用程序被修改，请重新安装”，而其他功能仍可使用，可先关闭第三方弹窗拦截器中会处理该提示的规则，再运行 `Start-Hide.cmd`。保持其控制台运行，可以最小化。

隐藏脚本只改变显示状态，提示调用仍然处于等待状态。如果它阻塞了主界面，隐藏不会解除阻塞；如果程序自行退出，隐藏不能阻止。不要对整个 `BaiduNetdiskUnite.exe` 使用可能关闭窗口或终止进程的拦截规则。

如果网盘运行在管理员权限下，脚本可能需要相同权限。

## 恢复与停止

- **撤销去广告**：退出网盘，运行 `Restore.cmd`，使用与应用时相同的安装路径。
- **停止隐藏**：在隐藏脚本控制台按 Ctrl+C；脚本会尝试重新显示本次隐藏的提示。
- **重新显示提示**：确认隐藏脚本已停止后，运行 `Restore-Notice.cmd`。如果直接关闭了隐藏脚本窗口，也可使用此入口恢复显示。

备份在安装目录的 `LocalCleanBackup-v1`。请保留。遇到“Backup folder already exists”时，先核对是否已应用、是否需要恢复，不要直接删除备份或反复覆盖。若已确认恢复完成，可以把旧备份移到其他位置保存，再重新应用。

## 命令行

```powershell
python scripts/clean_netdisk.py apply --path "C:\Program Files\BaiduNetdisk"
python scripts/clean_netdisk.py restore --path "C:\Program Files\BaiduNetdisk"
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/Hide-Notice.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/Hide-Notice.ps1 -Restore
```

直接运行 Python 时也支持 `BAIDUNETDISK_PATH` 环境变量，默认路径为 `C:\Program Files\BaiduNetdisk`。

## 修改范围与已知限制

去广告脚本针对顶部/侧栏推广、游戏入口、企业创建推广、头像菜单推广及部分会员促销/签约弹层。它不修改会员权益、云端文件或下载速度设置，不保证去除所有广告或阻断所有推广请求。

去除更新。设置 `AutoUpdate/config.ini` 中的 `IsAutoUpdate=0`，并将 `AutoUpdate/Autoupdate.exe` 改名为 `Autoupdate.exe.localclean-disabled`。其他更新渠道未被证明全部关闭。

客户端可能检测资源修改并提示或退出。该合集只提供可逆的资源修改和窗口隐藏，不保证规避所有检测。出现闪退、界面异常、无法上传下载时应恢复；不要把兼容模式提示当作已查明的崩溃原因。

<img width="1800" height="1200" alt="PixPin_2026-10-25_09-45-57" src="https://github.com/user-attachments/assets/44a22006-192a-4e7f-97c6-f1bbb865fec1" />



## 验证状态

已验证该版本资源转换函数未发生变化、修改后 JS 的语法及 ASAR 回读、工作副本上的应用/恢复哈希一致。隐藏脚本已通过 Windows PowerShell 下 C# API 辅助类编译检查。

尚未证明本合集在真实登录账号中长期稳定，隐藏脚本也未完成真实提示窗口的效果验证。此前其他 DLL 实验补丁的短时副本测试不代表本合集已通过完整客户端测试。


## Windows API 参考

- [ShowWindow / 窗口显示状态](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-showwindow)
- [MessageBoxW / 模态提示](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-messageboxw)
