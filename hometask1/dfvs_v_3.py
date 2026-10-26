import signal
import sys
import time

stop = False


def on_sigterm(signum, frame):
    global stop
    stop = True


def read_graph():
    lines = sys.stdin.buffer.read().split(b'\n')
    n = int(lines[0].split()[0])
    adj = []
    for line in lines[1:n + 1]:
        adj.append([int(x) - 1 for x in line.split()])
    return n, adj


def greedy(n, adj, deadline):
    out = [set(row) for row in adj]
    inc = [set() for _ in range(n)]
    for v in range(n):
        for u in out[v]:
            inc[u].add(v)
    alive = set(range(n))
    answer = set()
    stack = list(range(n))

    while alive and not stop and time.monotonic() < deadline:
        if stack:
            v = stack.pop()
            if v not in alive:
                continue
            take = v in out[v]  
            if not take and len(inc[v]) > 1 and len(out[v]) > 1:
                continue
        else:
            v = max(alive, key=lambda u: len(inc[u]) * len(out[u]))
            take = True

        before = list(inc[v])
        after = list(out[v])
        alive.remove(v)
        for u in before:
            out[u].discard(v)
        for u in after:
            inc[u].discard(v)
        out[v] = set()
        inc[v] = set()

        if take:
            answer.add(v)
        else:
            for u in before:
                for w in after:
                    out[u].add(w)
                    inc[w].add(u)
        stack.extend(before)
        stack.extend(after)

    answer.update(alive)
    return answer

def is_correct(adj, answer):
    n = len(adj)
    degree = [0] * n
    for v in range(n):
        if v not in answer:
            for u in adj[v]:
                if u not in answer:
                    degree[u] += 1

    stack = [v for v in range(n) if v not in answer and degree[v] == 0]
    count = 0
    while stack:
        v = stack.pop()
        count += 1
        for u in adj[v]:
            if u not in answer:
                degree[u] -= 1
                if degree[u] == 0:
                    stack.append(u)
    return count == n - len(answer)


def improve(adj, answer, deadline):
    for v in sorted(answer):
        if stop or time.monotonic() >= deadline:
            break
        answer.remove(v)
        if not is_correct(adj, answer):
            answer.add(v)
    return answer


def main():
    start = time.monotonic()
    signal.signal(signal.SIGTERM, on_sigterm)
    limit = 500
    deadline = time.monotonic() + limit
    n, adj = read_graph()
    answer = greedy(n, adj, deadline)
    answer = improve(adj, answer, deadline)

    sys.stdout.write(''.join(str(v + 1) + '\n' for v in sorted(answer)))
    sys.stdout.flush()

    elapsed = time.monotonic() - start
    print(f"Время работы: {elapsed:.3f} с", file=sys.stderr)
    print(f"Количество удалённых вершин: {len(answer)}", file=sys.stderr)

if __name__ == '__main__':
    main()
