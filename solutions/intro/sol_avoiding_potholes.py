import json
import sys
import urllib.request

OWNER = "gvwilson"
REPO = "sdxpy"
URL = f"https://api.github.com/repos/{OWNER}/{REPO}/issues?state=open&per_page=100"


def fetch_issues(url):
    """Fetch issues from the GitHub API and return parsed JSON."""
    req = urllib.request.Request(url)
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("User-Agent", "sdxpy-exercise/1.0")
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode("utf-8"))


def analyze(issue):
    """Return a dictionary of readability metrics for one issue."""
    body = issue.get("body") or ""
    title = issue["title"]
    return {
        "number": issue["number"],
        "title": title,
        "title_length": len(title),
        "body_length": len(body),
        "has_code_block": "```" in body,
        "has_numbered_steps": any(
            line.strip().startswith(("1.", "1)", "1-"))
            for line in body.splitlines()
        ),
        "comment_count": issue["comments"],
    }


def main():
    try:
        issues = fetch_issues(URL)
    except Exception as exc:
        print(f"Could not fetch issues: {exc}", file=sys.stderr)
        sys.exit(1)

    # Filter out pull requests (GitHub includes them in the issues endpoint).
    real_issues = [i for i in issues if "pull_request" not in i]
    print(f"Found {len(real_issues)} open issues.\n")

    analyzed = [analyze(i) for i in real_issues]
    analyzed.sort(key=lambda a: a["number"])

    for a in analyzed:
        flags = []
        if a["has_code_block"]:
            flags.append("code")
        if a["has_numbered_steps"]:
            flags.append("steps")
        print(f"#{a['number']}: {a['title']}")
        print(f"  title={a['title_length']} chars  "
              f"body={a['body_length']} chars  "
              f"comments={a['comment_count']}  "
              f"features={flags or ['none']}")
        print()


if __name__ == "__main__":
    main()
