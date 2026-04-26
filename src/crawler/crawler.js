import puppeteer from "puppeteer"
import { dnrWebsite, parkSectionIds, stateParkList } from "../util/rubric.js"
import { Processors } from "../util/processors.js"

const CHROME_PATH = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'

export class Crawler {
    constructor(chromePath = CHROME_PATH) {
        this.chromePath = chromePath
    }

    async launchBrowser(chromePath) {
        try {
            return await puppeteer.launch({
                executablePath: chromePath,
                headless: true
            })
        } catch (error) {
            console.warn(`Failed to launch Chrome at ${chromePath}, falling back to bundled Chromium.`)
            console.warn(error instanceof Error ? error.message : String(error))
            return puppeteer.launch({ headless: true })
        }
    }

    async visitDnrWebsite() {
        let browser = await this.launchBrowser(this.chromePath)
        let page = await browser.newPage()

        await page.goto(dnrWebsite)

        const title = await page.title()
        console.log('The title of this blog post is "%s".', title)

        await browser.close()
    }

    async getStateParkList() {
        let browser = await this.launchBrowser(this.chromePath)
        let page = await browser.newPage()

        try {
            await page.goto(stateParkList, { waitUntil: 'domcontentloaded' })

            const parks = await page.evaluate(() => {
                const buildParkUrl = (id) => `https://www.dnr.state.mn.us/state_parks/park.html?id=${encodeURIComponent(id)}#homepage`

                const uniqueByUrl = (rows) => {
                    const seen = new Set()
                    return rows.filter((row) => {
                        if (!row.url || seen.has(row.url)) {
                            return false
                        }
                        seen.add(row.url)
                        return true
                    })
                }

                const fromReservationData = Array.isArray(globalThis.reservation_data)
                    ? globalThis.reservation_data
                        .map((item) => ({
                            name: typeof item?.name === 'string' ? item.name.trim() : '',
                            url: typeof item?.brem === 'string' ? buildParkUrl(item.brem) : '',
                        }))
                        .filter((park) => park.name.length > 0 && park.url.length > 0)
                    : []

                if (fromReservationData.length > 0) {
                    return uniqueByUrl(fromReservationData)
                }

                const fromShowPark = Array.from(document.querySelectorAll('script'))
                    .map((script) => script.textContent ?? '')
                    .flatMap((scriptText) => {
                        const matches = Array.from(
                            scriptText.matchAll(/show_park\(\s*['"]([^'"]+)['"]\s*,\s*['"]((?:\\.|[^'"])*)['"]\s*\)/g)
                        )

                        return matches.map(([, id, name]) => ({
                            name: name.trim(),
                            url: buildParkUrl(id),
                        }))
                    })
                    .filter((park) => park.name.length > 0)

                if (fromShowPark.length > 0) {
                    return uniqueByUrl(fromShowPark)
                }

                // Fallback if the inline show_park scripts are not present.
                return uniqueByUrl(Array.from(document.querySelectorAll('a[href*="/state_parks/park.html?id="]'))
                    .map((anchor) => ({
                        name: anchor.textContent?.trim() ?? '',
                        url: anchor.href,
                    }))
                    .filter((park) => park.name.length > 0))
            })

            console.log(`Found ${parks.length} parks/recreation areas`)
            return parks
        } finally {
            await browser.close()
        }
    }

