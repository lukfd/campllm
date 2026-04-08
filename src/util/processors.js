import os from "node:os"

const MIN_CONCURRENCY = 2
const MAX_CONCURRENCY = 16

export class Processors {
    constructor(items = [], options = {}) {
        this.items = Array.isArray(items) ? items : []
        this.concurrency = options.concurrency ?? Processors.defaultConcurrency()
    }

    static defaultConcurrency() {
        const cpuCount = os.cpus()?.length ?? MIN_CONCURRENCY
        const suggested = cpuCount * 2
        return Math.min(MAX_CONCURRENCY, Math.max(MIN_CONCURRENCY, suggested))
    }

    async run(functionToRun) {
        if (typeof functionToRun !== 'function') {
            throw new TypeError('processors.run expects a function')
        }

        if (this.items.length === 0) {
            return []
        }

        const results = new Array(this.items.length)
        const workerCount = Math.min(this.concurrency, this.items.length)
        let cursor = 0

        const worker = async () => {
            while (cursor < this.items.length) {
                const index = cursor
                cursor += 1
                results[index] = await functionToRun(this.items[index], index)
            }
        }

        await Promise.all(Array.from({ length: workerCount }, worker))
        return results
    }
}