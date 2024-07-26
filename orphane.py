import requests
import concurrent.futures
import configparser
import os
import argparse
from progress.bar import IncrementalBar
from datetime import datetime 
from time import sleep 
import time


ini_file = configparser.ConfigParser()
ini_file.read(os.path.join(os.path.abspath(os.path.dirname(__file__)), './config/config.ini'))
api_token = ini_file.get('Github.API', 'api_key')

class orphane():
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    WHITE = '\033[97m'
    ERROR = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    title = """
 #####   ######   ######   ##   ##   ######  ######   #######  ######              ####    #####   ### ##   ### ##    ####     ######  
#######  #######  #######  ##   ##  #######  #######  #######  #######            ######  #######  #######  #######    ##      ######  
### ###  ### ###  ##   ##  ##  ###  ###  ##  ## ####  ##   #   ##  ###           ### ###  ### ###  #######  #######    ##      # ## #  
##   ##  ##  ##   ##  ##   #######  ##   ##  ##  ###  ####     ##   ##           ##   #   ##   ##  ## # ##  ## # ##    ##        ##    
##   ##  ## ##    ####     ### ###  ## ####  ##  ###  ##       ##   ##           ##       ##   ##  ## # ##  ## # ##    ##        ##    
### ###  ##  ##   ##       ##   ##  ##   ##  ##  ##   ##   ##  ##   ##            ##  ##  ### ###  ##   ##  ##   ##   ####       ##    
 #####   ##   ##  ##       ##  ###   ##  ##  ##  ###  #######  ######              ####    #####   ##   ##  ##   ##   ####       ##    
                                                                                                                                       
                """ 
    marantral = """
                          _____             __         __  ___      
                         / ___/______ ___ _/ /____ ___/ / / _ )__ __
                        / /__/ __/ -_) _ `/ __/ -_) _  / / _  / // /
                        \___/_/  \__/\_,_/\__/\__/\_,_/ /____/\_, / 
                                                            /___/  
                   __  ___                   __           __  ________      
                  /  |/  /__ ________ ____  / /________ _/ / /_  __/ /  ___ 
                 / /|_/ / _ `/ __/ _ `/ _ \/ __/ __/ _ `/ /   / / / _ \/ -_)
                /_/  /_/\_,_/_/  \_,_/_//_/\__/_/  \_,_/_/   /_/ /_//_/\__/ 

                             __  ___          __           ____
                            /  |/  /__ ____  / /________  / / /
                           / /|_/ / _ `/ _ \/ __/ __/ _ \/ / / 
                          /_/  /_/\_,_/_//_/\__/_/  \___/_/_/  

                                        Version 1.0

            !!!!!!!!!!!GO GET SOME COFFEE, THIS WILL TAKE A WHILE!!!!!!!!!!!
        """ 
    output_data = ''
    current_datetime = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    parser = argparse.ArgumentParser(description='Github Orphaned Enumeration tool')
    parser.add_argument('--repo', '-r', dest="repo", type=str, required=True,
                        help='What is the target  repository that you would like to enumerate?\n\tLike: marantral/orphanedCommit ')
    parser.add_argument('--output', '-o',type=str,  default=f"{current_datetime}_orphancommit.txt",
                        help="Output file name")
    parser.add_argument('--line', '-l', type=int, default=0,
                        help="Line last looked at within last search.")
    parser.add_argument('--fast', '-f', default=False, action="store_true",
                        help="Use multi-threading to go fast. This will cause rate limiting to occur faster requiring a sleep.")
    args = parser.parse_args()
    repo = args.repo 
    header_add = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36", "Authorization": f"Bearer {api_token}"
                , "X-GitHub-Api-Version": "2022-11-28",  "Accept": "application/vnd.github+json"}
    


    commit_check = []
    commit_check_url = f"https://api.github.com/repos/{repo}/commits"

    req = requests.get(commit_check_url, headers=header_add)
    row = 0
    
    if req.status_code == 403 or req.status_code == 429:
        print(BOLD + ERROR + title + ENDC)        
        print(GREEN + marantral + ENDC)
        print(req.headers['X-RateLimit-Reset'])
        print("You have been rate limited by Github or have not added a valid api key in the config.ini file.")
        exit()
    json_data = req.json()
    try:
        sha = json_data[row]['sha']
        check = True
    except:
        check = False

    while check:
        try:
            sha = json_data[row]['sha']
            if sha not in commit_check:
                commit_check.append(sha)
            row +=1
        except:
            check = False
    
    def scan(self,item):
        check_url = f"https://api.github.com/repos/{self.repo}/commits/{item}"
        req = requests.get(check_url, headers=self.header_add)
        if req.status_code == 200:
            try:
                json_data = req.json()
                sha_orphaned_commit = json_data['sha']
                author = str(json_data['commit']['author'])
                print(req.headers['X-RateLimit-Remaining'])
                if sha_orphaned_commit not in self.commit_check:
                    print(self.BOLD + self.ERROR + f"-------------------\nOrphaned Commit Identified: https://github.com/{self.repo}/commit/{sha_orphaned_commit}\n Author information:")
                    print({author})
                    print("\n-------------------\n" + self.ENDC)
                    self.output_data += f"-------------------\nOrphaned Commit Identified: https://github.com/{self.repo}/commit/{sha_orphaned_commit}\n Author information: {author}\n-------------------\n"
            except:
                pass
        if req.status_code == 403 or req.status_code == 429:
            sleep_time = int(req.headers['x-ratelimit-reset']) - time.time()
            print(f"\n\nYou have been rate limited by Github. Sleeping until ratelimit resets! Which is: {str(sleep_time)} seconds")
            sleep(sleep_time)
            with open(self.args.output, 'w') as file:
                file.write(self.output_data) 
        if 50 >= int(req.headers['X-RateLimit-Remaining']):
            sleep_time = int(req.headers['x-ratelimit-reset']) - time.time()
            print(f"Rate limiting is about to be active! Sleeping until ratelimit resets! Which is: {str(sleep_time)} seconds")
            
            sleep(sleep_time)                    
        bar.next()


    check_list = []
    with open('./config/gitcommitcheck.txt', 'r') as file:
        for l in file:
            current = l.strip()
            if current != "":
                if current not in check_list:
                    check_list.append(current)
    def main(self):
        global bar

        
        print(self.BOLD + self.ERROR + self.title + self.ENDC)
              
        print(self.GREEN + self.marantral + self.ENDC)
        bar = IncrementalBar('Scanning for Orphaned Commits:', max=65536)
        
        if self.args.fast:
            with concurrent.futures.ThreadPoolExecutor(max_workers=None) as executor:
                executor.map(self.scan, self.check_list)
        else:
            for item in self.check_list[self.args.line:]:
                self.scan(item)
        bar.finish()
        with open(self.args.output, 'w') as file:
            file.write(self.output_data)
        
    
       


# call main() function
if __name__ == '__main__':
    scanner = orphane()
    scanner.main()