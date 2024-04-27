perf record -F 99 -g -- python src/main.py
perf script > out.perf

if [ -d "~/FlameGraph" ]; then
    echo "WARNING. You should replace some my machine-specific paths in script if you don't have FlameGraph dir in home or install it there"
else
    ~/FlameGraph/stackcollapse-perf.pl out.perf > out.folded
    ~/FlameGraph/flamegraph.pl out.folded > ./flamegraph.svg
fi
                              
