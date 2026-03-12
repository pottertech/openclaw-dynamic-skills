import { lookupSkills } from "./client"
import { activateSkills } from "./sync"
import type { PluginConfig } from "./types"

type ToolArgs = Record<string, any>

export default function plugin(ctx: any) {
  const config = (ctx.config || {}) as PluginConfig

  return {
    agentTools: [
      {
        name: "dynamic_skill_search",
        description: "Search the dynamic skill catalog and return the best matching skills.",
        inputSchema: {
          type: "object",
          properties: {
            query: { type: "string" },
            limit: { type: "integer", minimum: 1, maximum: 20 }
          },
          required: ["query"]
        },
        handler: async ({ query, limit = 5 }: ToolArgs) => {
          const results = await lookupSkills(config, query, limit)
          return {
            count: results.length,
            results: results.map((r) => ({
              id: r.id,
              slug: r.slug,
              name: r.name,
              description: r.description,
              category: r.category,
              tags: r.tags || []
            }))
          }
        }
      },
      {
        name: "dynamic_skill_activate",
        description: "Fetch and activate the best matching skills by writing them into a local skill folder.",
        inputSchema: {
          type: "object",
          properties: {
            query: { type: "string" },
            limit: { type: "integer", minimum: 1, maximum: 20 },
            workspaceDir: { type: "string" }
          },
          required: ["query"]
        },
        handler: async ({ query, limit, workspaceDir }: ToolArgs) => {
          const maxActive = config.maxActiveSkills || 12
          const results = await lookupSkills(config, query, Math.min(limit || 5, maxActive))
          const activation = await activateSkills(config, results, workspaceDir)
          return {
            query,
            activated: activation.written,
            root: activation.root,
            count: activation.written.length
          }
        }
      }
    ]
  }
}
