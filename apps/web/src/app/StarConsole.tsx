\"use client\";

import { useState } from \"react\";
import type { StarLevel } from \"@mystar/shared\";
import { magnitudeLabels } from \"@mystar/shared\";

const GRAPHQL_URL = \"http://localhost:8000/graphql\";

async function callGraphQL<T>(query: string, variables?: Record<string, unknown>): Promise<T> {
  const res = await fetch(GRAPHQL_URL, {
    method: \"POST\",
    headers: { \"Content-Type\": \"application/json\" },
    body: JSON.stringify({ query, variables }),
  });
  if (!res.ok) {
    throw new Error(`GraphQL HTTP ${res.status}`);
  }
  const json = (await res.json()) as { data?: T; errors?: unknown };
  if (!json.data) {
    throw new Error(\"GraphQL 调用失败\");
  }
  return json.data;
}

export function StarConsole() {
  const [starId, setStarId] = useState<string>(\"\");
  const [starName, setStarName] = useState<string>(\"我的第一颗智星\");
  const [domain, setDomain] = useState<string>(\"古籍修复\");
  const [latestMag, setLatestMag] = useState<StarLevel | null>(null);
  const [feedingCount, setFeedingCount] = useState(0);
  const [loading, setLoading] = useState<string | null>(null);
  const [log, setLog] = useState<string>(\"\");

  const appendLog = (line: string) => {
    setLog((prev) => `${line}\n${prev}`);
  };

  const handleCreateStar = async () => {
    setLoading(\"create\");
    try {
      const data = await callGraphQL<{ createStar: { id: string; name: string } }>(
        `
        mutation CreateStar($name: String!, $domain: String!) {
          createStar(name: $name, domain: $domain) {
            id
            name
          }
        }
      `,
        { name: starName, domain },
      );
      setStarId(data.createStar.id);
      appendLog(`✅ 已创建智星「${data.createStar.name}」，ID=${data.createStar.id}`);
    } catch (e) {
      appendLog(`❌ 创建智星失败：${String(e)}`);
    } finally {
      setLoading(null);
    }
  };

  const handleFeed = async () => {
    if (!starId) {
      appendLog(\"请先创建或选择一颗智星。`);
      return;
    }
    setLoading(\"feed\");
    try {
      await callGraphQL<{ ingest_knowledge: boolean }>(
        `
        mutation Ingest($starId: String!) {
          ingest_knowledge(star_id: $starId)
        }
      `,
        { starId },
      );
      setFeedingCount((c) => c + 1);
      appendLog(\"✨ 已喂入一份星尘（模拟知识）。\");
    } catch (e) {
      appendLog(`❌ 星尘喂入失败：${String(e)}`);
    } finally {
      setLoading(null);
    }
  };

  const handleEvaluate = async () => {
    if (!starId) {
      appendLog(\"请先创建或选择一颗智星。`);
      return;
    }
    setLoading(\"eval\");
    try {
      const data = await callGraphQL<{ evaluate_star: StarLevel }>(
        `
        mutation Eval($starId: String!) {
          evaluate_star(star_id: $starId)
        }
      `,
        { starId },
      );
      setLatestMag(data.evaluate_star);
      appendLog(`🌟 评估完成，当前星等：${data.evaluate_star}`);
    } catch (e) {
      appendLog(`❌ 评估失败：${String(e)}`);
    } finally {
      setLoading(null);
    }
  };

  const disabled = !!loading;

  return (
    <section className=\"mt-10 w-full max-w-2xl rounded-2xl border border-slate-700/60 bg-slate-900/60 p-6\">
      <h2 className=\"text-xl font-semibold mb-4\">星主控制台 · MVP 闭环</h2>
      <p className=\"text-sm text-slate-400 mb-4\">
        按顺序体验：1）创建智星 2）多次喂星尘 3）一键评估星等。
      </p>

      <div className=\"space-y-3 mb-4\">
        <div className=\"flex gap-2\">
          <input
            className=\"flex-1 rounded bg-slate-800 px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-sky-500\"
            value={starName}
            onChange={(e) => setStarName(e.target.value)}
            placeholder=\"智星名称，如：古籍星\"
          />
          <input
            className=\"w-40 rounded bg-slate-800 px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-sky-500\"
            value={domain}
            onChange={(e) => setDomain(e.target.value)}
            placeholder=\"星域，如：古籍修复\"
          />
        </div>

        <button
          onClick={handleCreateStar}
          disabled={disabled}
          className=\"inline-flex items-center justify-center rounded-lg bg-sky-500 px-4 py-2 text-sm font-medium text-white hover:bg-sky-400 disabled:opacity-60\"
        >
          {loading === \"create\" ? \"创建中…\" : \"① 创建智星\"}
        </button>

        {starId && (
          <p className=\"text-xs text-slate-400 break-all\">
            当前智星 ID：<span className=\"font-mono\">{starId}</span>
          </p>
        )}
      </div>

      <div className=\"flex items-center gap-3 mb-4\">
        <button
          onClick={handleFeed}
          disabled={disabled || !starId}
          className=\"inline-flex items-center justify-center rounded-lg bg-emerald-500 px-4 py-2 text-sm font-medium text-white hover:bg-emerald-400 disabled:opacity-60\"
        >
          {loading === \"feed\" ? \"喂入中…\" : \"② 喂一份星尘\"}
        </button>
        <span className=\"text-xs text-slate-400\">已喂入次数：{feedingCount}</span>
      </div>

      <div className=\"flex items-center gap-3 mb-4\">
        <button
          onClick={handleEvaluate}
          disabled={disabled || !starId}
          className=\"inline-flex items-center justify-center rounded-lg bg-violet-500 px-4 py-2 text-sm font-medium text-white hover:bg-violet-400 disabled:opacity-60\"
        >
          {loading === \"eval\" ? \"评估中…\" : \"③ 一键评估星等\"}
        </button>
        {latestMag && (
          <span className=\"text-sm text-amber-300\">
            当前星等：{magnitudeLabels[latestMag]} ({latestMag})
          </span>
        )}
      </div>

      <div className=\"mt-4\">
        <p className=\"text-xs text-slate-500 mb-1\">操作日志（最新在上）</p>
        <pre className=\"h-32 overflow-y-auto rounded bg-slate-950/60 p-2 text-xs text-slate-300 whitespace-pre-wrap\">
          {log || \"尚无操作。试着先创建一颗智星吧。\"}
        </pre>
      </div>
    </section>
  );
}


