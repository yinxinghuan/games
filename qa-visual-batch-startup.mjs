import http from 'node:http'
import { readFile, stat } from 'node:fs/promises'
import { extname, join, normalize } from 'node:path'
import { createRequire } from 'node:module'

const require = createRequire(import.meta.url)
const { chromium } = require('playwright')

const root = '/Users/yin/code/games'
const projects = ['kinetic-name', 'bokeh-web', 'horizon-drift', 'cloud-loom', 'portrait-current']
const mime = {
  '.html': 'text/html; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.fnt': 'text/plain; charset=utf-8',
  '.txt': 'text/plain; charset=utf-8',
}

const server = http.createServer(async (request, response) => {
  try {
    const url = new URL(request.url, 'http://127.0.0.1')
    const [project, ...rest] = url.pathname.split('/').filter(Boolean)
    if (!projects.includes(project)) throw new Error('not found')
    let relative = rest.join('/') || 'index.html'
    const target = normalize(join(root, project, 'dist', relative))
    const info = await stat(target)
    if (info.isDirectory()) relative = join(relative, 'index.html')
    const body = await readFile(normalize(join(root, project, 'dist', relative)))
    response.writeHead(200, { 'content-type': mime[extname(relative)] || 'application/octet-stream' })
    response.end(body)
  } catch {
    response.writeHead(404)
    response.end('not found')
  }
})

await new Promise((resolve) => server.listen(4199, '127.0.0.1', resolve))
const browser = await chromium.launch({ headless: true })
const results = []

try {
  for (const project of projects) {
    for (const viewport of [{ width: 390, height: 844 }, { width: 320, height: 568 }]) {
      const context = await browser.newContext({ viewport })
      const page = await context.newPage()
      const errors = []
      page.on('console', (message) => {
        if (message.type() === 'error' && /shader|webgl|uncaught|typeerror/i.test(message.text())) errors.push(message.text())
      })
      page.on('pageerror', (error) => errors.push(error.message))
      await page.route('**/*', async (route) => {
        const url = route.request().url()
        if (!url.startsWith('http://127.0.0.1:4199')) return route.abort()
        if (/\.js$|\.(?:fnt|png|jpg)$/.test(url)) {
          await new Promise((resolve) => setTimeout(resolve, 420))
        }
        return route.continue()
      })

      const startedAt = Date.now()
      await page.goto(`http://127.0.0.1:4199/${project}/`, { waitUntil: 'commit' })
      await page.waitForSelector('.boot-bridge', { state: 'visible' })
      const bootVisibleAt = Date.now() - startedAt
      await page.waitForTimeout(150)
      await page.screenshot({ path: join(root, project, '_qa/ui', `${viewport.width}x${viewport.height}-startup-bridge.png`) })

      if (project === 'bokeh-web') {
        await page.waitForFunction(() => !document.querySelector('.boot-bridge'))
        await page.evaluate(() => {
          window.__bokehStartupOrder = []
          const bodyObserver = new MutationObserver(() => {
            if (document.body.dataset.visualReady === 'true') window.__bokehStartupOrder.push('frame-ready')
          })
          bodyObserver.observe(document.body, { attributes: true, attributeFilter: ['data-visual-ready'] })
          const sleeping = document.querySelector('.sleeping')
          const sleepingObserver = new MutationObserver(() => {
            if (sleeping.classList.contains('is-awake')) window.__bokehStartupOrder.push('cover-release')
          })
          sleepingObserver.observe(sleeping, { attributes: true, attributeFilter: ['class'] })
        })
        await page.locator('.wake').click()
        await page.waitForFunction(() => document.body.dataset.visualReady === 'true', null, { timeout: 20000 })
        const startupOrder = await page.evaluate(() => window.__bokehStartupOrder)
        const heldUntilFrame = startupOrder.indexOf('frame-ready') !== -1
          && startupOrder.indexOf('frame-ready') < startupOrder.indexOf('cover-release')
        results.push({ project, viewport: `${viewport.width}x${viewport.height}`, bootVisibleAt, heldUntilFrame, startupOrder, readyAt: Date.now() - startedAt, errors })
      } else {
        await page.waitForFunction(() => document.body.dataset.visualReady === 'true', null, { timeout: 20000 })
        results.push({ project, viewport: `${viewport.width}x${viewport.height}`, bootVisibleAt, readyAt: Date.now() - startedAt, errors })
      }

      await page.waitForFunction(() => !document.querySelector('.boot-bridge'), null, { timeout: 2000 })
      await page.screenshot({ path: join(root, project, '_qa/ui', `${viewport.width}x${viewport.height}-startup-ready.png`) })
      await context.close()
    }
  }
} finally {
  await browser.close()
  server.close()
}

for (const result of results) console.log(JSON.stringify(result))
if (results.some((result) => result.errors.length || result.heldUntilFrame === false)) process.exitCode = 1
