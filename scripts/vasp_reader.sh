#!/usr/bin/env bash
touch ./summary.txt
for file in $(find ./*/OUTCAR -type f); do
    grep "TOTEN" $file >> summary.txt
done

