import requests
import concurrent.futures
import json
import configparser
import os
import argparse
from progress.bar import IncrementalBar
from datetime import datetime 



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
    output_data = ''
    current_datetime = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    parser = argparse.ArgumentParser(description='Github Orphaned Enumeration tool')
    parser.add_argument('--repo', '-r', dest="repo", type=str, required=True,
                        help='What is the target  repository that you would like to enumerate?\n\tLike: marantral/orphanedCommit ')
    parser.add_argument('--output', '-o',type=str,  default=f"{current_datetime}_orphancommit.txt",
                        help="Output file name")
    args = parser.parse_args()
    repo = args.repo 
    header_add = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36", "Authorization": f"Bearer {api_token}"
                , "X-GitHub-Api-Version": "2022-11-28",  "Accept": "application/vnd.github+json"}
    def scan(self,item):
        check_url = f"https://api.github.com/repos/{repo}/commits/{item}"
        req = requests.get(check_url, headers=self.header_add)
        if req.status_code == 200:
            try:
                json_data = req.json()
                sha_orphaned_commit = json_data['sha']
                author = json_data['commit']['author']
                files = json_data['commit']['files']
                if sha_orphaned_commit not in self.commit_check:
                    print(f"Orphaned Commit Identified: https://github.com/{repo}/commit/{sha_orphaned_commit}")
                self.output_data += f"-------------------\nOrphaned Commit Identified: https://github.com/{repo}/commit/{sha_orphaned_commit}\n Author information: {author}\n"\
                " File information: \n {files} \n -------------------\n"
            except:
                pass


    commit_check = []
    commit_check_url = f"https://api.github.com/repos/{repo}/commits"

    req = requests.get(commit_check_url, headers=header_add)
    row = 0
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
        bar.next()
        check_url = f"https://api.github.com/repos/{self.repo}/commits/{item}"
        req = requests.get(check_url, headers=self.header_add)
        if req.status_code == 200:
            try:
                json_data = req.json()
                sha_orphaned_commit = json_data['sha']
                if sha_orphaned_commit not in self.commit_check:
                    print(f"Orphaned Commit Identified: https://github.com/{self.repo}/commit/{sha_orphaned_commit}")
            except:
                pass


    check_list = []
    with open('./config/gitcommitcheck.txt', 'r') as file:
        for l in file:
            current = l.strip()
            if current != "":
                if current not in check_list:
                    check_list.append(current)
    def main(self):
        global bar

        bar = IncrementalBar('Deep Scanning Subdomains:', max=65536)
        print(self.BOLD + self.ERROR + r"""
 #####   ######   ######   ##   ##   ######  ######   #######  ######              ####    #####   ### ##   ### ##    ####     ######  
#######  #######  #######  ##   ##  #######  #######  #######  #######            ######  #######  #######  #######    ##      ######  
### ###  ### ###  ##   ##  ##  ###  ###  ##  ## ####  ##   #   ##  ###           ### ###  ### ###  #######  #######    ##      # ## #  
##   ##  ##  ##   ##  ##   #######  ##   ##  ##  ###  ####     ##   ##           ##   #   ##   ##  ## # ##  ## # ##    ##        ##    
##   ##  ## ##    ####     ### ###  ## ####  ##  ###  ##       ##   ##           ##       ##   ##  ## # ##  ## # ##    ##        ##    
### ###  ##  ##   ##       ##   ##  ##   ##  ##  ##   ##   ##  ##   ##            ##  ##  ### ###  ##   ##  ##   ##   ####       ##    
 #####   ##   ##  ##       ##  ###   ##  ##  ##  ###  #######  ######              ####    #####   ##   ##  ##   ##   ####       ##    
                                                                                                                                       
                """ + self.ENDC)
              
        print(self.GREEN + """
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
        """ + self.ENDC)
        with concurrent.futures.ThreadPoolExecutor(max_workers=None) as executor:
            executor.map(self.scan, self.check_list)
        bar.finish()
        with open(self.args.output, 'w') as file:
            file.write(self.output_data)
        
    
       


# call main() function
if __name__ == '__main__':
    scanner = orphane()
    scanner.main()