# ophelia

> an opinionated helium fork


## Features

- **Containers**: stay signed in to different accounts on the same site in
  separate tabs, without making another profile. Each Container keeps its own
  cookies and site data.
  - Open tabs and links in a Container from the tab and link menus.
  - A Container's tabs are marked with its color in the tab strip.
  - Links stay in their tab's Container.
  - Container tabs come back in their Container after a restart and in saved
    tab groups.
  - Add, edit, reorder and delete Containers in settings. Deleting one also
    deletes its tabs and data.
  - Turn Containers on under Profiles and Containers in settings.
- **Square corners**: two Appearance switches, one for the browser UI and
  internal pages, one for websites.
- **New tab search**: new tab focuses an empty address bar instead of opening a
  blank tab, and what you open from it goes in a new tab. Also works for new
  tabs in groups and split views. An Appearance switch, off by default.


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
