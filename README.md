# ophelia

> an opinionated helium fork


## Layout

- `helium-linux/` – upstream [helium-linux](https://github.com/imputnet/helium-linux)
  (submodule, pinned to a release tag; it pins `helium-chromium` itself)
- `patches/` – Ophelia patches, applied after Helium's
- `scripts/build.sh` – makes a development build with Ophelia's patches
- `scripts/mtimes.py` – keeps files rewritten with the same content from
  triggering rebuilds


## Building

Builds run in a distrobox made from helium-linux's builder image, so you need
podman, distrobox and mise:

```sh
mise run setup   # fetch the upstream repos and create the box
mise run build   # build in the box
mise run run     # run the build with a separate profile
```


## License

Ophelia is licensed under GPL-3.0, see [LICENSE](LICENSE). Helium and Chromium,
pulled in through the `helium-linux` submodule, keep their own licenses.
