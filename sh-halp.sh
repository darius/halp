#!/usr/bin/env bash
# Copyright 2006 by Darius Bacon and Brandon Moore
# Distributed under the terms of the MIT X License, found at
# http://www.opensource.org/licenses/mit-license.php

work=`mktemp -d`
touch ${work}/line_numbers

grep -v '^| ' >${work}/input
awk '/^[$]/ { print NR >"'${work}/line_numbers'";
              print "echo -n SEP;" substr($0, 2); }' ${work}/input |
  sh | sed 's/^SEP/| /' |
  paste -d'a' ${work}/line_numbers - >${work}/edits
sed -f ${work}/edits <${work}/input

rm -r ${work}
