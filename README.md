# ophelia

> an opinionated helium fork


## Layout

Shared by every platform:

- `patches/` – Ophelia patches, applied after Helium's
- `branding/` – Ophelia icons and logos
- `scripts/build.py` – builds Ophelia for one platform
- `scripts/rebrand.py` – renames Helium to Ophelia in the source tree

Per platform, in `platforms/<os>/`:

- `upstream/` – the upstream Helium platform repo (submodule, pinned to a
  release tag; it pins `helium-chromium` itself)
- `patches/` – patches only this platform needs, applied after `patches/`
- `package/` – packaging (e.g. desktop file and metainfo on Linux)
- `build.py` – the platform steps `scripts/build.py` calls, driving `upstream/`


## License

Ophelia is licensed under GPL-3.0, see [LICENSE](LICENSE). Upstream Helium and
the projects it imports keep their own licenses, e.g. ungoogled-chromium code
remains under the [BSD 3-Clause license](LICENSE.ungoogled_chromium).
