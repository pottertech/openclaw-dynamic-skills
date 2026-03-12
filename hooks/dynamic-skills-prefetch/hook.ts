import fs from "node:fs/promises"
import path from "node:path"

async function ensureDir(dir: string): Promise<void> {
  await fs.mkdir(dir, { recursive: true })
}

function renderSkill(skill: any): string {
  return `---
name: ${skill.slug}
description: ${JSON.stringify(skill.description || "")}
---

# ${skill.title || skill.name}

${(skill.body_markdown || "").trim()}
`
}

export default async function handle(event: any, ctx: any) {
  const config = ctx.config?.plugins?.entries?.["dynamic-skills"] || {}
  const baseUrl = config.baseUrl
  if (!baseUrl) return

  const message = event?.message?.text || event?.input?.text || ""
  const workspaceDir = event?.workspaceDir || ctx.workspaceDir
  if (!message || !workspaceDir) return

  const url = new URL("/lookup", baseUrl)
  url.searchParams.set("q", message)
  url.searchParams.set("type", "hybrid")
  url.searchParams.set("limit", String(config.maxActiveSkills || 6))

  const res = await fetch(url.toString(), {
    headers: config.apiKey ? { Authorization: `Bearer ${config.apiKey}` } : {}
  })
  if (!res.ok) return

  const data = await res.json()
  const results = Array.isArray(data.results) ? data.results : []
  const root = path.join(workspaceDir, "skills", "dynamic")
  await ensureDir(root)

  for (const skill of results) {
    const slug = (skill.slug || skill.name).toLowerCase().replace(/[^a-z0-9._-]+/g, "-")
    const dir = path.join(root, slug)
    await ensureDir(dir)
    await fs.writeFile(path.join(dir, "SKILL.md"), renderSkill(skill), "utf8")
    await fs.writeFile(path.join(dir, ".dynamic-skill.json"), JSON.stringify({
      id: skill.id,
      slug
    }, null, 2), "utf8")
  }
}
