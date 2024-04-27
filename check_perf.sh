perf record -F 99 -g -- python src/main.py
perf script > out.perf
~/FlameGraph/stackcollapse-perf.pl out.perf > out.folded
~/FlameGraph/flamegraph.pl out.folded > ./flamegraph.svg
