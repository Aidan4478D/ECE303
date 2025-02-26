## ECE303 Programming Assignment #1

Welcome to the simple port scanner! To start scanning, enter in your terminal:
```console
python3 scanner.py [option1, option2, ..., optionN]
```
Where the following options are:
- `--ports <ports to scan>`
    - `<ports to scan>` must be of the form `[starting scan port - ending scan port]`
    - For example, if you wanted to scan ports 1-100, you would input `--ports [1-100]`
    - The default port range being scanned is `[1-1024]`

- `--ip <ip to scan>`
    - The ip of the ports to be scanned
    - The port scanner will scan `localhost` by default

- `--input <file name>`
    - Will read a list of IP addresses and port ranges specified in a file and perform the same scanning analysis for each set
    - The contents of the file must be of the form `<IP address> \t <port start> \t <port end>`

- `--output <file name>`
    - Specify a file to output content to
    - Default output is the console (stdout)

- `--help`
    - Display a help message summarizing the tool's usage

### Files
`scanner.py`
    - Argument handling and chooses where to take the input from (arguments or input file)
    - Includes entry point to port scanner (`main` function)

`PortScanner.py`
    - `PortScanner` class that includes port scanning logic and output
    - `print_help` function that prints the help message when the `--help` flag is specified
    - `input_from_file` function that handles and scans instructions from an external input file (as specified in the `--input` flag section). 

### Resources used:
- [https://docs.micropython.org/en/latest/library/socket.html](https://docs.micropython.org/en/latest/library/socket.html)
- [https://www.datacamp.com/tutorial/a-complete-guide-to-socket-programming-in-python](https://www.datacamp.com/tutorial/a-complete-guide-to-socket-programming-in-python)
- [https://stackoverflow.com/questions/44054463/how-to-return-the-socket-status-for-the-validating-the-port-scanning](https://stackoverflow.com/questions/44054463/how-to-return-the-socket-status-for-the-validating-the-port-scanning)

