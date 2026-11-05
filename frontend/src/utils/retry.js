/**
 * Run an async loader again when it fails, with a short growing pause.
 *
 * Written for the locale chunks: on a phone a single dropped request for
 * tr.json used to leave the whole app showing raw keys ("common.start")
 * until the reader closed it. A second attempt a moment later almost always
 * succeeds, so the cheap retry comes before anything drastic.
 */
export async function withRetry(load, { tries = 3, delayMs = 400, wait = ms => new Promise(r => setTimeout(r, ms)) } = {}) {
  let lastError
  for (let attempt = 0; attempt < tries; attempt++) {
    try {
      return await load()
    } catch (error) {
      lastError = error
      if (attempt < tries - 1) await wait(delayMs * (attempt + 1))
    }
  }
  throw lastError
}
