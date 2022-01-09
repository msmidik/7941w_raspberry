# 7941W RFID reader/writer for Raspberry Pi

Simle Python tool for cheap RFID reader and writer (Gwiot 7941W) on Raspberry Pi. See [7941W documentation](documentation.md)

# Connection
* via UART, module's RX goes to Raspberry's TX pin (GPIO 14) and module's TX goes to Raspberry's RX pin (GPIO 15)
* because Raspberry UART pins need 3.3 V but the module is 5 V, level converter is used

![connection](https://github.com/smidik/rfid-7941w/blob/main/docs/connection.jpg?raw=true)