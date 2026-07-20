# GNOME Hearts build playbook

Builds and installs GNOME Hearts 0.3.1 from the `gnome-hearts-0.3.1/`
source tree in this repo, targeting a modern Arch Linux desktop that no
longer ships GTK2/libglade2/Python 2 as installable packages.

It works around that by creating an [openSUSE Leap 15.4](https://get.opensuse.org/leap/)
[distrobox](https://distrobox.it/) container (openSUSE Leap 15.4 still
carries `gtk2-devel`, `libglade2-devel`, `libgnomeui-devel` and
`python-devel` 2.7 as ordinary packages), compiling the game inside it,
and exporting it as a regular application on the host desktop.

## Requirements

- Arch Linux
- [Ansible](https://archlinux.org/packages/extra/any/ansible/)

## Usage

```sh
ansible-galaxy collection install -r requirements.yml
ansible-playbook -K playbook.yml
```

`-K` prompts for your sudo password, needed to install `distrobox`/`docker`,
enable the docker service, and add your user to the `docker` group.

If you weren't already in the `docker` group, the playbook will stop and
ask you to log out and back in (or run `newgrp docker`) before re-running
it.

Once it finishes, look for **"Hearts (on gnome-hearts)"** in your
application launcher, or run:

```sh
distrobox enter -n gnome-hearts -- gnome-hearts
```
