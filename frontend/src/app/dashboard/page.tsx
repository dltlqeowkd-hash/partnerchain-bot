'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import axios from 'axios'
import Script from 'next/script'
import { useAuth } from '@/contexts/auth-context'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'

declare global {
    interface Window {
        IMP: any;
    }
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface Notification {
    id: number
    title: string
    content: string
    is_read: boolean
    created_at: string
}

export default function DashboardPage() {
    const { user, token, loading } = useAuth()
    const router = useRouter()
    const [notifications, setNotifications] = useState<Notification[]>([])

    useEffect(() => {
        if (!loading && !user) {
            router.push('/login')
        }
    }, [user, loading, router])

    useEffect(() => {
        if (token) {
            fetchNotifications()
        }
    }, [token])

    // 남은 체험 일수 계산
    const getRemainingTrialDays = () => {
        if (!user || !user.trial_end_date) return 0;
        const endDate = new Date(user.trial_end_date);
        const now = new Date();
        const diffTime = endDate.getTime() - now.getTime();
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
        return diffDays > 0 ? diffDays : 0;
    }

    // 구독 상태 배지 색상
    const getStatusBadgeColor = (status: string) => {
        switch (status) {
            case 'trial': return 'bg-blue-500 text-white';
            case 'active': return 'bg-green-500 text-white';
            case 'expired': return 'bg-red-500 text-white';
            default: return 'bg-gray-500 text-white';
        }
    }

    // 구독 상태 텍스트
    const getStatusText = (status: string) => {
        switch (status) {
            case 'trial': return '무료 체험 중';
            case 'active': return '구독 활성';
            case 'expired': return '체험 종료';
            default: return status;
        }
    }

    const fetchNotifications = async () => {
        try {
            const res = await axios.get(`${API_URL}/notifications/my`)
            setNotifications(res.data)
        } catch (err) {
            console.error(err)
        }
    }

    const markAsRead = async (id: number) => {
        try {
            await axios.put(`${API_URL}/notifications/${id}/read`)
            fetchNotifications()
        } catch (err) {
            console.error(err)
        }
    }

    const handlePayment = () => {
        if (!window.IMP) {
            alert("결제 모듈을 불러오는 중입니다. 잠시 후 다시 시도해주세요.");
            return;
        }

        const { IMP } = window;
        IMP.init('imp12345678');

        const today = new Date();
        const merchant_uid = `mid_${today.getTime()}`;

        IMP.request_pay({
            pg: 'html5_inicis',
            pay_method: 'card',
            merchant_uid: merchant_uid,
            name: '파트너체인 월간 구독 (30일)',
            amount: 100,
            buyer_email: user?.email,
            buyer_name: user?.username,
            buyer_tel: user?.phone_number,
            buyer_company: user?.company_name,
        }, async (rsp: any) => {
            if (rsp.success) {
                try {
                    await axios.post(`${API_URL}/payment/complete`, {
                        imp_uid: rsp.imp_uid,
                        merchant_uid: rsp.merchant_uid,
                        amount: rsp.paid_amount
                    });

                    alert('결제가 정상적으로 완료되었습니다!\\n알림함에서 라이선스 키를 확인하세요.');
                    fetchNotifications();
                } catch (err: any) {
                    alert('결제는 완료되었으나 서버 검증에 실패했습니다.\\n고객센터에 문의해주세요.\\n' + (err.response?.data?.detail || err.message));
                }
            } else {
                alert('결제에 실패하였습니다.\\n' + (rsp.error_msg || '알 수 없는 오류'));
            }
        });
    }

    const handleDownload = () => {
        // 실제 봇 파일 다운로드 링크 (public 폴더에 파일 배치 필요)
        const link = document.createElement('a');
        link.href = '/downloads/NaverShop_Pro_v3.2.1.exe';
        link.download = 'NaverShop_Pro_v3.2.1.exe';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }

    if (loading) {
        return (
            <div className="flex min-h-screen items-center justify-center">
                <p className="text-gray-900 text-lg font-medium">로딩 중...</p>
            </div>
        )
    }

    if (!user) return null

    const remainingDays = getRemainingTrialDays();

    return (
        <>
            <Script src="https://cdn.iamport.kr/v1/iamport.js" strategy="afterInteractive" />
            <div className="min-h-screen bg-gray-50 py-8">
                <div className="container mx-auto px-4">
                    <div className="mb-8">
                        <h1 className="text-3xl font-bold text-gray-900">
                            안녕하세요, {user.username}님! 👋
                        </h1>
                        <p className="text-gray-700 mt-2 font-medium">대시보드에 오신 것을 환영합니다.</p>
                    </div>

                    {/* 무료 체험 정보 카드 */}
                    {user.subscription_status === 'trial' && (
                        <Card className="mb-8 border-2 border-blue-300 bg-gradient-to-r from-blue-50 to-indigo-50">
                            <CardHeader>
                                <div className="flex items-center justify-between">
                                    <div>
                                        <CardTitle className="text-xl text-gray-900">🎉 무료 체험 중</CardTitle>
                                        <CardDescription className="text-gray-800 mt-1 font-medium">
                                            {remainingDays > 0 ? (
                                                <span className="font-bold text-blue-700">
                                                    남은 기간: {remainingDays}일
                                                </span>
                                            ) : (
                                                <span className="font-bold text-red-700">
                                                    체험 기간이 만료되었습니다
                                                </span>
                                            )}
                                        </CardDescription>
                                    </div>
                                    <Badge className={getStatusBadgeColor(user.subscription_status)}>
                                        {getStatusText(user.subscription_status)}
                                    </Badge>
                                </div>
                            </CardHeader>
                            <CardContent>
                                <p className="text-sm text-gray-800 mb-4 font-medium">
                                    무료 체험 기간 동안 모든 기능을 자유롭게 사용해보세요!
                                </p>
                                {remainingDays === 0 && (
                                    <Button onClick={handlePayment} className="w-full bg-blue-600 hover:bg-blue-700">
                                        지금 구독하기
                                    </Button>
                                )}
                            </CardContent>
                        </Card>
                    )}

                    {user.subscription_status === 'active' && (
                        <Card className="mb-8 border-2 border-green-300 bg-gradient-to-r from-green-50 to-teal-50">
                            <CardHeader>
                                <div className="flex items-center justify-between">
                                    <CardTitle className="text-xl text-gray-900">✅ 구독 활성</CardTitle>
                                    <Badge className={getStatusBadgeColor(user.subscription_status)}>
                                        {getStatusText(user.subscription_status)}
                                    </Badge>
                                </div>
                            </CardHeader>
                            <CardContent>
                                <p className="text-sm text-gray-800 font-medium">
                                    프리미엄 기능을 모두 이용하실 수 있습니다!
                                </p>
                            </CardContent>
                        </Card>
                    )}

                    <div className="grid gap-8 md:grid-cols-2">
                        {/* User Profile */}
                        <Card className="border-2">
                            <CardHeader>
                                <CardTitle className="text-gray-900">내 정보</CardTitle>
                                <CardDescription className="text-gray-700">계정 및 비즈니스 정보</CardDescription>
                            </CardHeader>
                            <CardContent className="space-y-2">
                                <div className="flex justify-between border-b pb-2">
                                    <span className="font-semibold text-gray-900">아이디</span>
                                    <span className="text-gray-900">{user.username}</span>
                                </div>
                                <div className="flex justify-between border-b pb-2">
                                    <span className="font-semibold text-gray-900">회사명</span>
                                    <span className="text-gray-900">{user.company_name}</span>
                                </div>
                                <div className="flex justify-between border-b pb-2">
                                    <span className="font-semibold text-gray-900">담당자</span>
                                    <span className="text-gray-900">{user.contact_name}</span>
                                </div>
                                <div className="flex justify-between border-b pb-2">
                                    <span className="font-semibold text-gray-900">이메일</span>
                                    <span className="text-gray-900">{user.email}</span>
                                </div>
                            </CardContent>
                        </Card>

                        {/* Subscription & Download */}
                        <Card className="border-2">
                            <CardHeader>
                                <CardTitle className="text-gray-900">구독 및 다운로드</CardTitle>
                                <CardDescription className="text-gray-700">봇 이용 현황</CardDescription>
                            </CardHeader>
                            <CardContent className="space-y-4">
                                <div className="flex items-center justify-between">
                                    <span className="font-semibold text-gray-900">구독 상태</span>
                                    <Badge className={getStatusBadgeColor(user.subscription_status)}>
                                        {getStatusText(user.subscription_status)}
                                    </Badge>
                                </div>
                                <div className="rounded-lg bg-gray-100 p-4 text-sm text-gray-900 font-medium">
                                    {user.subscription_status === 'trial' && `현재 무료 체험 중입니다. (${remainingDays}일 남음)`}
                                    {user.subscription_status === 'active' && '정식 구독 중입니다.'}
                                    {user.subscription_status === 'expired' && '체험 기간이 만료되었습니다. 구독을 연장해주세요.'}
                                </div>
                                <div className="flex gap-2">
                                    <Button
                                        className="flex-1 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white border-0"
                                        onClick={handlePayment}
                                    >
                                        💳 구독 연장 (100원 결제)
                                    </Button>
                                    <Button
                                        variant="outline"
                                        className="flex-1 border-2 border-gray-900 text-gray-900 hover:bg-gray-900 hover:text-white font-semibold"
                                        onClick={handleDownload}
                                    >
                                        ⬇️ 봇 다운로드
                                    </Button>
                                </div>
                            </CardContent>
                        </Card>
                    </div>

                    {/* Notification Center */}
                    <Card className="mt-8 border-2">
                        <CardHeader>
                            <CardTitle className="text-gray-900">알림함 (Mailbox)</CardTitle>
                            <CardDescription className="text-gray-700">시리얼 키 발급 및 중요 공지사항</CardDescription>
                        </CardHeader>
                        <CardContent>
                            {notifications.length === 0 ? (
                                <div className="text-center text-gray-600 py-8 font-medium">받은 메시지가 없습니다.</div>
                            ) : (
                                <div className="space-y-4">
                                    {notifications.map((noti) => (
                                        <div key={noti.id} className={`p-4 rounded-lg border-2 ${noti.is_read ? 'bg-gray-50 border-gray-200' : 'bg-blue-50 border-blue-300'}`}>
                                            <div className="flex justify-between items-start mb-2">
                                                <h4 className="font-bold text-lg text-gray-900">
                                                    {noti.title} {!noti.is_read && <Badge className="ml-2 bg-red-500">NEW</Badge>}
                                                </h4>
                                                <span className="text-xs text-gray-600 font-medium">{new Date(noti.created_at).toLocaleString()}</span>
                                            </div>
                                            <p className="whitespace-pre-wrap text-sm text-gray-900">{noti.content}</p>
                                            {!noti.is_read && (
                                                <Button size="sm" variant="ghost" className="mt-2 text-blue-600 font-semibold" onClick={() => markAsRead(noti.id)}>
                                                    읽음 표시
                                                </Button>
                                            )}
                                        </div>
                                    ))}
                                </div>
                            )}
                        </CardContent>
                    </Card>
                </div>
            </div>
        </>
    )
}
