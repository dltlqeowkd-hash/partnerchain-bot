'use client'

import { useParams, useRouter } from 'next/navigation'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'

const downloadsData: any = {
    'naver-shopping-bot': {
        name: 'NaverShop Pro',
        version: 'v3.2.1',
        releaseDate: '2026-02-01',
        fileSize: '45 MB',
        description: '네이버 쇼핑 자동화 봇 - 상품 순위 최적화 및 클릭률 자동 증가 솔루션',
        requirements: [
            'Windows 10 이상 (64bit)',
            'RAM 4GB 이상 권장',
            'Chrome 브라우저',
            '안정적인 인터넷 연결',
        ],
        features: [
            '자동 순위 모니터링',
            '키워드 최적화 엔진',
            'IP 로테이션 시스템',
            '실시간 분석 대시보드',
        ],
        instructions: [
            '다운로드 버튼을 클릭하여 설치 파일(NaverShopPro.exe)을 다운로드합니다.',
            '다운로드된 파일을 실행하여 설치를 진행합니다.',
            '설치 완료 후 프로그램을 실행하고 회원가입 시 사용한 계정으로 로그인합니다.',
            '대시보드에서 받은 라이선스 키를 입력하여 제품을 활성화합니다.',
            '자세한 사용법은 프로그램 내 "도움말" 메뉴를 참고하세요.',
        ],
        downloadPath: '/files/NaverShopPro_v3.2.1.exe',
    },
    'blog-master-ai': {
        name: 'BlogMaster AI',
        version: 'v2.5.0',
        releaseDate: '2026-01-28',
        fileSize: '38 MB',
        description: 'AI 기반 네이버 블로그 자동 포스팅 솔루션',
        requirements: [
            'Windows 10 이상 (64bit)',
            'RAM 4GB 이상 권장',
            'Chrome 브라우저',
            '안정적인 인터넷 연결',
        ],
        features: [
            'GPT 기반 콘텐츠 자동 생성',
            '이미지 자동 분석 및 캡션 생성',
            '예약 포스팅 기능',
            'SEO 최적화 자동 적용',
        ],
        instructions: [
            '다운로드 버튼을 클릭하여 설치 파일(BlogMasterAI.exe)을 다운로드합니다.',
            '다운로드된 파일을 실행하여 설치를 진행합니다.',
            '설치 완료 후 프로그램을 실행하고 계정으로 로그인합니다.',
            '라이선스 키를 입력하여 활성화합니다.',
            '네이버 블로그 계정을 연동하고 첫 포스팅을 시작하세요!',
        ],
        downloadPath: '/files/BlogMasterAI_v2.5.0.exe',
    },
    'sourcing-bot': {
        name: 'Sourcing Bot',
        version: 'v1.8.3',
        releaseDate: '2026-02-05',
        fileSize: '32 MB',
        description: '소싱 자동화 솔루션 - 타오바오/알리바바 자동 검색 및 비교',
        requirements: [
            'Windows 10 이상 (64bit)',
            'RAM 4GB 이상 권장',
            'Chrome 브라우저',
            '안정적인 인터넷 연결',
        ],
        features: [
            '다중 소싱 사이트 통합 검색',
            '실시간 환율 반영',
            '자동 번역 기능',
            '공급업체 신뢰도 평가',
        ],
        instructions: [
            '다운로드 버튼을 클릭하여 설치 파일(SourcingBot.exe)을 다운로드합니다.',
            '다운로드된 파일을 실행하여 설치를 진행합니다.',
            '프로그램 실행 후 로그인합니다.',
            '라이선스 키를 입력하여 활성화합니다.',
            '소싱할 상품 키워드를 입력하고 검색을 시작하세요!',
        ],
        downloadPath: '/files/SourcingBot_v1.8.3.exe',
    },
}

