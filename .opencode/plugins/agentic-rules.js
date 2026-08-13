/**
 * agentic-rules plugin for OpenCode.
 *
 * Registers skills/ via config.skills.paths, and does nothing else.
 *
 * No message transform hook: the rules that apply at all times are delivered by
 * the AGENTS.md that ba0918-scaffold generates in the consuming project. A
 * second delivery path through session injection would make it undecidable,
 * from the project side, which copy of a rule is in effect.
 */

import path from "path"
import { fileURLToPath } from "url"

const PACKAGE_ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..")
const SKILLS_DIR = path.join(PACKAGE_ROOT, "skills")

const AgenticRulesPlugin = async () => {
  return {
    config: async (config) => {
      config.skills = config.skills || {}
      config.skills.paths = config.skills.paths || []
      if (!config.skills.paths.includes(SKILLS_DIR)) {
        config.skills.paths.push(SKILLS_DIR)
      }
    },
  }
}

// OpenCode treats every module export as a plugin, so the plugin function is
// this module's only export.
export default AgenticRulesPlugin
