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
    G = []
    for line in lines[1:n + 1]:
        G.append([int(x) - 1 for x in line.split()])
    return n, G


def whal_v(n, G, deadline):
   
    out_e = []
    for ng in G:
        out_e.append(set(ng))

    in_e = [set() for _ in range(n)]

    for v in range(n):
        for u in out_e[v]:
            in_e[u].add(v)

    cur_G = set(range(n))
    answer = set()
    pot_v = list(range(n))

    while cur_G and not stop and time.monotonic() < deadline:
        if pot_v:
            v = pot_v.pop()

            if v not in cur_G:
                continue

            take_in_ans = v in out_e[v]

            if not take_in_ans:
                incoming_count = len(in_e[v])
                outgoing_count = len(out_e[v])

                if incoming_count > 1 and outgoing_count > 1:
                    continue
        else:
            best_score = -1

            for u in cur_G:
                incoming_count = len(in_e[u])
                outgoing_count = len(out_e[u])
                score = incoming_count * outgoing_count

                if score > best_score:
                    best_score = score
                    v = u

            take_in_ans = True

        before = list(in_e[v])
        after = list(out_e[v])
        cur_G.remove(v)

        for u in before:
            out_e[u].discard(v)

        for u in after:
            in_e[u].discard(v)

        out_e[v] = set()
        in_e[v] = set()

        if take_in_ans:
            answer.add(v)
        else:
            for u in before:
                for w in after:
                    out_e[u].add(w)
                    in_e[w].add(u)

        pot_v.extend(before)
        pot_v.extend(after)

    answer.update(cur_G)
    return answer


def khan(G, answer):
    n = len(G)

    in_count = [0] * n

    for v in range(n):
        if v in answer:
            continue

        for u in G[v]:
            if u not in answer:
                in_count[u] += 1
    in_deg0 = []

    for v in range(n):
        if v in answer:
            continue

        if in_count[v] == 0:
            in_deg0.append(v)

    pro_count = 0

    while len(in_deg0) > 0:
        v = in_deg0.pop()
        pro_count += 1

        for u in G[v]:
            if u in answer:
                continue

            in_count[u] -= 1
            
            if in_count[u] == 0:
                in_deg0.append(u)

    rest = n - len(answer)

    if pro_count == rest:
        return True
    else:
        return False




def improve(G, answer, deadline):
    for v in sorted(answer):
        if stop or time.monotonic() >= deadline:
            break
        answer.remove(v)
        if not khan(G, answer):
            answer.add(v)
    return answer


def main():
    start = time.monotonic()
    signal.signal(signal.SIGTERM, on_sigterm)
    limit = 590
    deadline = time.monotonic() + limit
    n, G = read_graph()
    answer = whal_v(n, G, deadline)
    answer = improve(G, answer, deadline)

    sys.stdout.write(''.join(str(v + 1) + '\n' for v in sorted(answer)))
    sys.stdout.flush()

    elapsed = time.monotonic() - start
    #print(f"Время работы: {elapsed:.3f} с", file=sys.stderr)
    #print(f"Количество удалённых вершин: {len(answer)}", file=sys.stderr)

if __name__ == '__main__':
    main()
