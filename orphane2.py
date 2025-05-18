import requests
import concurrent.futures
import configparser
import os
import argparse
from progress.bar import IncrementalBar
from datetime import datetime
from time import sleep, time
import logging
from threading import Lock

class Orphane:
    # ANSI color codes for terminal output
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    WHITE = '\033[97m'
    ERROR = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    def __init__(self):
        logging.basicConfig(level=logging.INFO)
        self.output_data = ''
        self.commit_check = []
        self.check_list = []
        self.lock = Lock()  # For thread-safe writes
        self.current_datetime = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        self.args = self.parse_args()
        self.repo = self.args.repo
        self.api_token = self.load_api_token()
        self.header_add = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
            "Authorization": f"Bearer {self.api_token}",
            "X-GitHub-Api-Version": "2022-11-28",
            "Accept": "application/vnd.github+json"
        }

    def parse_args(self):
        parser = argparse.ArgumentParser(description='Github Orphaned Enumeration tool')
        parser.add_argument('--repo', '-r', required=True, type=str,
                            help='Target repository to enumerate (e.g., marantral/orphanedCommit)')
        parser.add_argument('--output', '-o', type=str,
                            default=f"{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}_orphancommit.txt",
                            help="Output file name")
        parser.add_argument('--line', '-l', type=int, default=0,
                            help="Line last looked at within last search")
        parser.add_argument('--fast', '-f', action="store_true",
                            help="Use multi-threading for faster execution (may hit rate limits faster)")
        return parser.parse_args()

    def load_api_token(self):
        config_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), './config/config.ini')
        ini_file = configparser.ConfigParser()
        if not os.path.exists(config_path):
            logging.error(f"Config file not found: {config_path}")
            exit(1)
        ini_file.read(config_path)
        try:
            return ini_file.get('Github.API', 'api_key')
        except (configparser.NoSectionError, configparser.NoOptionError) as e:
            logging.error(f"API key not configured in config.ini: {e}")
            exit(1)

    def build_commit_list(self):
        commit_check_url = f"https://api.github.com/repos/{self.repo}/commits"
        try:
            req = requests.get(commit_check_url, headers=self.header_add)
            req.raise_for_status()
            json_data = req.json()
            self.commit_check = [item['sha'] for item in json_data if 'sha' in item]
        except requests.exceptions.HTTPError as e:
            if req.status_code in (403, 429):
                reset_time = int(req.headers.get('X-RateLimit-Reset', time()))
                wait_time = max(reset_time - time(), 0)
                logging.warning(f"Rate limited. Sleeping for {wait_time} seconds.")
                sleep(wait_time)
                self.build_commit_list()  # Retry
            else:
                logging.error(f"Failed to fetch commits: {e}")
                exit(1)
        except Exception as e:
            logging.error(f"Error fetching commit list: {e}")
            exit(1)

    def load_check_list(self, filename='./config/gitcommitcheck.txt'):
        if not os.path.exists(filename):
            logging.error(f"Commit check file not found: {filename}")
            exit(1)
        with open(filename, 'r') as file:
            for line in file:
                current = line.strip()
                if current and current not in self.check_list:
                    self.check_list.append(current)

    def scan(self, item):
        check_url = f"https://api.github.com/repos/{self.repo}/commits/{item}"
        try:
            req = requests.get(check_url, headers=self.header_add)
            if req.status_code in (403, 429):
                reset_time = int(req.headers.get('X-RateLimit-Reset', time()))
                sleep_time = max(reset_time - time(), 0)
                logging.warning(f"Rate limiting. Sleeping for {sleep_time} seconds.")
                self.save_output()
                sleep(sleep_time)
                return self.scan(item)  # Retry after sleeping

            req.raise_for_status()
            json_data = req.json()
            sha_orphaned_commit = json_data['sha']
            author = json_data['commit']['author']
            with self.lock:
                if sha_orphaned_commit not in self.commit_check:
                    msg = (
                        f"-------------------\n"
                        f"Orphaned Commit Identified: https://github.com/{self.repo}/commit/{sha_orphaned_commit}\n"
                        f"Author information: {author}\n"
                        f"-------------------\n"
                    )
                    logging.info(msg.strip())
                    self.output_data += msg
            xrl = int(req.headers.get('X-RateLimit-Remaining', 100))
            if xrl <= 50:
                reset_time = int(req.headers.get('X-RateLimit-Reset', time()))
                sleep_time = max(reset_time - time(), 0)
                logging.warning(f"Approaching rate limit. Sleeping for {sleep_time} seconds.")
                self.save_output()
                sleep(sleep_time)
            if hasattr(self, 'bar') and self.bar is not None:
                self.bar.next()
        except Exception as e:
            logging.error(f"Error in scan for {item}: {e}")

    def save_output(self):
        try:
            with open(self.args.output, 'w') as file:
                file.write(self.output_data)
        except Exception as e:
            logging.error(f"Error writing output to file: {e}")

    def main(self):
        print(self.GREEN + "!!!!!!!!! BUILDING LISTS !!!!!!!!!" + self.ENDC)
        self.build_commit_list()
        self.load_check_list()
        print(self.BOLD + self.ERROR + self.title_banner() + self.ENDC)
        print(self.GREEN + self.marantral_banner() + self.ENDC)
        self.bar = IncrementalBar('Scanning for Orphaned Commits:', max=len(self.check_list))
        try:
            if self.args.fast:
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    executor.map(self.scan, self.check_list[self.args.line:])
            else:
                for item in self.check_list[self.args.line:]:
                    self.scan(item)
        finally:
            self.bar.finish()
            self.save_output()

    @staticmethod
    def title_banner():
        return """
 #####   ######   ######   ##   ##   ######  ######   #######  ######              ####    #####   ### ##   ### ##    ####     ######  
#######  #######  #######  ##   ##  #######  #######  #######  #######            ######  #######  #######  #######    ##      ######  
### ###  ### ###  ##   ##  ##  ###  ###  ##  ## ####  ##   #   ##  ###           ### ###  ### ###  #######  #######    ##      # ## #  
##   ##  ##  ##   ##  ##   #######  ##   ##  ##  ###  ####     ##   ##           ##   #   ##   ##  ## # ##  ## # ##    ##        ##    
##   ##  ## ##    ####     ### ###  ## ####  ##  ###  ##       ##   ##           ##       ##   ##  ## # ##  ## # ##    ##        ##    
### ###  ##  ##   ##       ##   ##  ##   ##  ##  ##   ##   ##  ##   ##            ##  ##  ### ###  ##   ##  ##   ##   ####       ##    
 #####   ##   ##  ##       ##  ###   ##  ##  ##  ###  #######  ######              ####    #####   ##   ##  ##   ##   ####       ##    
"""

    @staticmethod
    def marantral_banner():
        return """
                          _____             __         __  ___      
                         / ___/______ ___ _/ /____ ___/ / / _ )__ __
                        / /__/ __/ -_) _ `/ __/ -_) _  / / _  / // /
                        \\___/_/  \\__/\\_,_/\\__/\\__/\\_,_/ /____/\\_, / 
                                                            /___/  
                   __  ___                   __           __  ________      
                  /  |/  /__ ________ ____  / /________ _/ / /_  __/ /  ___ 
                 / /|_/ / _ `/ __/ _ `/ _ \\/ __/ __/ _ `/ /   / / / _ \\/ -_)
                /_/  /_/\\_,_/_/  \\_,_/_//_/\\__/_/  \\_,_/_/   /_/ /_//_/\\__/ 

                             __  ___          __           ____
                            /  |/  /__ ____  / /________  / / /
                           / /|_/ / _ `/ _ \\/ __/ __/ _ \\/ / / 
                          /_/  /_/\\_,_/_//_/\\__/_/  \\___/_/_/  

                                        Version 1.0

            !!!!!!!!!!!GO GET SOME COFFEE, THIS WILL TAKE A WHILE!!!!!!!!!!!
"""

if __name__ == '__main__':
    scanner = Orphane()
    scanner.main()