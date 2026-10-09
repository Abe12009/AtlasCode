/**
 * Normalises a visual-programming graph as it arrives from the API.
 *
 * The editor's `Node` type declares `position: {x, y}` as required, but the
 * graph is untrusted JSON from `starter_code` -- the type describes what the
 * editor needs, not what the wire actually carries, and TypeScript cannot
 * check the difference. Seeded exercises 15 and 20 ship nodes with no
 * `position` at all, which made the edge layer throw
 * `Cannot read properties of undefined (reading 'x')` at render and blanked
 * the whole page.
 *
 * So the graph is normalised once on ingest rather than defended at each of
 * the four places that read `.position`: one place to be correct, and any
 * malformed graph -- seeded, authored later, or hand-posted -- renders instead
 * of white-screening.
 */

export interface GraphNode {
  id: string;
  type: string;
  position: { x: number; y: number };
  config: Record<string, string>;
}

export interface GraphEdge {
  id: string;
  source: string;
  target: string;
  sourceHandle?: string;
  targetHandle?: string;
}

export interface NormalisedGraph {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

/** Layout for nodes that arrive without a usable position. */
const COLUMNS = 3;
const ORIGIN_X = 80;
const ORIGIN_Y = 80;
const STEP_X = 220;
const STEP_Y = 120;

/** A cascade rather than a pile: stacking everything at 0,0 renders but is unusable. */
export function fallbackPosition(index: number): { x: number; y: number } {
  return {
    x: ORIGIN_X + (index % COLUMNS) * STEP_X,
    y: ORIGIN_Y + Math.floor(index / COLUMNS) * STEP_Y,
  };
}

const isFiniteNumber = (v: unknown): v is number => typeof v === 'number' && Number.isFinite(v);

/** True only for a position the editor can actually do arithmetic on. */
function usablePosition(value: unknown): value is { x: number; y: number } {
  if (typeof value !== 'object' || value === null) return false;
  const p = value as { x?: unknown; y?: unknown };
  return isFiniteNumber(p.x) && isFiniteNumber(p.y);
}

function normaliseConfig(value: unknown): Record<string, string> {
  if (typeof value !== 'object' || value === null) return {};
  const out: Record<string, string> = {};
  for (const [k, v] of Object.entries(value as Record<string, unknown>)) {
    out[k] = typeof v === 'string' ? v : String(v);
  }
  return out;
}

/**
 * Coerce an arbitrary parsed `starter_code` payload into a graph the editor
 * can render. Never throws: anything unrecognisable yields an empty graph,
 * which is the same thing the API already returns for unparseable JSON.
 */
export function normaliseGraph(raw: unknown): NormalisedGraph {
  if (typeof raw !== 'object' || raw === null) return { nodes: [], edges: [] };
  const source = raw as { nodes?: unknown; edges?: unknown };

  const rawNodes = Array.isArray(source.nodes) ? source.nodes : [];
  const nodes: GraphNode[] = [];
  rawNodes.forEach((entry, index) => {
    if (typeof entry !== 'object' || entry === null) return;
    const n = entry as Record<string, unknown>;
    // An id is the one thing that cannot be invented: edges reference it.
    if (typeof n.id !== 'string' || n.id === '') return;
    nodes.push({
      id: n.id,
      type: typeof n.type === 'string' ? n.type : 'start',
      position: usablePosition(n.position) ? { x: n.position.x, y: n.position.y } : fallbackPosition(index),
      config: normaliseConfig(n.config),
    });
  });

  const ids = new Set(nodes.map((n) => n.id));
  const rawEdges = Array.isArray(source.edges) ? source.edges : [];
  const edges: GraphEdge[] = [];
  rawEdges.forEach((entry, index) => {
    if (typeof entry !== 'object' || entry === null) return;
    const e = entry as Record<string, unknown>;
    if (typeof e.source !== 'string' || typeof e.target !== 'string') return;
    // Drop orphans: getHandlePosition is only called once both ends resolve,
    // and a dangling edge would otherwise render as a line to nowhere.
    if (!ids.has(e.source) || !ids.has(e.target)) return;
    edges.push({
      // Seeded edges carry only source/target; the renderer keys on id.
      id: typeof e.id === 'string' && e.id !== '' ? e.id : `edge-${e.source}-${e.target}-${index}`,
      source: e.source,
      target: e.target,
      ...(typeof e.sourceHandle === 'string' ? { sourceHandle: e.sourceHandle } : {}),
      ...(typeof e.targetHandle === 'string' ? { targetHandle: e.targetHandle } : {}),
    });
  });

  return { nodes, edges };
}
