# GNOME Hearts build playbook

Builds and installs GNOME Hearts 0.3.1 from the `gnome-hearts-0.3.1/`
source tree in this repo, targeting a modern Linux desktop that no
longer ships GTK2/libglade2/Python 2 as installable packages.

It works around that by creating an [openSUSE Leap 15.4](https://get.opensuse.org/leap/)
[distrobox](https://distrobox.it/) container (openSUSE Leap 15.4 still
carries `gtk2-devel`, `libglade2-devel`, `libgnomeui-devel` and
`python-devel` 2.7 as ordinary packages), compiling the game inside it,
and exporting it as a regular application on the host desktop.

## Requirements

- [Ansible](https://docs.ansible.com/ansible/latest/installation_guide/index.html)
- [Docker](https://docs.docker.com/engine/install/), running, with your
  user in the `docker` group
- [distrobox](https://distrobox.it/#installation)

The playbook checks for Docker and distrobox and stops with instructions
if either is missing — it does not install them itself, since the right
way to do so depends on your distribution.

## Usage

```sh
ansible-playbook playbook.yml
```

Once it finishes, look for **"Hearts (on gnome-hearts)"** in your
application launcher, or run:

```sh
distrobox enter -n gnome-hearts -- gnome-hearts
```
