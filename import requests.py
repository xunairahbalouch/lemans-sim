import requests
import concurrent.futures
import time
import csv

# --- CONFIGURATION ---
TARGET_URL = "https://www.nike.com/launch"  # The target
MAX_THREADS = 50  # How many bots at once (don't go too high)
TIMEOUT = 5 # Seconds to wait before giving up

# Results storage
results = []

def test_proxy(proxy_url, proxy_type):
    try:
        proxies = {
            "http": f"http://{proxy_url}",
            "https": f"http://{proxy_url}",
        }
        # We pretend to be a real browser (User Agent)
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        
        start = time.time()
        # HEAD request saves bandwidth!
        response = requests.head(TARGET_URL, proxies=proxies, headers=headers, timeout=TIMEOUT)
        latency = round((time.time() - start) * 1000)
        
        status = response.status_code
        print(f"[{proxy_type}] Status: {status} | Latency: {latency}ms")
        
        return {
            "type": proxy_type,
            "status": status,
            "latency": latency,
            "success": 1 if status == 200 else 0
        }

    except Exception as e:
        print(f"[{proxy_type}] Failed: {str(e)}")
        return {
            "type": proxy_type,
            "status": "ERROR",
            "latency": 0,
            "success": 0
        }

# --- MAIN EXECUTION ---
def run_experiment(file_name, p_type):
    # Load proxies from file (format: user:pass@ip:port)
    with open(file_name, "r") as f:
        proxy_list = [line.strip() for line in f if line.strip()]

    # Run the test in parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        futures = [executor.submit(test_proxy, p, p_type) for p in proxy_list]
        for future in concurrent.futures.as_completed(futures):
            results.append(future.result())

# Create dummy files for testing if you don't have them yet
run_experiment("proxies_dc.txt", "Datacenter")
run_experiment("proxies_resi.txt", "Residential")

# Save to CSV for Excel
keys = results[0].keys()
with open('nike_experiment_data.csv', 'w', newline='') as output_file:
    dict_writer = csv.DictWriter(output_file, keys)
    dict_writer.writeheader()
    dict_writer.writerows(results)

print("Experiment Done. Data saved to nike_experiment_data.csv")
