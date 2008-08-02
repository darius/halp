#!/usr/bin/env bash
# Copyright 2006 by Darius Bacon and Brandon Moore
# Distributed under the terms of the MIT X License, found at
# http://www.opensource.org/licenses/mit-license.php

work=`mktemp -d`
touch ${work}/line_numbers

sed 's/module.*?where/module Main where/' | grep -v '^| ' >${work}/Main.lhs
awk '/^)/ { print NR >"'${work}/line_numbers'";
            print substr($0, 2); }' ${work}/Main.lhs |
  ghci ${work}/Main.lhs 2>&1 |
  awk '
    NR < 10           { next; }
    /Leaving GHCi[.]/ { next; }
                      { sub(/[*]Main> /, "| "); print; } ' |
  paste -d'a' ${work}/line_numbers - >${work}/edits
sed -f ${work}/edits <${work}/Main.lhs

rm -r ${work}
