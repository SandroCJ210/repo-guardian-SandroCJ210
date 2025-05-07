"""
    Only run this script locally. This generates the fixtures used for testing purposes. 
"""
import os
import shutil
import subprocess
import stat
from pathlib import Path

FIXTURES_DIR = Path(__file__).resolve().parent.parent / "fixtures"
FIXTURES_DIR.mkdir(exist_ok=True)

def run(cmd, cwd):
    subprocess.run(cmd, cwd=cwd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def force_remove_readonly(func, path, _):
    os.chmod(path, stat.S_IWRITE)
    func(path)

def create_clean_repo(path):
    run(["git", "init", "--bare"], cwd=path.parent)
    return path

def create_corrupt_blob_repo():
    repo_path = FIXTURES_DIR / "corrupt-blob.git"
    
    if repo_path.exists():
        shutil.rmtree(repo_path, onerror=force_remove_readonly)
    
    repo_path.mkdir(parents=True)
    
    run(["git", "init"], cwd=repo_path)

    # Crear un archivo de texto
    blob_file = repo_path / "loose.txt"
    blob_file.write_text("This is a loose blob object")

    # Crear loose object
    run(["git", "hash-object", "-w", "loose.txt"], cwd=repo_path)

    blob_hash = subprocess.check_output(
        ["git", "hash-object", "loose.txt"], cwd=repo_path
    ).decode().strip()

    print(f"✓ Loose blob created: {blob_hash} → stored in .git/objects/{blob_hash[:2]}/{blob_hash[2:]}")
    
def create_pack_corrupt_repo():
    repo_path = FIXTURES_DIR / "pack-corrupt.git"
    if repo_path.exists():
            shutil.rmtree(repo_path, onerror=force_remove_readonly)
    repo_path.mkdir()
    run(["git", "init"], cwd=repo_path)

    for i in range(10):
        (repo_path / f"file{i}.txt").write_text(f"linea {i}")
        run(["git", "add", f"file{i}.txt"], cwd=repo_path)
        run(["git", "commit", "-m", f"commit {i}"], cwd=repo_path)

    run(["git", "gc", "--aggressive", "--prune=now"], cwd=repo_path)

    pack_dir = repo_path / ".git" / "objects" / "pack"
    for packfile in pack_dir.glob("*.pack"):
        packfile.chmod(0o644)
        with open(packfile, "rb+") as f:
            f.seek(-20, os.SEEK_END)  
            f.truncate()

def create_rewrite_case_repo():
    repo_path = FIXTURES_DIR / "rewrite-case.git"
    if repo_path.exists():
            shutil.rmtree(repo_path, onerror=force_remove_readonly)
    repo_path.mkdir()
    run(["git", "init"], cwd=repo_path)


    (repo_path / "main.txt").write_text("A")
    run(["git", "add", "main.txt"], cwd=repo_path)
    run(["git", "commit", "-m", "A"], cwd=repo_path)

    (repo_path / "main.txt").write_text("B")
    run(["git", "add", "main.txt"], cwd=repo_path)
    run(["git", "commit", "-m", "B"], cwd=repo_path)

    run(["git", "checkout", "-b", "temp"], cwd=repo_path)
    run(["git", "reset", "--hard", "HEAD~1"], cwd=repo_path)
    (repo_path / "main.txt").write_text("B-prime")
    run(["git", "add", "main.txt"], cwd=repo_path)
    run(["git", "commit", "-m", "B (rewritten)"], cwd=repo_path)

def main():
    print("Generando fixtures...")
    create_corrupt_blob_repo()
    print("corrupt-blob.git listo.")
    create_pack_corrupt_repo()
    print("pack-corrupt.git listo.")
    create_rewrite_case_repo()
    print("✅ rewrite-case.git listo.")

if __name__ == "__main__":
    main()
