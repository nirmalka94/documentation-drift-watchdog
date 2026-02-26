import git
from unidiff import PatchSet
import tempfile
import os

class GitDiffExtractor:
    def __init__(self, repo_url, branch, local_dir=None):
        self.repo_url = repo_url
        self.branch = branch
        self.local_dir = local_dir or tempfile.mkdtemp()
        self.repo = None

    def clone_or_pull(self):
        if not os.path.exists(self.local_dir):
            self.repo = git.Repo.clone_from(self.repo_url, self.local_dir, branch=self.branch)
        else:
            self.repo = git.Repo(self.local_dir)
            self.repo.remotes.origin.pull()

    def get_diff(self, from_commit, to_commit):
        self.clone_or_pull()
        diff = self.repo.git.diff(f'{from_commit}..{to_commit}', unified=0)
        return PatchSet(diff)
