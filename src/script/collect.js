import { parseArgs } from 'node:util'
import { writeFile } from 'node:fs/promises'
import { Crawler } from '../crawler/crawler.js'

const args = process.argv.slice(2)
const options = {
  'chrome-path': {
    type: 'string',
    short: 'c',
  },
  collect: {
    type: 'boolean',
    short: 'd',
  },
  help: {
    type: 'boolean',
    short: 'h',
  },
  output: {
    type: 'string',
    short: 'o',
  },
}

const { values } = parseArgs({ args, options, allowPositionals: false })

if (values.help) {
  console.log('Usage: node ./src/script/collect.js [-c|--chrome-path <path>] [-d|--collect] [-o|--output <file>]')
  process.exit(0)
}

const c = new Crawler(values['chrome-path'])
const parks = await c.getStateParkList()

const toJsonl = (rows) => `${rows.map((row) => JSON.stringify(row)).join('\n')}\n`

if (values.collect) {
  const records = await c.collectDnrData(parks)

  if (values.output) {
    await writeFile(values.output, toJsonl(records), 'utf-8')
    console.log(`Saved ${records.length} JSONL records to ${values.output}`)
  } else {
    console.log(`Collected ${records.length} records. Pass -o <file>.jsonl to save.`)
  }
} else if (values.output) {
  await writeFile(values.output, `${JSON.stringify(parks, null, 2)}\n`, 'utf-8')
  console.log(`Saved ${parks.length} entries to ${values.output}`)
}

