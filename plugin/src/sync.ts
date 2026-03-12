import fs from "node:fs/promises"
import path from "node:path"
import os from "node:os"
import type { PluginConfig, SkillResult } from "./types"

function yamlFrontmatter(skill: SkillResult): string {
  const name = skill.slug || skill.name
  const description = (skill.description || "").replace(/\n/g, " ").trim()
  return `---\nname: ${name}\ndescription: ${JSON.stringify(description)}\n---\n`
}

function renderSkillMd(skill: SkillResult): string {
  return [
    yamlFrontmatter(skill),
    "",
    `# ${skill.title || skill.name}`,
    "",
    skill.body_markdown.trim(),
    ""
  ].join("\n")
}

async function ensureDir(dir: string): Promise<void> {
  await fs.mkdir(dir, { recursive: true })
}

export async function getTargetRoot(
  config: PluginConfig,
  workspaceDir?: string
): Promise<string> {
  if (config.workspaceMode === "managed" || !workspaceDir) {
    return config.managedDir || path.join(os.homedir(), ".openclaw", "skills", "dynamic")
  }
  return path.join(workspaceDir, config.workspaceSubdir || "skills/dynamic")
}

export async function activateSkills(
  config: PluginConfig,
  skills: SkillResult[],
  workspaceDir?: string
): Promise<{ root: string; written: string[] }> {
  const root = await getTargetRoot(config, workspaceDir)
  await ensureDir(root)

  const written: string[] = []
  for (const skill of skills) {
    const slug = (skill.slug || skill.name).toLowerCase().replace(/[^a-z0-9._-]+/g, "-")
    const dir = path.join(root, slug)
    await ensureDir(dir)
    await fs.writeFile(path.join(dir, "SKILL.md"), renderSkillMd(skill), "utf8")
    await fs.writeFile(
      path.join(dir, ".dynamic-skill.json"),
      JSON.stringify({
        id: skill.id,
        slug,
        updated_at: skill.updated_at || null
      }, null, 2),
      "utf8"
    )
    written.push(slug)
  }

  return { root, written }
}
