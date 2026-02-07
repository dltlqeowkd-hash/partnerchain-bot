'use client'

import { useParams, useRouter } from 'next/navigation'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { useAuth } from '@/contexts/auth-context'

const productsData: any = {
    'naver-shopping-bot': {
        name: 'NaverShop Pro',
        description: '네이버 쇼핑 자동화 봇',
        fullDescription: '네이버 쇼핑에서 상품 순위를 높이고 클릭률을 극대화하는 프리미엄 자동화 솔루션입니다.',
        features: [
            '실시간 순위 모니터링 및 자동 최적화',
            '경쟁사 분석 및 가격 전략 수립',
            '자동 키워드 관리 및 SEO 최적화',
            '클릭/조회수 자동 증가 시스템',
            '안전한 IP 로테이션 및 인간 행동 시뮬레이션',
        ],
        benefits: [
            '하루 평균 2-3시간 작업 시간 절약',
            '상품 노출률 200% 이상 증가',
            '전환율 향상으로 매출 극대화',
        ],
        price: '월 99,000원',
        trial: true,
    },
    'blog-master-ai': {
        name: 'BlogMaster AI',
        description: '네이버 블로그 자동 포스팅',
        fullDescription: 'AI 기반으로 고품질 블로그 콘텐츠를 자동 생성하고 포스팅하는 혁신적인 솔루션입니다.',
        features: [
            'GPT 기반 자연스러운 콘텐츠 자동 생성',
            '이미지 분석 및 자동 캡션 생성',
            'SEO 최적화된 키워드 자동 삽입',
            '예약 포스팅 및 자동 발행',
            '블로그 트래픽 분석 대시보드',
        ],
        benefits: [
            '하루 최대 10개 고품질 포스팅 자동 생성',
            '검색 노출 향상으로 방문자 유입 증가',
            '블로그 운영 시간 90% 단축',
        ],
        price: '월 79,000원',
        trial: true,
    },
    'sourcing-bot': {
        name: 'Sourcing Bot',
        description: '소싱 자동화 솔루션',
        fullDescription: '중국 및 해외 소싱 사이트에서 상품을 자동으로 검색하고 가격을 비교하는 스마트 소싱 도구입니다.',
        features: [
            '타오바오, 알리바바 등 주요 소싱 사이트 연동',
            '실시간 환율 반영 가격 비교',
            '자동 번역 및 상품 정보 추출',
            '공급업체 신뢰도 자동 평가',
            '원클릭 견적서 다운로드',
        ],
        benefits: [
            '소싱 시간 80% 단축',
            '최저가 공급업체 자동 탐색',
            '위험 공급업체 사전 필터링',
        ],
        price: '월 59,000원',
        trial: true,
    },
}

export default function ProductDetailPage() {
    const params = useParams()
    const router = useRouter()
    const { user } = useAuth()
    const id = params.id as string
    const product = productsData[id]

    if (!product) {
        return (
            <div className="container mx-auto px-4 py-16 text-center">
                <h1 className="text-2xl font-bold text-gray-900 mb-4">제품을 찾을 수 없습니다</h1>
                <Button onClick={() => router.push('/')}>홈으로 돌아가기</Button>
            </div>
        )
    }

    return (
        <div className="min-h-screen bg-gray-50">
            {/* Hero */}
            <div className="bg-gradient-to-r from-blue-600 to-indigo-700 text-white py-16">
                <div className="container mx-auto px-4">
                    <div className="max-w-4xl mx-auto text-center">
                        <h1 className="text-5xl font-bold mb-4">{product.name}</h1>
                        <p className="text-xl mb-6">{product.fullDescription}</p>
                        {product.trial && (
                            <Badge className="bg-yellow-400 text-yellow-900 px-4 py-2 text-sm font-semibold">
                                ✨ 7일 무료 체험 가능
                            </Badge>
                        )}
                    </div>
                </div>
            </div>

            <div className="container mx-auto px-4 py-16">
                <div className="max-w-5xl mx-auto grid md:grid-cols-3 gap-8">
                    {/* Main Content */}
                    <div className="md:col-span-2 space-y-8">
                        {/* Features */}
                        <Card className="shadow-lg">
                            <CardHeader>
                                <CardTitle className="text-2xl text-gray-900">주요 기능</CardTitle>
                            </CardHeader>
                            <CardContent>
                                <ul className="space-y-3">
                                    {product.features.map((feature: string, idx: number) => (
                                        <li key={idx} className="flex items-start text-gray-700">
                                            <svg className="w-6 h-6 text-blue-600 mr-3 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                                            </svg>
                                            {feature}
                                        </li>
                                    ))}
                                </ul>
                            </CardContent>
                        </Card>

                        {/* Benefits */}
                        <Card className="shadow-lg">
                            <CardHeader>
                                <CardTitle className="text-2xl text-gray-900">기대 효과</CardTitle>
                            </CardHeader>
                            <CardContent>
                                <ul className="space-y-3">
                                    {product.benefits.map((benefit: string, idx: number) => (
                                        <li key={idx} className="flex items-start text-gray-700">
                                            <svg className="w-6 h-6 text-green-600 mr-3 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                                            </svg>
                                            {benefit}
                                        </li>
                                    ))}
                                </ul>
                            </CardContent>
                        </Card>
                    </div>

                    {/* Sidebar */}
                    <div>
                        <Card className="shadow-xl sticky top-24 border-2 border-blue-200">
                            <CardHeader className="bg-gradient-to-r from-blue-50 to-indigo-50">
                                <CardTitle className="text-center text-gray-900">구독 플랜</CardTitle>
                            </CardHeader>
                            <CardContent className="space-y-6 pt-6">
                                <div className="text-center">
                                    <div className="text-4xl font-bold text-blue-600 mb-2">{product.price}</div>
                                    <p className="text-sm text-gray-600">VAT 별도</p>
                                </div>

                                <div className="space-y-3">
                                    {user ? (
                                        // 로그인 상태: 대시보드로 이동
                                        <>
                                            <Button
                                                className="w-full bg-blue-600 hover:bg-blue-700 text-white py-6 text-lg"
                                                onClick={() => router.push('/dashboard')}
                                            >
                                                대시보드로 이동
                                            </Button>
                                            <Button
                                                variant="outline"
                                                className="w-full border-2 border-blue-600 text-blue-600 hover:bg-blue-50 py-6 text-lg"
                                                onClick={() => router.push(`/download/${id}`)}
                                            >
                                                프로그램 다운로드
                                            </Button>
                                        </>
                                    ) : (
                                        // 비로그인 상태: 회원가입
                                        <>
                                            <Button
                                                className="w-full bg-blue-600 hover:bg-blue-700 text-white py-6 text-lg"
                                                onClick={() => router.push('/signup')}
                                            >
                                                무료 체험 시작하기
                                            </Button>
                                            <Button
                                                variant="outline"
                                                className="w-full border-2 border-blue-600 text-blue-600 hover:bg-blue-50 py-6 text-lg"
                                                onClick={() => router.push(`/download/${id}`)}
                                            >
                                                프로그램 다운로드
                                            </Button>
                                        </>
                                    )}
                                </div>

                                <div className="text-sm text-gray-600 text-center space-y-2 pt-4 border-t">
                                    <p>✅ 7일 무료 체험</p>
                                    <p>✅ 언제든지 해지 가능</p>
                                    <p>✅ 24/7 고객 지원</p>
                                </div>
                            </CardContent>
                        </Card>
                    </div>
                </div>
            </div>
        </div>
    )
}
