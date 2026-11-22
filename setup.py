"""Ship the same browser assets used by the source checkout inside the wheel."""
from pathlib import Path
import shutil
from setuptools import setup
from setuptools.command.build_py import build_py

class BuildWithWeb(build_py):
    def run(self):
        super().run()
        shutil.copytree(Path(__file__).parent/'web',Path(self.build_lib)/'ont'/'static',dirs_exist_ok=True)

setup(cmdclass={'build_py':BuildWithWeb})
