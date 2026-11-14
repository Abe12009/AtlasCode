/**
 * Every `className` value in a source file, as text.
 *
 * Brace-aware on purpose, and shared by the RTL and glass source guards. A
 * className is often `className={cn('a', flag && 'b')}` spanning several
 * lines with nested braces and quotes inside: a `className="[^"]*"` regex
 * matches none of those, and a `{[^}]*}` one stops at the first inner `}`. So
 * walk instead -- quoted values read to their closing quote, braced values to
 * the brace that balances, ignoring braces that sit inside a string.
 */
export function classNameValues(text: string): string[] {
  const out: string[] = [];
  const NEEDLE = 'className=';
  for (let i = text.indexOf(NEEDLE); i !== -1; i = text.indexOf(NEEDLE, i + 1)) {
    const j = i + NEEDLE.length;
    const open = text[j];
    if (open === '"' || open === "'") {
      const end = text.indexOf(open, j + 1);
      if (end !== -1) out.push(text.slice(j + 1, end));
      continue;
    }
    if (open !== '{') continue;
    let depth = 0;
    let quote: string | null = null;
    for (let k = j; k < text.length; k++) {
      const c = text[k];
      if (quote) {
        if (c === quote && text[k - 1] !== '\\') quote = null;
        continue;
      }
      if (c === '"' || c === "'" || c === '`') { quote = c; continue; }
      if (c === '{') depth++;
      else if (c === '}') {
        depth--;
        if (depth === 0) { out.push(text.slice(j + 1, k)); break; }
      }
    }
  }
  return out;
}

/**
 * Every whole class token actually written in a className, as opposed to
 * every word inside the expression.
 *
 * `classNameValues` returns the raw source of the expression, which for a
 * `cn(...)` call can include comments -- and a comment saying "parent card is
 * glass" is not a class. So take only the contents of the string literals
 * inside the expression, then split those on whitespace.
 */
export function classNameTokens(text: string): string[] {
  const tokens: string[] = [];
  for (const value of classNameValues(text)) {
    // A bare quoted className has no inner quotes; a cn(...) expression does.
    const literals = value.match(/'[^']*'|"[^"]*"|`[^`]*`/g) ?? [value];
    for (const literal of literals) {
      for (const token of literal.replace(/^['"`]|['"`]$/g, '').split(/\s+/)) {
        if (token) tokens.push(token);
      }
    }
  }
  return tokens;
}
