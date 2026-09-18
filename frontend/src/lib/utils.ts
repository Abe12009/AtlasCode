import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

/** The backend serializes naive UTC datetimes (SQLAlchemy `DateTime` columns
 * populated via `datetime.utcnow()`, no timezone suffix) -- `new Date(iso)`
 * on a suffix-less ISO string is parsed as LOCAL time by the JS spec, which
 * would silently shift anything computed from it (a countdown, an "expires
 * in") by the viewer's UTC offset. Append 'Z' only when the string doesn't
 * already carry a zone designator, so an already-correct value is untouched. */
export function parseUtcDate(iso: string): Date {
  return new Date(/[zZ]|[+-]\d\d:\d\d$/.test(iso) ? iso : `${iso}Z`);
}