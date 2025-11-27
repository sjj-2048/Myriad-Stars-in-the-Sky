export default function HomePage() {
  return (
    <main className="min-h-screen bg-black text-white flex flex-col items-center justify-center gap-4">
      <p className="text-sm uppercase tracking-[0.3em] text-slate-300">MyriadStar</p>
      <h1 className="text-4xl font-light">Be Your Star. Shine Your Expertise.</h1>
      <p className="max-w-xl text-center text-slate-400">
        当前为中心化实现阶段。请使用 GraphQL Gateway 或 REST API 与智星交互，
        随时间观察星等、技能与成长轨迹。
      </p>
    </main>
  );
}
