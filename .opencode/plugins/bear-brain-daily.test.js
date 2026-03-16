import { describe, expect, test } from "bun:test"

import { BearBrainDailyPlugin } from "./bear-brain-daily.js"

describe("BearBrainDailyPlugin", () => {
  test("writes daily when session.compact command executes", async () => {
    const calls = []
    const fakeShell = async (strings, ...values) => {
      calls.push({ strings: [...strings], values })
      return { exitCode: 0 }
    }

    const plugin = await BearBrainDailyPlugin({
      $: fakeShell,
      worktree: "/tmp/bear-brain",
    })

    await plugin.event({
      event: {
        type: "tui.command.execute",
        properties: { command: "session.compact" },
      },
    })

    expect(calls).toHaveLength(1)
    expect(calls[0].strings.join(" ")).toContain("append-daily")
    expect(calls[0].values[0]).toBe("/tmp/bear-brain")
  })
})
