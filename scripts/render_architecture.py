"""Render the checked-in architecture SVG without external diagram dependencies."""
from pathlib import Path
from xml.sax.saxutils import escape
root=Path(__file__).resolve().parents[1]
boxes=[(50,100,'Operator console','web/index.html + app.js'),(390,100,'Control plane','Auth · policy · review gates'),(730,100,'Persistent evidence','SQLite · events · artifacts'),(50,290,'Execution bridge','External Docker harness'),(390,290,'Factory snapshots','Repository · budget · gates'),(730,290,'Evaluation datasets','Trusted labels required'),(50,480,'Native C++ planner','Placement + bounded scaling'),(390,480,'Continuous evaluator','Paired holdout · regression gates'),(730,480,'Reviewable reports','Hash-addressed · no auto-promotion')]
parts=['<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="760" viewBox="0 0 1080 760" role="img" aria-labelledby="title desc">','<title id="title">Ont software factory architecture</title><desc id="desc">Implemented console, control plane, storage, execution bridge, configuration, and evaluation loop with planned adapters.</desc>','<rect width="1080" height="760" fill="#101c1b"/><style>text{font-family:Arial,sans-serif}.heading{font-size:28px;fill:#fff}.label{font-size:18px;fill:#effaf5}.sub{font-size:13px;fill:#abc9bf}</style>','<text x="50" y="50" class="heading">Ont · software factory architecture</text>']
for x1,y1,x2,y2 in [(330,155,390,155),(670,155,730,155),(190,290,190,210),(530,210,530,290),(870,210,870,290),(870,400,870,480),(330,535,390,535),(670,535,730,535)]:
    parts.append(f'<path d="M{x1} {y1} L{x2} {y2}" stroke="#55bda2" stroke-width="2"/>')
for x,y,title,sub in boxes:
    parts.append(f'<rect x="{x}" y="{y}" width="280" height="110" rx="12" fill="#193730" stroke="#397e6d"/><text x="{x+18}" y="{y+40}" class="label">{escape(title)}</text><text x="{x+18}" y="{y+72}" class="sub">{escape(sub)}</text>')
parts.append('<rect x="50" y="650" width="960" height="70" rx="10" fill="none" stroke="#55bda2" stroke-dasharray="7 5"/><text x="70" y="680" class="label">Planned adapter boundary</text><text x="70" y="704" class="sub">GitHub App · MCP · scoped memory · inference gateway · durable cloud orchestration</text></svg>')
(root/'docs/assets/ont-architecture.svg').write_text(''.join(parts))