export default function DownloadPage() {
    const params = useParams()
    const router = useRouter()
    const id = params.id as string
    const downloadInfo = downloadsData[id]

    if (!downloadInfo) {
        return (
            <div className="container mx-auto px-4 py-16 text-center">
                <h1 className="text-2xl font-bold text-gray-900 mb-4">다운로드를 찾을 수 없습니다</h1>
                <Button onClick={() => router.push('/')}>홈으로 돌아가기</Button>
            </div>
        )
    }

    const handleDownload = () => {
        // 실제 다운로드 로직 (예: 백엔드 API 호출 후 파일 링크 제공)
        alert(`준비 중입니다.\n파일: ${downloadInfo.name} (${downloadInfo.version})\n\n실제 서비스에서는 로그인 후 구독 중인 사용자만 다운로드할 수 있습니다.`)
    }

    return (
        <div className="min-h-screen bg-gray-50">
            <div className="bg-gradient-to-r from-green-600 to-teal-700 text-white py-12">
                <div className="container mx-auto px-4 text-center">
                    <h1 className="text-4xl font-bold mb-2">{downloadInfo.name}</h1>
                    <p className="text-lg">{downloadInfo.description}</p>
                </div>
            </div>

            <div className="container mx-auto px-4 py-12">
                <div className="max-w-4xl mx-auto">
                    <div className="grid md:grid-cols-3 gap-8">
                        {/* Main Content */}
                        <div className="md:col-span-2 space-y-6">
                            {/* Version Info */}
                            <Card className="shadow-lg">
                                <CardHeader>
                                    <CardTitle className="text-xl text-gray-900">버전 정보</CardTitle>
                                </CardHeader>
                                <CardContent className="grid grid-cols-2 gap-4 text-gray-700">
                                    <div>
                                        <p className="text-sm text-gray-500">버전</p>
                                        <p className="font-semibold">{downloadInfo.version}</p>
                                    </div>
                                    <div>
                                        <p className="text-sm text-gray-500">배포일</p>
                                        <p className="font-semibold">{downloadInfo.releaseDate}</p>
                                    </div>
                                    <div>
                                        <p className="text-sm text-gray-500">파일 크기</p>
                                        <p className="font-semibold">{downloadInfo.fileSize}</p>
                                    </div>
                                    <div>
                                        <p className="text-sm text-gray-500">상태</p>
                                        <Badge className="bg-green-100 text-green-800">최신 버전</Badge>
                                    </div>
                                </CardContent>
                            </Card>

                            {/* System Requirements */}
                            <Card className="shadow-lg">
                                <CardHeader>
                                    <CardTitle className="text-xl text-gray-900">시스템 요구사항</CardTitle>
                                </CardHeader>
                                <CardContent>
                                    <ul className="space-y-2">
                                        {downloadInfo.requirements.map((req: string, idx: number) => (
                                            <li key={idx} className="flex items-center text-gray-700">
                                                <svg className="w-5 h-5 text-blue-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                                                </svg>
                                                {req}
                                            </li>
                                        ))}
                                    </ul>
                                </CardContent>
                            </Card>

                            {/* Installation Instructions */}
                            <Card className="shadow-lg">
                                <CardHeader>
                                    <CardTitle className="text-xl text-gray-900">설치 및 사용 방법</CardTitle>
                                </CardHeader>
                                <CardContent>
                                    <ol className="space-y-3">
                                        {downloadInfo.instructions.map((instruction: string, idx: number) => (
                                            <li key={idx} className="flex items-start text-gray-700">
                                                <span className="inline-flex items-center justify-center w-7 h-7 rounded-full bg-blue-600 text-white font-bold text-sm mr-3 flex-shrink-0 mt-0.5">
                                                    {idx + 1}
                                                </span>
                                                {instruction}
                                            </li>
                                        ))}
                                    </ol>
                                </CardContent>
                            </Card>
                        </div>

                        {/* Sidebar Download Box */}
                        <div>
                            <Card className="shadow-xl sticky top-24 border-2 border-green-200">
                                <CardHeader className="bg-gradient-to-r from-green-50 to-teal-50">
                                    <CardTitle className="text-center text-gray-900">다운로드</CardTitle>
                                </CardHeader>
                                <CardContent className="space-y-4 pt-6">
                                    <div className="text-center">
                                        <div className="text-6xl mb-4">📦</div>
                                        <h3 className="font-bold text-lg text-gray-900 mb-2">{downloadInfo.name}</h3>
                                        <p className="text-sm text-gray-600 mb-4">{downloadInfo.version} ({downloadInfo.fileSize})</p>
                                    </div>

                                    <Button
                                        className="w-full bg-green-600 hover:bg-green-700 text-white py-6 text-lg font-semibold"
                                        onClick={handleDownload}
                                    >
                                        ⬇️ 다운로드 시작
                                    </Button>

                                    <div className="text-xs text-gray-500 text-center space-y-1 pt-4 border-t">
                                        <p>✅ 무료 체험 7일</p>
                                        <p>✅ 자동 업데이트 지원</p>
                                        <p>✅ 안전한 다운로드</p>
                                    </div>

                                    <div className="pt-4 border-t">
                                        <p className="text-sm text-gray-600 mb-3">제품에 대해 더 알고 싶으신가요?</p>
                                        <Button
                                            variant="outline"
                                            className="w-full border-green-600 text-green-700 hover:bg-green-50"
                                            onClick={() => router.push(`/products/${id}`)}
                                        >
                                            제품 상세 보기
                                        </Button>
                                    </div>
                                </CardContent>
                            </Card>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}
