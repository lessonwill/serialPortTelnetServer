# Serial Port Telnet Server

## Overview

This Serial Port Telnet Server program is designed to bridge serial port communication to a Telnet server. It allows users to interact with devices connected via serial ports through a Telnet client. The program is developed using Python and leverages libraries like `asyncio` and `serial_asyncio` for asynchronous I/O, as well as Tkinter for the graphical user interface.

## Features

- **Supports multiple Telnet clients connecting to the same serial port. Operations from each client can be seen on all other clients.**
- **Easy-to-use GUI for configuration**
- **Support for dynamic selection of COM ports**
- **Configurable baud rate and Telnet port**
- **Built-in logging of Telnet connections**
- **Supports Windows/Linux. Tested on Win10/Beagle Board Black (Debian buster).**

## Prerequisites

- Python 3.x
- Tkinter
- asyncio
- serial_asyncio
- psutil

## Installation

Clone the repository:

```bash
git clone https://github.com/yourusername/SerialPortTelnetServer.git
```

Install required packages:

```bash
pip install -r requirements.txt
```

## Usage

1. **Launch the program** by running `serialServerCmd.py`:
    
    GUI mode:
    ```bash
    python3 serialServerCmd.py
    ```
    CMD mode:
    ```bash
    python3 serialServerCmd.py --cli --com /dev/ttyUSB0 --baud 9600 --port 9001
    ```
    The following steps only apply to GUI mode.

3. The GUI will appear, allowing you to **select the COM port**, **set the baud rate**, and **specify the Telnet port**.

4. **Click the "Connect" button** to start the Telnet server. The button will change to "Disconnect", indicating that the server is running.

5. **Connect to the server** using a Telnet client. The IP address will be displayed in the GUI.

6. **Click "Disconnect"** to stop the server.

## Contributing

Feel free to submit pull requests or report issues.

## License

This project is licensed under the MIT License.

## Acknowledgments

- The asyncio library for asynchronous I/O.
- The serial_asyncio library for serial port communication.

# 串口Telnet服务器

## 概述

本串口Telnet服务器程序旨在将串口通信桥接到Telnet服务器。它允许用户通过Telnet客户端与通过串口连接的设备进行交互。该程序使用Python开发，利用了`asyncio`和`serial_asyncio`库进行异步I/O，以及使用Tkinter进行图形用户界面设计。

## 功能

- **支持多个Telnet客户端连接到同一个串口。每个客户端的操作，在其他客户端上都可以看到**
- **易于使用的图形用户界面进行配置**
- **支持动态选择COM端口**
- **可配置的波特率和Telnet端口**
- **内置的Telnet连接日志记录**
- **支持Windows/Linux。 在WIN10和Beagle Board Black (Debian buster)上测试成功。**


## 前提条件

- Python 3.x
- Tkinter
- asyncio
- serial_asyncio
- psutil

## 安装

克隆仓库：

```bash
git clone https://github.com/yourusername/SerialPortTelnetServer.git
```

安装所需的包：

```bash
pip install -r requirements.txt
```

## 使用说明

1. **运行`serialServerCmd.py`以启动程序**：
  
    GUI 模式:
    ```bash
    python3 serialServerCmd.py
    ```
    命令行模式:
    ```bash
    python3 serialServerCmd.py --cli --com /dev/ttyUSB0 --baud 9600 --port 9001
    ```
    下面的步骤仅对GUI模式适用。
2. 图形界面将出现，允许您**选择COM端口**，**设置波特率**，以及**指定Telnet端口**。

3. **点击“连接”按钮**以启动Telnet服务器。按钮将变为“断开”，表示服务器正在运行。

4. **使用Telnet客户端连接到服务器**。IP地址将在图形界面中显示。

5. **点击“断开”以停止服务器**。

## 如何贡献

欢迎提交拉取请求或报告问题。

## 许可证

该项目采用MIT许可证。

## 致谢

- `asyncio`库用于异步I/O。
- `serial_asyncio`库用于串口通信。
