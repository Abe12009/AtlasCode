import { describe, it, expect } from 'vitest';
import { NODES, project } from '../HeroGraph';

/** The projection is the only non-trivial maths in the hero graph: get the
 * perspective divide backwards and the sphere renders inside-out, which looks
 * plausible enough in a screenshot to ship unnoticed. */
describe('HeroGraph projection', () => {
  it('spreads every node on the unit sphere', () => {
    expect(NODES).toHaveLength(54);
    for (const n of NODES) {
      expect(Math.hypot(n.x, n.y, n.z)).toBeCloseTo(1, 5);
    }
  });

  it('scales nodes nearer the camera up and further ones down', () => {
    const near = project({ x: 0, y: 0, z: -1, done: false }, 400, 400, 100, 0, 0);
    const far = project({ x: 0, y: 0, z: 1, done: false }, 400, 400, 100, 0, 0);
    expect(near.k).toBeGreaterThan(1);
    expect(far.k).toBeLessThan(1);
    expect(near.k).toBeGreaterThan(far.k);
    // On the view axis, both stay dead centre however much they scale.
    expect(near.X).toBeCloseTo(200);
    expect(near.Y).toBeCloseTo(200);
    expect(far.X).toBeCloseTo(200);
  });

  it('rotates a side node away from the camera after a quarter turn', () => {
    const node = { x: 1, y: 0, z: 0, done: false };
    const front = project(node, 400, 400, 100, 0, 0);
    const turned = project(node, 400, 400, 100, Math.PI / 2, 0);
    expect(front.X).toBeCloseTo(300);
    expect(turned.X).toBeCloseTo(200);
    expect(turned.z).toBeGreaterThan(front.z);
  });
});
