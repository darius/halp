#!/usr/bin/env bash
# Copyright 2006 by Darius Bacon and Brandon Moore
# Distributed under the terms of the MIT X License, found at
# http://www.opensource.org/licenses/mit-license.php

work=`mktemp -d /tmp/halp.XXXXXXXXXX`
touch ${work}/line_numbers

sed 's/module.*?where/module Main where/' | grep -v '^| ' >${work}/Main.lhs

echo '

> aouhtnuoeahn = 0 -- Ensure file has *some* code.' >>${work}/Main.lhs

awk '/^[)]/ { print NR >"'${work}/line_numbers'";
              print substr($0, 2); }' ${work}/Main.lhs |
  ghci ${work}/Main.lhs 2>&1 |
  awk '
    NR <= 4           { next; }
    /Leaving GHCi[.]/ { next; }
                      { sub(/[*]Main> /, "| "); print; } ' |
  awk '
    { getline linenumber <"'${work}/line_numbers'";
      print linenumber "a \\";
      print $0; }' >${work}/edits

sed -f ${work}/edits <${work}/Main.lhs | 
  awk '{ line[NR] = $0; }; END { for (i = 1; i <= NR-3; ++i) print line[i]; }'

rm -r ${work}
