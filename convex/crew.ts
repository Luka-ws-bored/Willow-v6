import { internalAction, internalMutation, internalQuery, mutation, query } from "./_generated/server";
import { v } from "convex/values";
import { internal } from "./_generated/api";

export const launchTask = mutation({
  args: {
    crewId: v.string(),
    taskDescription: v.string(),
  },
  handler: async (ctx, args) => {
    const taskId = await ctx.db.insert("crewTasks", {
      crewId: args.crewId,
      taskDescription: args.taskDescription,
      status: "running",
      createdAt: Date.now(),
    });

    // Schedule the crew task execution
    await ctx.scheduler.runAfter(0, internal.crew.executeTask, {
      taskId,
    });

    return taskId;
  },
});

export const executeTask = internalAction({
  args: {
    taskId: v.id("crewTasks"),
  },
  handler: async (ctx, args) => {
    try {
      const task = await ctx.runQuery(internal.crew.getTask, { taskId: args.taskId });
      if (!task) {
        throw new Error("Task not found");
      }

      // Simulate CrewAI execution
      const result = await simulateCrewExecution(task.crewId, task.taskDescription);

      // Update task with result
      await ctx.runMutation(internal.crew.updateTaskResult, {
        taskId: args.taskId,
        status: "completed",
        result,
      });

    } catch (error) {
      console.error("Crew task execution error:", error);
      
      await ctx.runMutation(internal.crew.updateTaskResult, {
        taskId: args.taskId,
        status: "failed",
        error: error instanceof Error ? error.message : "Unknown error",
      });
    }
  },
});

export const getTask = internalQuery({
  args: { taskId: v.id("crewTasks") },
  handler: async (ctx, args) => {
    return await ctx.db.get(args.taskId);
  },
});

export const updateTaskResult = internalMutation({
  args: {
    taskId: v.id("crewTasks"),
    status: v.string(),
    result: v.optional(v.string()),
    error: v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    await ctx.db.patch(args.taskId, {
      status: args.status,
      result: args.result,
      error: args.error,
      completedAt: Date.now(),
    });
  },
});

export const getActiveTasks = query({
  args: {},
  handler: async (ctx) => {
    const tasks = await ctx.db
      .query("crewTasks")
      .withIndex("by_status", (q) => q.eq("status", "running"))
      .order("desc")
      .take(10);

    return tasks;
  },
});

// Simulate CrewAI execution
async function simulateCrewExecution(crewId: string, taskDescription: string): Promise<string> {
  // Simulate processing time
  await new Promise(resolve => setTimeout(resolve, 2000));

  const crewResults = {
    'document-analysis': `## Document Analysis Results

**Task:** ${taskDescription}

**Crew Execution Summary:**
- **Researcher Agent:** Identified key themes and patterns in uploaded documents
- **Analyst Agent:** Performed deep analysis and extracted insights
- **Summarizer Agent:** Created comprehensive summary with actionable recommendations

**Key Findings:**
1. Document structure analysis completed
2. Content themes identified and categorized
3. Recommendations generated based on analysis

**Next Steps:**
- Review findings with stakeholders
- Implement recommended actions
- Monitor progress and outcomes`,

    'content-generation': `## Content Generation Results

**Task:** ${taskDescription}

**Crew Execution Summary:**
- **Writer Agent:** Generated initial content draft based on requirements
- **Editor Agent:** Refined content for clarity and engagement
- **Reviewer Agent:** Performed quality assurance and final review

**Generated Content:**
- High-quality content aligned with specifications
- SEO-optimized structure and keywords
- Engaging tone and clear messaging

**Quality Metrics:**
- Readability score: 85/100
- SEO optimization: Complete
- Brand alignment: Verified`,

    'data-processing': `## Data Processing Results

**Task:** ${taskDescription}

**Crew Execution Summary:**
- **Data Engineer Agent:** Processed and transformed raw data
- **Validator Agent:** Ensured data quality and integrity
- **Formatter Agent:** Applied consistent formatting and structure

**Processing Results:**
- Data validation: 100% complete
- Transformation: Successfully applied
- Quality checks: All passed

**Output Summary:**
- Clean, structured data ready for analysis
- Consistent formatting applied
- Quality assurance completed`
  };

  return crewResults[crewId as keyof typeof crewResults] || `Crew task "${crewId}" completed successfully for: ${taskDescription}`;
}
