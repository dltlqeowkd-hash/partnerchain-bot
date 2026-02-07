'use client'

import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { useAuth } from "@/contexts/auth-context";
import { Check, Zap, Shield, TrendingUp, Users, Clock } from "lucide-react";

export default function Home() {
  const { user } = useAuth();

  const plans = [
    {
      name: "스타터",
      price: "29,000원",
      period: "/월",
      description: "개인 사업자에게 최적",
      features: [
        "기본 자동화 기능",
        "월 1,000건 처리",
        "이메일 지원",
        "기본 리포트"
      ],
      color: "from-blue-500 to-cyan-500",
      recommended: false
    },
    {
      name: "프로페셔널",
      price: "79,000원",
      period: "/월",
      description: "성장하는 비즈니스를 위한",
      features: [
        "고급 자동화 기능",
        "월 5,000건 처리",
        "우선 지원",
        "상세 분석 리포트",
        "API 접근",
        "멀티 계정"
      ],
      color: "from-purple-500 to-pink-500",
      recommended: true
    },
    {
      name: "엔터프라이즈",
      price: "문의",
      period: "",
      description: "대규모 운영을 위한",
      features: [
        "무제한 자동화",
        "무제한 처리",
        "전담 매니저",
        "맞춤형 솔루션",
        "24/7 지원",
        "온프레미스 옵션"
      ],
      color: "from-orange-500 to-red-500",
      recommended: false
    }
  ];

  const features = [
    {
      icon: <Zap className="w-8 h-8" />,
      title: "빠른 자동화",
      description: "복잡한 작업을 몇 분 만에 자동화하여 시간을 절약하세요"
    },
    {
      icon: <Shield className="w-8 h-8" />,
      title: "안전한 관리",
      description: "엔터프라이즈급 보안으로 데이터를 안전하게 보호합니다"
    },
    {
      icon: <TrendingUp className="w-8 h-8" />,
      title: "성장 지원",
      description: "비즈니스 성장에 따라 자유롭게 확장 가능합니다"
    },
    {
      icon: <Users className="w-8 h-8" />,
      title: "팀 협업",
      description: "팀원들과 함께 효율적으로 작업할 수 있습니다"
    },
    {
      icon: <Clock className="w-8 h-8" />,
      title: "실시간 모니터링",
      description: "모든 작업을 실시간으로 추적하고 관리하세요"
    }
  ];

  return (
    <div className="flex min-h-screen flex-col">
      {/* Hero Section - COOL IP Style */}
      <section className="relative flex-1 flex items-center justify-center overflow-hidden bg-gradient-to-br from-blue-600 via-indigo-700 to-purple-800 px-4 py-24 text-center text-white">
        {/* Animated Background */}
        <div className="absolute inset-0 opacity-20">
          <div className="absolute top-0 -left-4 w-72 h-72 bg-purple-500 rounded-full mix-blend-multiply filter blur-xl animate-blob"></div>
          <div className="absolute top-0 -right-4 w-72 h-72 bg-blue-500 rounded-full mix-blend-multiply filter blur-xl animate-blob animation-delay-2000"></div>
          <div className="absolute -bottom-8 left-20 w-72 h-72 bg-indigo-500 rounded-full mix-blend-multiply filter blur-xl animate-blob animation-delay-4000"></div>
        </div>

        <div className="relative mx-auto max-w-5xl space-y-8">
          <div className="inline-block">
            <Badge className="mb-4 bg-white/20 text-white border-white/30 px-4 py-2 text-sm backdrop-blur-sm">
              ✨ 3일 무료 체험 진행 중
            </Badge>
          </div>

          <h1 className="text-5xl font-bold tracking-tight sm:text-6xl md:text-7xl">
            비즈니스 자동화의
            <br />
            <span className="bg-gradient-to-r from-cyan-300 to-blue-300 bg-clip-text text-transparent">
              새로운 기준
            </span>
          </h1>

          <p className="mx-auto max-w-2xl text-lg sm:text-xl text-blue-100">
            복잡한 업무를 간단하게. 반복 작업을 자동으로.
            <br />
            지금 바로 파트너체인과 함께 시작하세요.
          </p>

          <div className="flex flex-col items-center justify-center gap-4 sm:flex-row mt-8">
            {user ? (
              <Link href="/dashboard">
                <Button size="lg" className="h-14 min-w-[200px] text-lg font-bold bg-white text-indigo-900 hover:bg-gray-100 shadow-xl hover:shadow-2xl transition-all">
                  대시보드로 이동
                </Button>
              </Link>
            ) : (
              <>
                <Link href="/signup">
                  <Button size="lg" className="h-14 min-w-[200px] text-lg font-bold bg-white text-indigo-900 hover:bg-gray-100 shadow-xl hover:shadow-2xl transition-all">
                    무료 체험 시작하기
                  </Button>
                </Link>
                <Link href="/login">
                  <Button size="lg" variant="outline" className="h-14 min-w-[200px] text-lg border-2 border-white text-white hover:bg-white/10 backdrop-blur-sm">
                    로그인
                  </Button>
                </Link>
              </>
            )}
          </div>

          <div className="flex flex-wrap items-center justify-center gap-8 mt-12 text-sm text-blue-200">
            <div className="flex items-center gap-2">
              <Check className="w-5 h-5" />
              <span>신용카드 불필요</span>
            </div>
            <div className="flex items-center gap-2">
              <Check className="w-5 h-5" />
              <span>3일 무료 체험</span>
            </div>
            <div className="flex items-center gap-2">
              <Check className="w-5 h-5" />
              <span>언제든 해지 가능</span>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-gray-50">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              왜 파트너체인인가요?
            </h2>
            <p className="text-xl text-gray-600">
              비즈니스 성장을 위한 완벽한 솔루션
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 max-w-6xl mx-auto">
            {features.map((feature, index) => (
              <Card key={index} className="border-2 hover:border-blue-500 transition-all hover:shadow-lg">
                <CardHeader>
                  <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-2xl flex items-center justify-center text-white mb-4">
                    {feature.icon}
                  </div>
                  <CardTitle className="text-xl">{feature.title}</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-gray-600">{feature.description}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing Section - COOL IP Style Cards */}
      <section className="py-20 bg-white">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              합리적인 요금제
            </h2>
            <p className="text-xl text-gray-600">
              비즈니스 규모에 맞는 최적의 플랜을 선택하세요
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-6xl mx-auto">
            {plans.map((plan, index) => (
              <Card
                key={index}
                className={`relative border-2 transition-all hover:shadow-2xl ${plan.recommended
                    ? 'border-purple-500 shadow-xl scale-105'
                    : 'border-gray-200 hover:border-blue-400'
                  }`}
              >
                {plan.recommended && (
                  <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                    <Badge className="bg-gradient-to-r from-purple-500 to-pink-500 text-white px-4 py-1 text-sm">
                      🔥 BEST
                    </Badge>
                  </div>
                )}

                <CardHeader className="text-center pb-8 pt-8">
                  <div className={`w-20 h-20 mx-auto mb-4 rounded-2xl bg-gradient-to-br ${plan.color} flex items-center justify-center`}>
                    <Zap className="w-10 h-10 text-white" />
                  </div>
                  <CardTitle className="text-2xl mb-2">{plan.name}</CardTitle>
                  <CardDescription className="text-gray-600">{plan.description}</CardDescription>
                  <div className="mt-6">
                    <span className="text-4xl font-bold text-gray-900">{plan.price}</span>
                    <span className="text-gray-600">{plan.period}</span>
                  </div>
                </CardHeader>

                <CardContent className="space-y-4">
                  <div className="space-y-3">
                    {plan.features.map((feature, fIndex) => (
                      <div key={fIndex} className="flex items-start gap-3">
                        <Check className="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5" />
                        <span className="text-gray-700">{feature}</span>
                      </div>
                    ))}
                  </div>

                  <Button
                    className={`w-full mt-6 h-12 text-lg ${plan.recommended
                        ? 'bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700'
                        : 'bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700'
                      }`}
                    asChild
                  >
                    <Link href={user ? "/dashboard" : "/signup"}>
                      {user ? "플랜 선택하기" : "무료로 시작하기"}
                    </Link>
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-r from-blue-600 to-indigo-700 text-white">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-4xl font-bold mb-6">
            지금 바로 시작하세요
          </h2>
          <p className="text-xl mb-8 text-blue-100 max-w-2xl mx-auto">
            3일 무료 체험으로 파트너체인의 모든 기능을 경험해보세요.
            <br />
            신용카드 정보 없이 바로 시작할 수 있습니다.
          </p>
          {!user && (
            <Link href="/signup">
              <Button size="lg" className="h-14 min-w-[250px] text-lg font-bold bg-white text-indigo-900 hover:bg-gray-100 shadow-xl">
                무료 체험 시작하기 →
              </Button>
            </Link>
          )}
        </div>
      </section>

      <style jsx global>{`
        @keyframes blob {
          0% {
            transform: translate(0px, 0px) scale(1);
          }
          33% {
            transform: translate(30px, -50px) scale(1.1);
          }
          66% {
            transform: translate(-20px, 20px) scale(0.9);
          }
          100% {
            transform: translate(0px, 0px) scale(1);
          }
        }
        .animate-blob {
          animation: blob 7s infinite;
        }
        .animation-delay-2000 {
          animation-delay: 2s;
        }
        .animation-delay-4000 {
          animation-delay: 4s;
        }
      `}</style>
    </div>
  );
}
