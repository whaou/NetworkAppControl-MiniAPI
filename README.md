# NetworkAppControl-MiniAPI
Fork of the 5GASP's MiniAPI (https://github.com/5gasp/NetworkAppControl-MiniAPI) to package it as a Debian package

According the [Debian packaging guidelines](https://wiki.debian.org/GitPackaging):
- The upstream code of the 5GASP project lies in the `upstream/latest` branch.
- The packaging code lies in the `debian/latest` branch.


## Initial setup

Git is unhappy with empty repositories.
So, either create a `README.md` (in this case, there will be a small conflict to resolve) or dummy file (as decribed just bellow)
```sh
echo "This file is needed because the initial checkout requires at least one file..." > dummy.txt
git add dummy.txt
git commit -m "Dummy file to populate the inital repository"
```

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

In case there was already a `README.md`, their will be a conflict to solve. This can be done like this:
```sh
git checkout --ours README.md
git add README.md
git rebase --continue
```