    async collectDnrData(parks) {
        if (!Array.isArray(parks) || parks.length === 0) {
            return []
        }

        const browser = await this.launchBrowser(this.chromePath)
        const tasks = parks.flatMap((park) =>
            parkSectionIds.map((sectionId) => {
                const url = new URL(park.url)
                url.hash = sectionId

                return {
                    parkName: park.name,
                    parkUrl: park.url,
                    sectionId,
                    sectionUrl: url.toString(),
                }
            })
        )

        const processors = new Processors(tasks)

        try {
            return await processors.run(async (task, index) => {
                const page = await browser.newPage()
                const total = tasks.length

                try {
                    page.setDefaultNavigationTimeout(45000)

                    let collected = null
                    let lastError = null

                    for (let attempt = 1; attempt <= 3; attempt += 1) {
                        try {
                            await page.goto(task.sectionUrl, { waitUntil: 'networkidle2' })

                            await page.waitForSelector('#park, #main_page_content, main, article', { timeout: 15000 })

                            await page
                                .waitForFunction(() => {
                                    const normalize = (text) => (text ?? '').replace(/\s+/g, ' ').trim()
                                    const park = document.querySelector('#park')
                                    const text = normalize(park?.textContent)

                                    if (!text || text.length < 120) {
                                        return false
                                    }

                                    // Skip obvious unrendered/template payloads.
                                    if (text.includes('var reservation_data') || text.includes('<%=')) {
                                        return false
                                    }

                                    return true
                                }, { timeout: 10000 })
                                .catch(() => {
                                    // Some pages may not fully hydrate; fallback extraction still runs below.
                                })

                            const pageData = await page.evaluate((sectionId) => {
                                const normalize = (text) => (text ?? '').replace(/\s+/g, ' ').trim()

                                const normalizedHash = (value) => {
                                    if (value == null) {
                                        return ''
                                    }

                                    const text = String(value).trim()

                                    if (!text) {
                                        return ''
                                    }

                                    if (text.startsWith('#')) {
                                        return text.replace(/^#/, '').trim().toLowerCase()
                                    }

                                    // For raw IDs like "alerts", return the value directly.
                                    if (!text.includes('/')) {
                                        return text.toLowerCase()
                                    }

                                    const hashOnly = (() => {
                                        try {
                                            return new URL(text, window.location.href).hash
                                        } catch {
                                            return ''
                                        }
                                    })()

                                    return hashOnly.replace(/^#/, '').trim().toLowerCase()
                                }

                                const cleanNodeText = (node) => {
                                    if (!node) {
                                        return ''
                                    }

                                    const clone = node.cloneNode(true)
                                    clone
                                        .querySelectorAll('script,style,noscript,template')
                                        .forEach((el) => el.remove())

                                    return normalize(clone.textContent)
                                }

                                const parkRoot = document.querySelector('#park')
                                const mainRoot = document.querySelector('#main_page_content, main, article') ?? document.body

                                const primaryRoot =
                                    document.getElementById(sectionId) ??
                                    parkRoot?.querySelector(`[id="${sectionId}"]`) ??
                                    document.querySelector(`[data-anchor="${sectionId}"]`) ??
                                    document.querySelector(`a[name="${sectionId}"]`)?.closest('section,article,div')

                                const root = primaryRoot ?? parkRoot ?? mainRoot
                                const sectionText = cleanNodeText(root)
                                const pageHeading = normalize(document.querySelector('#title h1, h1')?.textContent)
                                const sectionHeading = normalize(root?.querySelector('h2,h3,h4')?.textContent)

                                const requestedHash = normalizedHash(sectionId)
                                const locationHash = normalizedHash(window.location.hash)
                                const activeNavHash = Array.from(document.querySelectorAll('a.navlinkactive[href], a.active[href], [aria-current="page"][href]'))
                                    .map((link) => normalizedHash(link.getAttribute('href') ?? ''))
                                    .find(Boolean)

                                // DNR pages mark the active section with navlinkactive instead of section container IDs.
                                const sectionFound = Boolean(primaryRoot) ||
                                    (requestedHash.length > 0 && activeNavHash === requestedHash) ||
                                    (requestedHash.length > 0 && locationHash === requestedHash && sectionHeading.length > 0)

                                const hasTemplateLeak =
                                    sectionText.includes('var reservation_data') ||
                                    sectionText.includes('<%=') ||
                                    sectionText.includes('function getArgs()')

                                return {
                                    pageHeading,
                                    sectionHeading,
                                    sectionText,
                                    sectionFound,
                                    templateLeak: hasTemplateLeak,
                                }
                            }, task.sectionId)

                            collected = {
                                ...task,
                                finalUrl: page.url(),
                                pageTitle: await page.title(),
                                pageHeading: pageData.pageHeading,
                                sectionHeading: pageData.sectionHeading,
                                sectionText: pageData.sectionText,
                                sectionFound: pageData.sectionFound,
                                fetchedAt: new Date().toISOString(),
                            }
                            break
                        } catch (error) {
                            lastError = error

                            if (attempt < 3) {
                                await new Promise((resolve) => setTimeout(resolve, attempt * 750))
                            }
                        }
                    }

                    if (!collected) {
                        throw (lastError ?? new Error('Failed to collect section data'))
                    }

                    console.log(`[${index + 1}/${total}] Collected ${task.parkName}#${task.sectionId}`)
                    return collected
                } catch (error) {
                    console.warn(`[${index + 1}/${total}] Failed ${task.parkName}#${task.sectionId}`)
                    return {
                        ...task,
                        error: error instanceof Error ? error.message : String(error),
                        fetchedAt: new Date().toISOString(),
                    }
                } finally {
                    await page.close()
                }
            })
        } finally {
            await browser.close()
        }
    }
}
