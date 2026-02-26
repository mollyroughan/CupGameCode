from functools import lru_cache
from collections import deque
import json

def moves(state):
    n = len(state)
    for i, k in enumerate(state):
        if k == 0:
            continue
        for d in (-k, k):
            j = i + d
            if 0 <= j < n and state[j] > 0:
                new = list(state)
                new[i] = 0
                new[j] += k
                yield tuple(new)

@lru_cache(None)
def winning(state):
    return any(not winning(nxt) for nxt in moves(state))

def build_graph(n, max_nodes=None):
    start = (1,) * n
    adj = {}
    seen = {start}
    q = deque([start])

    while q:
        s = q.popleft()
        children = list(moves(s))
        adj[s] = children
        for t in children:
            if t not in seen:
                seen.add(t)
                if max_nodes is not None and len(seen) > max_nodes:
                    raise RuntimeError("Graph too big; set a larger max_nodes or smaller n.")
                q.append(t)

    return start, adj

def write_html(start, adj, filename="game.html"):
    import json

    # assign ids
    states = list(adj.keys())
    sid = {s: i for i, s in enumerate(states)}

    nodes = [
        {
            "id": sid[s],
            "state": str(s),
            "wl": ("W" if winning(s) else "L")
        }
        for s in states
    ]

    edges = [
        {"source": sid[s], "target": sid[t]}
        for s, kids in adj.items()
        for t in kids
    ]

    data = {"start": sid[start], "nodes": nodes, "edges": edges}

    html = f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8"/>
  <title>Cup Game Graph</title>
  <style>
    body {{ font-family: system-ui, Arial; margin: 0; }}
    #top {{ padding: 10px 14px; border-bottom: 1px solid #ddd; }}
    #svg {{ width: 100vw; height: calc(100vh - 52px); }}

    .node {{ cursor: pointer; }}
    .label {{
      font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
      font-size: 11px;
      pointer-events: none;
    }}
  </style>
</head>
<body>
<div id="top">
  <b>Click nodes to toggle their outgoing edges</b>
</div>
<svg id="svg"></svg>

<script>
const DATA = {json.dumps(data)};

const svg = document.getElementById("svg");
const W = svg.clientWidth;
const H = svg.clientHeight;

const nodes = new Map(DATA.nodes.map(n => [n.id, n]));
const out = new Map();
for (const e of DATA.edges) {{
  if (!out.has(e.source)) out.set(e.source, []);
  out.get(e.source).push(e.target);
}}

// BFS layering
const depth = new Map([[DATA.start, 0]]);
const q = [DATA.start];

while (q.length) {{
  const u = q.shift();
  const du = depth.get(u);
  for (const v of (out.get(u) || [])) {{
    if (!depth.has(v)) {{
      depth.set(v, du + 1);
      q.push(v);
    }}
  }}
}}

const layers = new Map();
for (const [id, d] of depth.entries()) {{
  if (!layers.has(d)) layers.set(d, []);
  layers.get(d).push(id);
}}

const pos = new Map();
const maxD = Math.max(...layers.keys());

for (let d = 0; d <= maxD; d++) {{
  const layer = layers.get(d) || [];
  const y = 60 + d * 100;
  const spacing = (W - 80) / Math.max(1, layer.length);
  for (let i = 0; i < layer.length; i++) {{
    const x = 40 + i * spacing;
    pos.set(layer[i], {{x, y}});
  }}
}}

let expanded = new Set([DATA.start]);

function clear() {{
  while (svg.firstChild) svg.removeChild(svg.firstChild);
}}

function draw() {{
  clear();

  // Draw edges
  for (const u of expanded) {{
    const pu = pos.get(u);
    for (const v of (out.get(u) || [])) {{
      const pv = pos.get(v);
      if (!pu || !pv) continue;
      const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
      line.setAttribute("x1", pu.x);
      line.setAttribute("y1", pu.y);
      line.setAttribute("x2", pv.x);
      line.setAttribute("y2", pv.y);
      line.setAttribute("stroke", "#aaa");
      svg.appendChild(line);
    }}
  }}

  // Draw nodes
  for (const [id, p] of pos.entries()) {{
    const n = nodes.get(id);
    const g = document.createElementNS("http://www.w3.org/2000/svg", "g");
    g.classList.add("node");

    g.addEventListener("click", () => {{
      if (expanded.has(id)) expanded.delete(id);
      else expanded.add(id);
      draw();
    }});

    const rect = document.createElementNS("http://www.w3.org/2000/svg", "rect");
    rect.setAttribute("x", p.x - 45);
    rect.setAttribute("y", p.y - 20);
    rect.setAttribute("width", 90);
    rect.setAttribute("height", 40);
    rect.setAttribute("rx", 10);
    rect.setAttribute("stroke", "#333");
    rect.setAttribute("stroke-width", (id === DATA.start) ? "3" : "1.5");

    // Color by win/loss
    if (n.wl === "W") {{
      rect.setAttribute("fill", "#d4f8d4");  // light green
    }} else {{
      rect.setAttribute("fill", "#f8d4d4");  // light red
    }}

    g.appendChild(rect);

    const text = document.createElementNS("http://www.w3.org/2000/svg", "text");
    text.setAttribute("x", p.x);
    text.setAttribute("y", p.y + 4);
    text.setAttribute("text-anchor", "middle");
    text.setAttribute("class", "label");
    text.textContent = n.state;
    g.appendChild(text);

    svg.appendChild(g);
  }}
}}

draw();
</script>
</body>
</html>
"""

    with open(filename, "w", encoding="utf-8") as f:
        f.write(html)

    return filename

if __name__ == "__main__":
    n = 5
    start, adj = build_graph(n, max_nodes=20000)
    fn = write_html(start, adj, filename=f"cup_game_n{n}.html")
    print("Wrote", fn, "- open it in your browser.")