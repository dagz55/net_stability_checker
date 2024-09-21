# net_stability_checker
Validates network stability and more...


# Network Stability Test Script

This Python script is designed to test network stability in a domain environment. It performs various tests including DNS resolution, ping, port checks, and latency measurements for a specified domain and its domain controllers.

## Features

- DNS Resolution Tests
- Ping Tests
- Port Checks (for ports 53, 88, 389, 445, 636)
- Latency Tests
- Comprehensive summary of test results

## Requirements

- Python 3.6 or higher
- Root/sudo privileges (for certain tests like ping)

## Usage

1. Clone this repository or download the script.

2. Make the script executable:
   ```
   chmod +x network_stability_test.py
   ```

3. Run the script with sudo privileges:
   ```
   sudo python3 network_stability_test.py -d your_domain.com -dc dc1.your_domain.com dc2.your_domain.com
   ```

   Replace `your_domain.com` with your actual domain, and `dc1.your_domain.com dc2.your_domain.com` with your actual domain controllers.

### Command-line Arguments

- `-d`, `--domain`: Specify the domain to test (required)
- `-dc`, `--domain-controllers`: List of Domain Controllers to test (optional)

## Output

The script provides detailed output for each test performed and ends with a summary of all tests, including success rates for each test category.

## Logging

The script logs its activities to the console. You can modify the logging configuration in the script to log to a file if needed.

## Error Handling

The script includes error handling for common issues that may occur during network tests. Failed tests are logged and included in the final summary.

## Contributing

Contributions to improve the script are welcome. Please feel free to submit a Pull Request or open an Issue.

## License

This project is open source and available under the [MIT License](LICENSE).
