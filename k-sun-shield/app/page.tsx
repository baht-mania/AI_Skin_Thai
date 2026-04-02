export default function Home() {
  return (
    <div
      className="min-h-screen flex flex-col items-center justify-center"
      style={{ background: "linear-gradient(135deg, #1A0E3F 0%, #2D1B69 100%)" }}
    >
      <main className="flex flex-col items-center gap-8 px-6 text-center">
        {/* Logo / Brand */}
        <div className="flex flex-col items-center gap-2">
          <span className="text-5xl">🌕</span>
          <h1 className="text-4xl font-bold text-white tracking-tight">
            K-Sun Shield
          </h1>
          <p className="text-lg font-medium" style={{ color: "#F7C948" }}>
            by FULLMOON
          </p>
        </div>

        {/* Tagline */}
        <p className="max-w-sm text-base text-purple-200 leading-relaxed">
          AI 피부 진단으로 나만의 K-뷰티 루틴을 찾아보세요.<br />
          태국 세븐일레븐에서 만나는 스마트 스킨케어.
        </p>

        {/* CTA Button */}
        <a
          href="/scan"
          className="mt-4 px-8 py-4 rounded-full text-base font-semibold text-white transition-opacity hover:opacity-90 active:opacity-75"
          style={{ background: "linear-gradient(90deg, #F7C948, #FF6B35)" }}
        >
          피부 진단 시작하기 →
        </a>

        {/* Feature pills */}
        <div className="flex flex-wrap justify-center gap-3 mt-2">
          {["AI 피부 분석", "K-뷰티 추천", "즉시 구매"].map((f) => (
            <span
              key={f}
              className="px-4 py-1.5 rounded-full text-sm font-medium text-white border border-white/20 bg-white/10"
            >
              {f}
            </span>
          ))}
        </div>
      </main>

      {/* Footer */}
      <p className="absolute bottom-6 text-xs text-purple-300/60">
        © 2026 FULLMOON · Powered by Korean Kolmar
      </p>
    </div>
  );
}
