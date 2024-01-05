# NetworkAppControl-MiniAPI
Fork of the 5GASP's MiniAPI
(https://github.com/5gasp/NetworkAppControl-MiniAPI) to package it as a
Debian package

According to the [Debian packaging guidelines](https://wiki.debian.org/GitPackaging):
- The upstream code of the 5GASP project lies in the `upstream/latest`
  branch. This is not delivered within this repository, but can be added
  manually using the the commands described [bellow](#add-the-upstreamlatest-and-configure-it-to-track-the-upstream-repository).
- The packaging code lies in the `debian/latest` branch. In this branch,
  - The `src/` directory contains the source code from upstream with
    slight modifications to make it easier to package. Basically:
    - The main code of miniapi is turned into a python module
    - We add an `__init__.py` to the miniapi module to start the miniAPI
      from the command line.
    - We use the python setup tools to package the python code. So that 
      debian helper (or dpkg-build) can easily build the package.
   - The `debian/` directory contains the files to set up the deb
     package (including the systemctl files to start the miniAPI as a
     linux daemon)



## Instal git-buildpackage and other dependencies for the build phase

```sh
sudo apt install -y git-buildpackage
sudo apt install -y dh-python python3-setuptools python3-pydantic
```


## Run git-buildpackage

*Note:* By default, git-buildpackage will try to sign the package with
the author's GPG key. For that:
* Either edit the author email in the `debian/changelog` of the
  `debian/latest` branch. This suppose that you have a GPG key for this 
  email already installed on your system...
* Or pass the `-uc -us` parameters to git-buildpackage to skip the 
  signature .

```sh
git checkout debian/latest
gbp buildpackage --git-ignore-branch --git-ignore-new
```
The compilation results (`.deb`, `.tgz`, etc) will be placed in the
parent folder. This can be changed with the `--git-export-dir=XXXX`
parameter.



## Add the upstream/latest and configure it to track the upstream repository

```sh
# Add the upstream remote source
git remote add 5gasp git@github.com:5gasp/NetworkAppControl-MiniAPI.git
git remote -vv

# Fetch upstream history
git fetch 5gasp

# Create the upstream/latest branch
git checkout -b upstream/latest

# Set the upstream/latest branch to track the upstream repository
git branch -u 5gasp/main
git rebase 5gasp/main
```

In case there was already a `README.md`, there will be a conflict to 
solve. This can be done like this:
```sh
git checkout --ours README.md
git add README.md
git rebase --continue
```
