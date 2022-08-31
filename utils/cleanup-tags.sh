#!/bin/sh
git tag | xargs -L 1 | xargs git push origin --delete
git tag | xargs -L 1 | xargs git tag --delete
