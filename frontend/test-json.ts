import * as fs from 'fs';

const en = JSON.parse(fs.readFileSync('./src/locales/en.json', 'utf-8'));

console.log('en.common.preferred_language:', en.common?.preferred_language);
console.log('en.auth.preferred_language:', en.auth?.preferred_language);
console.log('en.common keys:', Object.keys(en.common || {}).length);
console.log('Has preferred_language in common:', 'preferred_language' in (en.common || {}));