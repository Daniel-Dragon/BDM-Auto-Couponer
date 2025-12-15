import os
import time
import requests
import json
import logging
import sys
from bs4 import BeautifulSoup


class BDMAutoCouponer:
    family_name: str
    region: str
    interval: int
    redeemed: dict
  
    def __init__(self):
        pass

    def init(self):
        print("Initializing BDM Auto Couponer...")
        config = self.load_config()
        self.family_name = config.get("family_name")
        self.region = config.get("region")
        if (not self.family_name):
            logging.error("Family name not set in configuration.")
            exit(1)
        if (not self.region):
            logging.error("Region not set in configuration.")
            exit(1)
        self.interval = config.get("interval", 86400)
        print(f"Family Name: {self.family_name}, Region: {self.region}")
        self.redeemed = self.load_redeemed()
        

    def load_config(self):
        config_path = os.path.join(os.path.dirname(__file__), "config", "config.json")
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"Failed to load configuration: {e}")
            exit(1)

    def load_redeemed(self):
        redeemed_path = os.path.join(os.path.dirname(__file__), "cache", "redeemed.json")
        try:
            with open(redeemed_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            return {}
    
    def save_redeemed(self):
        redeemed_path = os.path.join(os.path.dirname(__file__), "cache", "redeemed.json")
        try:
            with open(redeemed_path, "w", encoding="utf-8") as f:
                json.dump(self.redeemed, f, indent=4)
        except Exception as e:
            logging.error(f"Failed to save redeemed coupons: {e}")

    def mark_redeemed(self, coupon_code):
        self.redeemed[coupon_code] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        self.save_redeemed()

    def get_available_coupons(self):
        """
        Scrapes https://bdm.tools/coupons for all actively available coupon codes.
        Returns a list of coupon code strings.
        """
        url = "https://bdm.tools/coupons"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            coupons = []
            # Find the coupon table
            table = soup.find("table", class_="table-dark")
            if not table:
                logging.error("Coupon table not found on the page.")
                return []
            for tr in table.find("tbody").find_all("tr"):
                # Skip rows that are ads or have no <td>
                tds = tr.find_all("td")
                if not tds or len(tds) < 1:
                    continue
                # Skip expired coupons (they have multiple <b> tags in the first <td>)
                # and skip ads (they have no <b> tags)
                bolds = tds[0].find_all("b")
                if not len(bolds) == 1:
                    continue
                # Append this coupon
                coupons.append(bolds[0].get_text(strip=True))
            return coupons
        except Exception as e:
            logging.error(f"Failed to scrape coupons: {e}")
            return []
    
    def submit_coupon(self, coupon_code):
        """
        Submits a coupon code to the BDM coupon redemption endpoint.
        Returns the response JSON or None if failed.
        """
        url = "https://game.world.blackdesertm.com/Coupon/ApplyCouponInWeb?"
        data = {
            "userNickname": self.family_name,
            "region": self.region,
            "couponCode": coupon_code
        }
        try:
            response = requests.post(url, data=data, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logging.error(f"Failed to submit coupon '{coupon_code}': {e}")
            return None

    def run(self):
        # Main logic for the BDM Auto Couponer
        print("Running BDM Auto Couponer...")
        self.init()
        
        while True:
            
            available_coupons = self.get_available_coupons()
            for coupon in available_coupons:
                if coupon in self.redeemed:
                    print(f"Coupon '{coupon}' already redeemed on {self.redeemed[coupon]}. Skipping.")
                    continue
                print(f"Submitting coupon '{coupon}'...")
                result = self.submit_coupon(coupon)
                if result:
                    if result.get("resultCode") == 0:
                        print(f"Coupon '{coupon}' redeemed successfully!")
                        self.mark_redeemed(coupon)
                    elif result.get("resultCode") == -20007:
                        print(f"Coupon '{coupon}' has already been used.")
                        self.mark_redeemed(coupon)
                    elif result.get("resultCode") == -20006:
                        print(f"Coupon '{coupon}' is expired.")
                        self.mark_redeemed(coupon)
                    else:
                        error_msg = result.get("resultMsg", "Unknown error")
                        print(f"Failed to redeem coupon '{coupon}': {error_msg}")
                else:
                    print(f"Failed to redeem coupon '{coupon}': No response from server.")
            print(f"Waiting for {self.interval} seconds before next check...")
            time.sleep(self.interval)


if __name__ == "__main__":
    # Flush stdout to ensure docker logs appear immediately
    sys.stdout.reconfigure(line_buffering=True)
    couponer = BDMAutoCouponer()
    couponer.run()
