/**
 * Today's date in the READER's time zone, as YYYY-MM-DD.
 *
 * `new Date().toISOString().slice(0, 10)` is today in UTC: for a US reader
 * after about 19:00 that is tomorrow, for a Turkish reader between midnight
 * and 03:00 it is yesterday — so a purchase made "today" was dated wrong and
 * the "bought today" label missed. 'en-CA' formats as YYYY-MM-DD.
 */
export function localToday(now = new Date()) {
  return now.toLocaleDateString('en-CA')
}
