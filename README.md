
---

# orphanedCommit

A Python tool to identify **orphaned commits** in a GitHub repository. Orphaned commits are commits that are no longer referenced by any branch or tag, but still exist in the repository’s history.

---

## Features

- Scans a GitHub repository for orphaned commits using the GitHub API
- Supports multi-threaded scanning for speed (with rate limit handling)
- Outputs detailed information on identified orphaned commits
- Customizable output file and resume progress from a specific line

---

## Installation

1. **Clone this repository:**
   ```bash
   git clone https://github.com/Marantral/orphanedCommit.git
   cd orphanedCommit
   ```

2. **Create a GitHub personal access token**  
   - Go to [GitHub Settings > Developer settings > Personal access tokens](https://github.com/settings/tokens)
   - Generate a token with `repo` access

3. **Configure your token:**  
   - Copy `config/config.ini.example` to `config/config.ini`
   - Edit `config/config.ini` and paste your GitHub token under `[Github.API]` as `api_key`

4. **Install dependencies:**  
   ```bash
   pip install -r requirements.txt
   ```

---

## Usage

Basic usage:
```bash
python3 ./orphane.py -r 'owner/repo' -o "output.txt"
```

**Options:**
- `-r`, `--repo` (required): Target repository (e.g., `marantral/orphanedCommit`)
- `-o`, `--output`: Output file name (default: timestamped)
- `-l`, `--line`: Resume from a specific line number in the check list
- `-f`, `--fast`: Enable multi-threading for faster scanning (may hit GitHub rate limits sooner)

**Examples:**
```bash
# Standard scan
python3 ./orphane.py -r 'marantral/test' -o "marantraloutput.txt"

# Fast scan (multi-threaded, will require waiting if rate limited)
python3 ./orphane.py -r 'marantral/test' -f -o "marantraloutput.txt"
```

---

## Output

Results are saved to the specified output file with details about each orphaned commit, including commit SHA and author information.

---

## Notes

- If you encounter GitHub API rate limiting, the tool will pause until limits reset.
- Ensure your `gitcommitcheck.txt` file (in `config/`) contains the list of commits to check, one per line.
- For large repositories, scanning may take a while.

---

## Contributing

Pull requests and issues are welcome!  
Please open an issue for bugs, questions, or feature requests.

---

## License

MIT License

---

Do you want to add a project description, usage tips, or links to related resources? Let me know if you’d like this template tailored further or want it formatted for direct commit.