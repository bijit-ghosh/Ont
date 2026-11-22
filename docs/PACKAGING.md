# Packaging and installation

## Artifacts

| Artifact | Contents | Intended use |
| --- | --- | --- |
| Python wheel | `ont` modules, CLI, packaged browser assets and MIT license | Installable runtime and isolated demo |
| Source distribution | Python source plus browser source, native source, guides, examples and developer checks | Rebuild and inspect the project |
| Git source archive | Tracked repository state, including CI configuration | Full repository handoff |
| Docker image | Locked Python runtime and browser assets | Reproducible service deployment |

Build and install artifacts from this repository. Wheel metadata uses the distribution name `ont-software-factory`; the installed command is `ont`. The JavaScript console is bundled with the wheel, not published to npm. Rust source is supplied separately; the wheel does not contain a native scheduler binary.

## Build from source

```bash
python -m pip install -r requirements.lock.txt
python -m pip install -r requirements-build.txt
python -m build --no-isolation
python scripts/package_smoke.py
```

Build artifacts appear in `dist/`. The smoke test installs the wheel into a disposable directory outside the checkout, serves its packaged assets through the test client, creates a complete labeled demo fixture, and checks the CLI version. It makes no live model or deployment calls.

`requirements.lock.txt` pins application dependencies for this release. `requirements-build.txt` pins build tools. Package metadata declares compatible dependency ranges; use the runtime lock when preparing a controlled deployment. The build backend copies current `web/` sources into the wheel's `ont/static/` directory, avoiding stale checked-in duplicates.

## Install a wheel

```bash
python -m pip install -r requirements.lock.txt
python -m pip install --no-deps dist/ont_software_factory-0.1.0-py3-none-any.whl
ont --version
ont serve
```

The default database lives under the working directory's `data/`, not inside site-packages. Set `ONT_DB` for a different persistent path. `ont demo` creates a separate demo database and refuses to overwrite an existing one.

## Release checklist

Build wheel and source distribution, run the isolated package smoke, run the complete source gate, build the Docker image, run container smoke, and inspect the matching CI result. Record artifact hashes and publish only the artifacts built from that exact commit. A package build passing is not a security audit or external integration qualification.
