import type { PluginConfig, SkillResult } from "./types"

export async function lookupSkills(
  config: PluginConfig,
  query: string,
  limit: number
): Promise<SkillResult[]> {
  const url = new URL("/lookup", config.baseUrl)
  url.searchParams.set("q", query)
  url.searchParams.set("type", "hybrid")
  url.searchParams.set("limit", String(limit))

  const res = await fetch(url.toString(), {
    headers: config.apiKey ? { Authorization: `Bearer ${config.apiKey}` } : {}
  })

  if (!res.ok) {
    throw new Error(`Lookup failed: ${res.status} ${res.statusText}`)
  }

  const data = await res.json()
  return Array.isArray(data.results) ? data.results : []
}
