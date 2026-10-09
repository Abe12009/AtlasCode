import { describe, it, expect } from 'vitest';
import { normaliseGraph, fallbackPosition } from '../visualGraph';

/**
 * Regression cover for the Visual Programming white-screen.
 *
 * Seeded exercises 15 and 20 carry nodes with no `position`; the editor read
 * `node.position.x` while rendering edges and threw, blanking the page.
 */
describe('normaliseGraph', () => {
  // Exactly the payload exercise 15 serves.
  const seeded15 = {
    nodes: [
      { id: '1', type: 'start', config: {} },
      { id: '2', type: 'loop', config: { var: 'i', times: '5' } },
      { id: '3', type: 'output', config: { value: 'i' } },
      { id: '4', type: 'end', config: {} },
    ],
    edges: [
      { source: '1', target: '2' },
      { source: '2', target: '3' },
      { source: '3', target: '4' },
    ],
  };

  it('gives every position-less node a usable position', () => {
    const { nodes } = normaliseGraph(seeded15);
    expect(nodes).toHaveLength(4);
    for (const n of nodes) {
      expect(Number.isFinite(n.position.x), `${n.id}.x`).toBe(true);
      expect(Number.isFinite(n.position.y), `${n.id}.y`).toBe(true);
    }
  });

  it('cascades rather than piling every node at the origin', () => {
    const { nodes } = normaliseGraph(seeded15);
    const seen = new Set(nodes.map((n) => `${n.position.x},${n.position.y}`));
    expect(seen.size, 'positions must be distinct').toBe(nodes.length);
    expect(nodes[0].position).toEqual(fallbackPosition(0));
  });

  it('keeps a position that is already valid', () => {
    const { nodes } = normaliseGraph({
      nodes: [{ id: '1', type: 'start', position: { x: 42, y: 99 }, config: {} }],
      edges: [],
    });
    expect(nodes[0].position).toEqual({ x: 42, y: 99 });
  });

  it.each([
    ['missing', undefined],
    ['null', null],
    ['not an object', 'nope'],
    ['partial', { x: 10 }],
    ['non-numeric', { x: 'a', y: 'b' }],
    ['NaN', { x: NaN, y: 0 }],
    ['Infinity', { x: Infinity, y: 0 }],
  ])('replaces a %s position', (_label, position) => {
    const { nodes } = normaliseGraph({ nodes: [{ id: '1', type: 'start', position, config: {} }], edges: [] });
    expect(Number.isFinite(nodes[0].position.x)).toBe(true);
    expect(Number.isFinite(nodes[0].position.y)).toBe(true);
  });

  it('drops edges whose endpoints do not exist', () => {
    const { edges } = normaliseGraph({
      nodes: [{ id: '1', type: 'start', config: {} }, { id: '2', type: 'end', config: {} }],
      edges: [
        { source: '1', target: '2' },      // keep
        { source: '1', target: 'ghost' },  // orphan target
        { source: 'ghost', target: '2' },  // orphan source
      ],
    });
    expect(edges).toHaveLength(1);
    expect(edges[0]).toMatchObject({ source: '1', target: '2' });
  });

  it('gives every edge an id, since the renderer keys on it', () => {
    const { edges } = normaliseGraph(seeded15);
    expect(edges).toHaveLength(3);
    const ids = edges.map((e) => e.id);
    expect(ids.every((id) => typeof id === 'string' && id.length > 0)).toBe(true);
    expect(new Set(ids).size, 'ids must be unique').toBe(ids.length);
  });

  it('drops nodes without a usable id, because edges reference it', () => {
    const { nodes } = normaliseGraph({
      nodes: [{ id: '1', type: 'start', config: {} }, { type: 'end', config: {} }, { id: '', type: 'end' }],
      edges: [],
    });
    expect(nodes.map((n) => n.id)).toEqual(['1']);
  });

  it.each([
    ['null', null],
    ['undefined', undefined],
    ['a string', 'not a graph'],
    ['an empty object', {}],
    ['nodes of the wrong type', { nodes: 'x', edges: 7 }],
    ['entries that are not objects', { nodes: [null, 3, 'a'], edges: [null] }],
  ])('returns an empty graph for %s rather than throwing', (_label, input) => {
    expect(() => normaliseGraph(input)).not.toThrow();
    expect(normaliseGraph(input)).toEqual({ nodes: [], edges: [] });
  });

  it('coerces non-string config values instead of dropping them', () => {
    const { nodes } = normaliseGraph({
      nodes: [{ id: '1', type: 'loop', config: { times: 5, on: true } }],
      edges: [],
    });
    expect(nodes[0].config).toEqual({ times: '5', on: 'true' });
  });
});
