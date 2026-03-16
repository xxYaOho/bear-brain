export const BearBrainDailyPlugin = async ({ $, worktree }) => {
  let sawWork = false

  const getCommand = (event) => {
    const payload = event?.properties ?? event?.payload ?? event ?? {}
    return String(payload.command ?? payload.name ?? "")
  }

  const appendDaily = async () => {
    sawWork = false
    await $`uv run python memory_worker.py append-daily --project-root ${worktree} --did ${"完成一轮 OpenCode 工作"} --found ${"本轮发生了实际工具调用或文件变更"} --judgment ${"需要继续按 daily -> promote-memory 闭环沉淀"}`
  }

  return {
    event: async ({ event }) => {
      if (event.type === "tool.execute.after" || event.type === "file.edited" || event.type === "todo.updated") {
        sawWork = true
      }

      if (event.type === "tui.command.execute" && getCommand(event) === "/compact") {
        await appendDaily()
        return
      }

      if (event.type !== "session.idle" || !sawWork) {
        return
      }

      await appendDaily()
    },
  }
}
