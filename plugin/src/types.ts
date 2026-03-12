export type SkillResult = {
  id: string
  slug: string
  name: string
  title?: string
  description?: string
  category?: string
  tags?: string[]
  yaml_frontmatter?: Record<string, unknown>
  body_markdown: string
  updated_at?: string
}

export type PluginConfig = {
  baseUrl: string
  apiKey?: string
  workspaceMode?: "workspace" | "managed"
  managedDir?: string
  workspaceSubdir?: string
  maxActiveSkills?: number
}
