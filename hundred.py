# run_hundred.py
import os, shutil, subprocess, tempfile, glob
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from git import Repo

OUTPUT_DIR = os.getcwd()
PROJECT = {
    'name': 'Hundred Finance',
    'repo': 'https://github.com/Hundred-Finance/hundred-finance-v2.git',
    'lang': 'solidity',
    'crash': '2023-04-16',
    'type': '技术漏洞'
}

def solidity_metrics(repo_path):
    sol_files = glob.glob(f'{repo_path}/**/*.sol', recursive=True)
    if not sol_files:
        return {'dit': 0, 'cbo': 0}
    dit_sum = 0
    import_count = 0
    for f in sol_files:
        with open(f, 'r', errors='ignore') as fp:
            content = fp.read()
            dit_sum += content.count(' is ') + content.count(' implements ')
            import_count += content.count('import ') + content.count(' from ')
    num = len(sol_files)
    dit = min(dit_sum / num, 5) if num else 0
    cbo = min(import_count / num, 20) if num else 0
    return {'dit': dit, 'cbo': cbo}

tmp = tempfile.mkdtemp()
try:
    print(f"Cloning {PROJECT['repo']}...")
    Repo.clone_from(PROJECT['repo'], tmp, depth=1)
    os.chdir(tmp)
    res = subprocess.run(['git', 'log', '--format=%H,%ct'], capture_output=True, text=True)
    data = []
    for line in res.stdout.strip().split('\n'):
        if ',' in line:
            h, ts = line.split(',')
            data.append((h, int(ts)))
    commits = pd.DataFrame(data, columns=['hash', 'timestamp'])
    commits['timestamp'] = pd.to_datetime(commits['timestamp'], unit='s')
    if commits.empty:
        raise Exception("No commits")
    m = solidity_metrics(tmp)
    x1 = min(m['dit'] / 10, 1.0)
    x3 = min(m['cbo'] / 30, 1.0)
    n = len(commits)
    commits['x1'] = x1
    commits['x2'] = np.random.uniform(0.3, 0.7, n)
    commits['phi'] = 2 * np.pi * commits['x2'] - np.pi
    commits['x3'] = x3
    commits['x4'] = np.linspace(0, 1, n)
    commits['x5'] = 0.1
    commits['x6'] = np.random.uniform(0, 1, n)
    commits['theta'] = 2 * np.pi * commits['x1'] - np.pi
    commits['alpha'] = commits['theta'] + commits['phi']
    commits['sigma'] = np.tanh(5.0 * (np.pi - np.abs(commits['alpha'])))
    commits['icdi'] = 100 * (0.3*commits['x1'] + 0.25*commits['x2'] + 0.25*(commits['phi']+np.pi)/(2*np.pi) + 0.2*(1-commits['x5']))
    # 绘图
    fig, axs = plt.subplots(4,1,figsize=(12,10))
    axs[0].plot(commits['timestamp'], commits['alpha'])
    axs[0].axvline(pd.to_datetime(PROJECT['crash']), color='r', linestyle='--')
    axs[0].set_ylabel('α')
    axs[1].plot(commits['timestamp'], commits['theta'], label='θ')
    axs[1].plot(commits['timestamp'], commits['phi'], label='φ')
    axs[1].legend()
    axs[2].plot(commits['timestamp'], commits['sigma'], color='purple')
    axs[2].axhline(0, color='k', linestyle=':')
    axs[3].plot(commits['timestamp'], commits['icdi'])
    axs[3].axhline(50, color='orange', linestyle='--')
    plt.suptitle(f"{PROJECT['name']} ({PROJECT['type']})")
    plt.tight_layout()
    img_path = os.path.join(OUTPUT_DIR, f"{PROJECT['name']}.png")
    plt.savefig(img_path)
    plt.close()
    print(f"Saved {img_path}")
except Exception as e:
    print(f"Error: {e}")
finally:
    shutil.rmtree(tmp, ignore_errors=True)
