#!/usr/bin/env python3
"""Rebuild index.html from template + brands_index.json.
NO duplicate animation code. NO corrupted brandsData.
Then sync gh-pages for GitHub Pages deployment.

Usage: python3 update_homepage.py [--no-push] [--no-sync]
"""
import json, re, shutil, sys, os, subprocess

WORKSPACE = "/workspace/pinpai-ai-in"
WWW = "/var/www/pinpai"
TEMPLATE = f"{WORKSPACE}/index.html"
BRANDS_JSON = f"{WORKSPACE}/brands_index.json"
OUTPUT = f"{WORKSPACE}/index.html"  # same file, we rebuild inline

NO_PUSH = "--no-push" in sys.argv
NO_SYNC = "--no-sync" in sys.argv

def esc(s):
    return s.replace("\\\\", "\\\\\\\\").replace('"', '\\\\"').replace("\\n", "\\\\n").replace("\\r", "\\\\r")

def main():
    # 1. Read template
    with open(TEMPLATE, "r") as f:
        template = f.read()

    # 2. Read brand data
    with open(BRANDS_JSON, "r") as f:
        brands = json.load(f)

    # 3. Build JS array
    lines = []
    for b in brands:
        t = b.get('t', 1)
        line = '{{name:"{0}",name_en:"{1}",slug:"{2}",category:"{3}",t:{4}}}'.format(
            esc(b['name']), esc(b.get('name_en', '')), esc(b['slug']), esc(b.get('category', '')), t
        )
        lines.append(line)
    js_array = "var brandsData = [\\n" + ",\\n".join(lines) + "\\n];"

    # 4. Replace ONLY the first var brandsData = []
    if "var brandsData = [];" in template:
        html = template.replace("var brandsData = [];", js_array, 1)
    else:
        # Fallback with exact match from template.html
        html = re.sub(
            r'var brandsData = \\[.*?\\];',
            js_array,
            template,
            count=1,
            flags=re.DOTALL
        )

    # 5. Verify structure
    errors = []
    if "updateAnimation" not in html:
        errors.append("updateAnimation missing")
    anim_count = html.count("setInterval(updateAnimation")
    if anim_count != 1:
        errors.append(f"setInterval(updateAnimation) count = {anim_count}")
    bdata_count = html.count("var brandsData")
    if bdata_count != 1:
        errors.append(f"var brandsData count = {bdata_count}")

    if errors:
        print("ERRORS: " + "; ".join(errors))
        sys.exit(1)

    # 6. Write workspace output
    with open(OUTPUT, "w") as f:
        f.write(html)

    print(f"OK: workspace/index.html rebuilt")
    print(f"  Size: {len(html)} bytes")
    print(f"  Brands: {len(brands)}")
    print(f"  Animation: OK")
    print(f"  setInterval(updateAnimation): {anim_count}")

    # 7. Copy to www directory
    if os.path.isdir(WWW):
        with open(f"{WWW}/index.html", "w") as f:
            f.write(html)
        print(f"  Copied to {WWW}/index.html")

    # 8. Git commit + push
    if not NO_PUSH:
        os.chdir(WORKSPACE)
        rc = os.system("git add index.html && git commit -m 'rebuild index.html with " + str(len(brands)) + " brands' && git push")
        if rc == 0:
            print(f"  Git push: OK")
        else:
            print(f"  Git push: returned {rc}")

    # 9. Sync gh-pages
    if not NO_SYNC and not NO_PUSH:
        _sync_gh_pages()

def _sync_gh_pages():
    gh_deploy = "/tmp/gh-pages-deploy-toot"
    try:
        if os.path.exists(gh_deploy):
            shutil.rmtree(gh_deploy, ignore_errors=True)
        os.system(f"cd {WORKSPACE} && git worktree prune 2>/dev/null")

        rc = os.system(f"cd {WORKSPACE} && git worktree add {gh_deploy} gh-pages 2>/dev/null")
        if rc == 0:
            os.system(f"cd {gh_deploy} && git rm -rf . 2>/dev/null")
            shutil.copy(f"{WORKSPACE}/index.html", f"{gh_deploy}/index.html")
            os.system(f"cd {gh_deploy} && git add index.html && git commit -m 'deploy: sync gh-pages'")
            push_rc = os.system(f"cd {gh_deploy} && git push origin gh-pages --force")
            if push_rc == 0:
                print(f"  gh-pages sync: OK")
            else:
                print(f"  gh-pages push: returned {push_rc}")
            os.system(f"cd {WORKSPACE} && git worktree remove {gh_deploy} 2>/dev/null")
            shutil.rmtree(gh_deploy, ignore_errors=True)
        else:
            _fallback_sync()
    except Exception as e:
        print(f"  gh-pages sync error: {e}")
        _fallback_sync()

def _fallback_sync():
    print("  Using fallback gh-pages sync...")
    os.system(f"cd {WORKSPACE} && git branch -D gh-pages 2>/dev/null")
    os.system(f"cd {WORKSPACE} && git checkout -b gh-pages 2>/dev/null")
    os.system(f"cd {WORKSPACE} && git rm -rf . 2>/dev/null")
    os.system(f"cd {WORKSPACE} && git checkout main -- index.html 2>/dev/null")
    os.system(f"cd {WORKSPACE} && git add index.html && git commit -m 'deploy: sync gh-pages'")
    os.system(f"cd {WORKSPACE} && git push origin gh-pages --force")
    os.system(f"cd {WORKSPACE} && git checkout main")

if __name__ == "__main__":
    main()
