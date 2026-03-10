# Linux community test container

Build the image:

```bash
docker build -f docker/community-linux.Dockerfile -t infinite-graph-community .
```

Run `sbm_dl`:

```bash
docker run --rm infinite-graph-community python3 tools/test_crisp_algorithms.py --algorithm sbm_dl
```

Run `sbm_dl_nested`:

```bash
docker run --rm infinite-graph-community python3 tools/test_crisp_algorithms.py --algorithm sbm_dl_nested
```

Run the full crisp mono benchmark:

```bash
docker run --rm infinite-graph-community python3 tools/test_crisp_algorithms.py
```

## Linux Python 3.13 Ricci test

Build the dedicated image:

```bash
docker build -f docker/community-linux-py313.Dockerfile -t infinite-graph-community-py313 .
```

Run `ricci_community`:

```bash
docker run --rm infinite-graph-community-py313 python tools/test_crisp_algorithms.py --algorithm ricci_community
```
