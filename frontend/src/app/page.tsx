'use client'

import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useAuth } from "@/contexts/auth-context";

export default function Home() {
  const { user } = useAuth();

  return (
    <div className="flex min-h-screen flex-col">
      <section className="relative flex-1 flex items-center justify-center overflow-hidden bg-gradient-to-br from-indigo-900 via-purple-900 to-black px-4 py-24 text-center text-white">
        <div className="absolute inset-0 bg-[url('/grid-pattern.svg')] opacity-10"></div>
        <div className="container relative z-10 mx-auto max-w-4xl space-y-8">
          <Badge variant="secondary" className="px-4 py-1 text-sm font-medium uppercase tracking-wider text-indigo-900 bg-indigo-100">
            Performance Marketing Automation v4.2
          </Badge>
          <h1 className="text-5xl font-extrabold tracking-tight sm:text-7xl bg-clip-text text-transparent bg-gradient-to-r from-blue-200 to-purple-200">
            PartnerChain
            <br />
            <span className="text-4xl sm:text-6xl text-gray-300">네이버 마케팅 자동화의 혁신</span>
          </h1>
          <p className="mx-auto max-w-2xl text-lg text-gray-300 sm:text-xl">
            수작업 없는 100% 자동화, 강력한 어뷰징 방지 기술.
            <br />
            검증된 알고리즘으로 당신의 비즈니스를 상위 노출시키세요.
          </p>
          <div className="flex flex-col items-center justify-center gap-4 sm:flex-row">
            {user ? (
              // 로그인 상태: 대시보드로 이동
              <Link href="/dashboard">
                <Button size="lg" className="h-14 min-w-[200px] text-lg font-bold bg-white text-indigo-900 hover:bg-gray-100">
                  대시보드로 이동
                </Button>
              </Link>
            ) : (
              // 비로그인 상태: 회원가입 & 로그인
              <>
                <Link href="/signup">
                  <Button size="lg" className="h-14 min-w-[200px] text-lg font-bold bg-white text-indigo-900 hover:bg-gray-100">
                    무료 체험 시작하기
                  </Button>
                </Link>
                <Link href="/login">
                  <Button size="lg" variant="outline" className="h-14 min-w-[200px] text-lg border-white text-white hover:bg-white/10">
                    로그인
                  </Button>
                </Link>
              </>
            )}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="bg-background py-24">
        <div className="container mx-auto px-4">
          <div className="grid gap-12 sm:grid-cols-2 lg:grid-cols-3">
            <FeatureCard
              title="검증된 로직"
              desc="수년간의 테스트를 거친 안전하고 효과적인 상위 노출 알고리즘을 탑재했습니다."
              icon="🛡️"
            />
            <FeatureCard
              title="완전 자동화"
              desc="키워드 입력만 하면 끝. 검색, 클릭, 체류, 이동까지 모든 과정을 봇이 처리합니다."
              icon="🤖"
            />
            <FeatureCard
              title="실시간 리포트"
              desc="대시보드에서 봇의 활동 내역과 성과를 실시간으로 확인하고 제어할 수 있습니다."
              icon="📊"
            />
          </div>
        </div>
      </section>
    </div>
  );
}

function FeatureCard({ title, desc, icon }: { title: string; desc: string; icon: string }) {
  return (
    <div className="group rounded-2xl border bg-card p-8 shadow-sm transition-all hover:shadow-md hover:-translate-y-1">
      <div className="mb-4 text-4xl">{icon}</div>
      <h3 className="mb-3 text-xl font-bold">{title}</h3>
      <p className="text-muted-foreground leading-relaxed">{desc}</p>
    </div>
  );
}
