import { cache } from "react";
import { Client, fetchExchange, gql } from "urql";
import { magnitudeLabels, slogan } from "@mystar/shared";
import { StarConsole } from "./StarConsole";

const getClient = cache(
  () =>
    new Client({
      url: "http://localhost:8000/graphql",
      exchanges: [fetchExchange],
    }),
);

const HealthQuery = gql`
  query HealthAndMe {
    health
    me {
      id
      email
      display_name
    }
  }
`;

export default async function HomePage() {
  const client = getClient();
  const { data } = await client
    .query(HealthQuery, {})
    .toPromise()
    .catch(() => ({ data: undefined }));

  const exampleLevel = "L3" as const;

  return (
    <main className="min-h-screen bg-black text-white flex flex-col items-center gap-6 p-6">
      <section className="flex flex-col items-center gap-4">
        <p className="text-sm uppercase tracking-[0.3em] text-slate-300">MyriadStar</p>
        <h1 className="text-4xl font-light">{slogan}</h1>
        <p className="max-w-xl text-center text-slate-400">
          GraphQL health: <span className="font-mono">{data?.health ?? "unknown"}</span>；
          当前登录星主（示例）：
          <span className="font-mono">
            {data?.me?.display_name ?? "未初始化"} ({data?.me?.email ?? "n/a"})
          </span>
          。示例星等标签：{magnitudeLabels[exampleLevel]} ({exampleLevel}).
        </p>
      </section>

      <StarConsole />
    </main>
  );
}
