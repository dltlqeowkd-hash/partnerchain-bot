import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

export default function AboutPage() {
    return (
        <div className="min-h-screen bg-gradient-to-b from-white to-gray-50">
            {/* Hero Section */}
            <div className="bg-gradient-to-r from-blue-600 to-indigo-700 text-white py-20">
                <div className="container mx-auto px-4 text-center">
                    <h1 className="text-5xl font-bold mb-6">PartnerChain과 함께하세요</h1>
                    <p className="text-xl max-w-3xl mx-auto leading-relaxed">
                        우리는 온라인 비즈니스의 성공을 위한 최첨단 자동화 솔루션을 제공합니다.
                        <br />
                        판매자들이 더 경쟁력 있는 상품과 콘텐츠를 만들도록 돕는 것이 우리의 사명입니다.
                    </p>
                </div>
            </div>

            {/* Mission Section */}
            <div className="container mx-auto px-4 py-16">
                <div className="max-w-4xl mx-auto">
                    <h2 className="text-4xl font-bold text-center text-gray-900 mb-12">우리의 비전</h2>

                    <div className="grid md:grid-cols-3 gap-8 mb-16">
                        <Card className="text-center shadow-lg hover:shadow-xl transition border-t-4 border-t-blue-600">
                            <CardHeader>
                                <div className="text-5xl mb-4">🚀</div>
                                <CardTitle className="text-xl text-gray-900">혁신적인 자동화</CardTitle>
                            </CardHeader>
                            <CardContent className="text-gray-600">
                                최신 AI 기술과 자동화를 통해 반복적인 작업을 제거하고, 비즈니스 성장에 집중할 수 있게 합니다.
                            </CardContent>
                        </Card>

                        <Card className="text-center shadow-lg hover:shadow-xl transition border-t-4 border-t-indigo-600">
                            <CardHeader>
                                <div className="text-5xl mb-4">💎</div>
                                <CardTitle className="text-xl text-gray-900">프리미엄 품질</CardTitle>
                            </CardHeader>
                            <CardContent className="text-gray-600">
                                검증된 알고리즘과 수년간의 노하우로 안전하고 효과적인 솔루션을 제공합니다.
                            </CardContent>
                        </Card>

                        <Card className="text-center shadow-lg hover:shadow-xl transition border-t-4 border-t-purple-600">
                            <CardHeader>
                                <div className="text-5xl mb-4">🤝</div>
                                <CardTitle className="text-xl text-gray-900">파트너십</CardTitle>
                            </CardHeader>
                            <CardContent className="text-gray-600">
                                단순한 도구 제공이 아닌, 고객 성공을 위한 진정한 파트너로 함께합니다.
                            </CardContent>
                        </Card>
                    </div>

                    {/* What We Do */}
                    <Card className="shadow-xl">
                        <CardHeader>
                            <CardTitle className="text-2xl text-gray-900">우리가 하는 일</CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-6 text-gray-700">
                            <div className="space-y-4">
                                <h3 className="text-lg font-semibold text-gray-900 flex items-center">
                                    <span className="mr-3 text-2xl">📊</span>
                                    네이버 쇼핑 최적화
                                </h3>
                                <p className="ml-11">
                                    네이버 쇼핑에서 상품 순위를 높이고, 클릭률을 증가시키는 자동화 솔루션을 제공합니다.
                                    실시간 알고리즘 분석을 통해 경쟁력을 극대화합니다.
                                </p>
                            </div>

                            <div className="space-y-4">
                                <h3 className="text-lg font-semibold text-gray-900 flex items-center">
                                    <span className="mr-3 text-2xl">✍️</span>
                                    콘텐츠 자동 생성
                                </h3>
                                <p className="ml-11">
                                    AI 기반 블로그 포스팅, 상품 설명 자동 작성 등 콘텐츠 마케팅을 자동화합니다.
                                    SEO 최적화된 고품질 콘텐츠를 빠르게 생산할 수 있습니다.
                                </p>
                            </div>

                            <div className="space-y-4">
                                <h3 className="text-lg font-semibold text-gray-900 flex items-center">
                                    <span className="mr-3 text-2xl">⚡</span>
                                    효율성 극대화
                                </h3>
                                <p className="ml-11">
                                    하루 종일 수작업으로 해야 할 일들을 몇 분 만에 완료할 수 있도록 지원합니다.
                                    시간을 절약하고, 더 중요한 전략 수립에 집중할 수 있습니다.
                                </p>
                            </div>
                        </CardContent>
                    </Card>

                    {/* CTA Section */}
                    <div className="mt-16 text-center bg-gradient-to-r from-blue-50 to-indigo-50 p-12 rounded-xl">
                        <h3 className="text-3xl font-bold text-gray-900 mb-4">
                            지금 바로 시작하세요
                        </h3>
                        <p className="text-gray-600 mb-8 text-lg">
                            전문가들이 사용하는 프리미엄 자동화 솔루션으로 비즈니스를 한 단계 업그레이드하세요.
                        </p>
                        <div className="flex justify-center space-x-4">
                            <a href="/signup" className="px-8 py-3 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition shadow-lg">
                                무료 체험 시작하기
                            </a>
                            <a href="/products/naver-shopping-bot" className="px-8 py-3 bg-white text-blue-600 border-2 border-blue-600 rounded-lg font-semibold hover:bg-blue-50 transition">
                                제품 둘러보기
                            </a>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}
