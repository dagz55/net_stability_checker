#!/usr/bin/env python3

import argparse
import subprocess
import socket
import time
import statistics
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_command(command):
    try:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        stdout, stderr = process.communicate()
        if process.returncode != 0:
            logging.error(f"Command failed: {' '.join(command)}")
            logging.error(f"Error output: {stderr}")
            return f"Error: {stderr}"
        return stdout
    except Exception as e:
        logging.exception(f"Exception occurred while running command: {' '.join(command)}")
        return f"Error: {str(e)}"

def ping_test(host, count=5):
    logging.info(f"Pinging {host}...")
    command = ["ping", "-c", str(count), "-W", "2", host]
    output = run_command(command)
    if "Error" in output:
        logging.warning(f"Ping to {host} failed: {output}")
        return f"Ping to {host} failed: {output}", False
    
    lines = output.splitlines()
    for line in lines:
        if "packets transmitted" in line:
            logging.info(f"Ping results for {host}: {line}")
            return f"Ping results for {host}: {line}", "0% packet loss" in line
    
    logging.warning(f"Unexpected ping output for {host}")
    return f"Unexpected ping output for {host}", False

def dns_resolution_test(domain):
    logging.info(f"Resolving DNS for {domain}...")
    try:
        ip_addresses = socket.gethostbyname_ex(domain)[2]
        result = f"DNS resolution for {domain}: {', '.join(ip_addresses)}"
        logging.info(result)
        return result, True
    except socket.gaierror as e:
        result = f"DNS resolution failed for {domain}: {str(e)}"
        logging.warning(result)
        return result, False

def port_check(host, port):
    logging.info(f"Checking port {port} on {host}...")
    try:
        with socket.create_connection((host, port), timeout=5):
            result = f"Port {port} is open on {host}"
            logging.info(result)
            return result, True
    except (socket.timeout, ConnectionRefusedError):
        result = f"Port {port} is closed on {host}"
        logging.warning(result)
        return result, False
    except Exception as e:
        result = f"Error checking port {port} on {host}: {str(e)}"
        logging.error(result)
        return result, False

def latency_test(host, count=10):
    logging.info(f"Testing latency to {host}...")
    latencies = []
    for _ in range(count):
        start_time = time.time()
        try:
            socket.create_connection((host, 445), timeout=2)
            latency = (time.time() - start_time) * 1000  # Convert to milliseconds
            latencies.append(latency)
        except Exception:
            latencies.append(None)
        time.sleep(0.5)  # Wait half a second between tests
    
    valid_latencies = [l for l in latencies if l is not None]
    if valid_latencies:
        avg_latency = statistics.mean(valid_latencies)
        min_latency = min(valid_latencies)
        max_latency = max(valid_latencies)
        result = f"Latency to {host}: Avg={avg_latency:.2f}ms, Min={min_latency:.2f}ms, Max={max_latency:.2f}ms"
        logging.info(result)
        return result, True
    else:
        result = f"All latency tests to {host} failed"
        logging.warning(result)
        return result, False

def main():
    parser = argparse.ArgumentParser(description="Network Stability Test for Domain Environment")
    parser.add_argument("-d", "--domain", required=True, help="Domain to test")
    parser.add_argument("-dc", "--domain-controllers", nargs='+', help="List of Domain Controllers to test")
    args = parser.parse_args()

    domain = args.domain
    dcs = args.domain_controllers or []

    print(f"Starting network stability tests for domain: {domain}")
    print("=" * 50)

    summary = {
        "dns_resolution": {"success": 0, "fail": 0},
        "ping": {"success": 0, "fail": 0},
        "port_checks": {"success": 0, "fail": 0},
        "latency": {"success": 0, "fail": 0}
    }

    # DNS tests
    print("\nDNS Resolution Tests:")
    result, success = dns_resolution_test(domain)
    print(result)
    summary["dns_resolution"]["success" if success else "fail"] += 1
    for dc in dcs:
        result, success = dns_resolution_test(dc)
        print(result)
        summary["dns_resolution"]["success" if success else "fail"] += 1

    # Ping tests
    print("\nPing Tests:")
    result, success = ping_test(domain)
    print(result)
    summary["ping"]["success" if success else "fail"] += 1
    for dc in dcs:
        result, success = ping_test(dc)
        print(result)
        summary["ping"]["success" if success else "fail"] += 1

    # Port checks
    ports_to_check = [53, 88, 389, 445, 636]
    print("\nPort Checks:")
    for dc in dcs:
        for port in ports_to_check:
            result, success = port_check(dc, port)
            print(result)
            summary["port_checks"]["success" if success else "fail"] += 1

    # Latency tests
    print("\nLatency Tests:")
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_host = {executor.submit(latency_test, host): host for host in [domain] + dcs}
        for future in as_completed(future_to_host):
            host = future_to_host[future]
            try:
                result, success = future.result()
                print(result)
                summary["latency"]["success" if success else "fail"] += 1
            except Exception as exc:
                print(f"{host} generated an exception: {exc}")
                summary["latency"]["fail"] += 1

    print("\nTest Summary:")
    print("=" * 50)
    for test, results in summary.items():
        print(f"{test.replace('_', ' ').title()}:")
        print(f"  Successful: {results['success']}")
        print(f"  Failed: {results['fail']}")
        print(f"  Success Rate: {results['success'] / (results['success'] + results['fail']) * 100:.2f}%")
        print()

    print("Network stability tests completed.")

if __name__ == "__main__":
    main()
