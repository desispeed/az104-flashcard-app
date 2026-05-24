#!/usr/bin/env node
import { McpServer, ResourceTemplate } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const __dirname = dirname(fileURLToPath(import.meta.url));
const QUESTIONS = JSON.parse(
  readFileSync(join(__dirname, "data", "questions.json"), "utf8")
);

const QUESTIONS_BY_ID = new Map(QUESTIONS.map((q) => [q.id, q]));

const CATEGORIES = (() => {
  const counts = new Map();
  for (const q of QUESTIONS) {
    counts.set(q.category, (counts.get(q.category) ?? 0) + 1);
  }
  return [...counts.entries()].map(([name, count]) => ({ name, count }));
})();

const formatQuestion = (q, { revealAnswer = false } = {}) => {
  const lines = [
    `#${q.id} [${q.category}]`,
    q.question,
    "",
    ...q.options.map((opt, i) => `  ${String.fromCharCode(65 + i)}. ${opt}`),
  ];
  if (revealAnswer) {
    lines.push("", `Answer: ${String.fromCharCode(65 + q.correct)}`);
    lines.push(`Explanation: ${q.explanation}`);
  }
  return lines.join("\n");
};

const findCategory = (input) => {
  if (!input) return null;
  const needle = input.trim().toLowerCase();
  return (
    CATEGORIES.find((c) => c.name.toLowerCase() === needle) ??
    CATEGORIES.find((c) => c.name.toLowerCase().includes(needle)) ??
    null
  );
};

const filterByCategory = (category) => {
  if (!category) return QUESTIONS;
  const match = findCategory(category);
  if (!match) return [];
  return QUESTIONS.filter((q) => q.category === match.name);
};

const textResult = (text) => ({ content: [{ type: "text", text }] });

const server = new McpServer({
  name: "az104-flashcards",
  version: "1.0.0",
});

server.tool(
  "list_categories",
  "List all AZ-104 question categories with the number of questions in each.",
  {},
  async () => {
    const total = QUESTIONS.length;
    const lines = [
      `${total} questions across ${CATEGORIES.length} categories:`,
      "",
      ...CATEGORIES.map((c) => `- ${c.name} (${c.count})`),
    ];
    return textResult(lines.join("\n"));
  }
);

server.tool(
  "get_question",
  "Fetch a specific question by id. Set reveal_answer=true to include the correct answer and explanation.",
  {
    id: z.number().int().min(1).describe("Question id (1-based)."),
    reveal_answer: z
      .boolean()
      .optional()
      .describe("Include the correct answer and explanation. Defaults to false."),
  },
  async ({ id, reveal_answer }) => {
    const q = QUESTIONS_BY_ID.get(id);
    if (!q) return textResult(`No question with id ${id}.`);
    return textResult(formatQuestion(q, { revealAnswer: reveal_answer ?? false }));
  }
);

server.tool(
  "get_random_question",
  "Return a random question, optionally filtered by category. Use reveal_answer=true to include the answer.",
  {
    category: z
      .string()
      .optional()
      .describe("Optional category name (case-insensitive substring match)."),
    reveal_answer: z.boolean().optional(),
  },
  async ({ category, reveal_answer }) => {
    const pool = filterByCategory(category);
    if (pool.length === 0) {
      return textResult(`No questions found for category "${category}".`);
    }
    const q = pool[Math.floor(Math.random() * pool.length)];
    return textResult(formatQuestion(q, { revealAnswer: reveal_answer ?? false }));
  }
);

server.tool(
  "search_questions",
  "Search questions by keyword in the question text or options. Returns matching ids and question previews.",
  {
    query: z.string().min(1).describe("Substring to search for (case-insensitive)."),
    limit: z.number().int().min(1).max(50).optional(),
  },
  async ({ query, limit }) => {
    const needle = query.toLowerCase();
    const matches = QUESTIONS.filter(
      (q) =>
        q.question.toLowerCase().includes(needle) ||
        q.options.some((o) => o.toLowerCase().includes(needle))
    ).slice(0, limit ?? 10);
    if (matches.length === 0) return textResult(`No matches for "${query}".`);
    const lines = matches.map((q) => `#${q.id} [${q.category}] ${q.question}`);
    return textResult(lines.join("\n"));
  }
);

server.tool(
  "check_answer",
  "Check whether a chosen option is correct for a given question. answer accepts 0-based index or letter A/B/C/D.",
  {
    id: z.number().int().min(1),
    answer: z.union([z.number().int().min(0), z.string().length(1)]),
  },
  async ({ id, answer }) => {
    const q = QUESTIONS_BY_ID.get(id);
    if (!q) return textResult(`No question with id ${id}.`);
    let chosenIndex;
    if (typeof answer === "number") {
      chosenIndex = answer;
    } else {
      chosenIndex = answer.toUpperCase().charCodeAt(0) - 65;
    }
    if (chosenIndex < 0 || chosenIndex >= q.options.length) {
      return textResult(
        `Invalid answer "${answer}" for question ${id} (expected 0-${q.options.length - 1} or A-${String.fromCharCode(64 + q.options.length)}).`
      );
    }
    const correct = chosenIndex === q.correct;
    const verdict = correct ? "Correct!" : "Incorrect.";
    const correctLetter = String.fromCharCode(65 + q.correct);
    return textResult(
      `${verdict}\nYour answer: ${String.fromCharCode(65 + chosenIndex)}. ${q.options[chosenIndex]}\nCorrect answer: ${correctLetter}. ${q.options[q.correct]}\nExplanation: ${q.explanation}`
    );
  }
);

server.tool(
  "start_quiz",
  "Build a quiz of N random questions (without answers shown). Optionally filter by category.",
  {
    count: z.number().int().min(1).max(50).default(5),
    category: z.string().optional(),
  },
  async ({ count, category }) => {
    const pool = filterByCategory(category);
    if (pool.length === 0) {
      return textResult(`No questions found for category "${category}".`);
    }
    const shuffled = [...pool].sort(() => Math.random() - 0.5);
    const picked = shuffled.slice(0, Math.min(count, pool.length));
    const blocks = picked.map((q) => formatQuestion(q));
    return textResult(
      [
        `Quiz: ${picked.length} question(s)${category ? ` from ${findCategory(category)?.name ?? category}` : ""}.`,
        "Use the check_answer tool with the question id and your choice (A/B/C/D) to grade each.",
        "",
        blocks.join("\n\n---\n\n"),
      ].join("\n")
    );
  }
);

server.resource(
  "all-questions",
  "az104://questions",
  { description: "Full AZ-104 question bank (JSON).", mimeType: "application/json" },
  async (uri) => ({
    contents: [
      {
        uri: uri.href,
        mimeType: "application/json",
        text: JSON.stringify(QUESTIONS, null, 2),
      },
    ],
  })
);

server.resource(
  "question",
  new ResourceTemplate("az104://questions/{id}", { list: undefined }),
  { description: "A single AZ-104 question by id (JSON)." },
  async (uri, { id }) => {
    const q = QUESTIONS_BY_ID.get(Number(id));
    if (!q) {
      return {
        contents: [
          { uri: uri.href, mimeType: "text/plain", text: `No question with id ${id}.` },
        ],
      };
    }
    return {
      contents: [
        { uri: uri.href, mimeType: "application/json", text: JSON.stringify(q, null, 2) },
      ],
    };
  }
);

const transport = new StdioServerTransport();
await server.connect(transport);
