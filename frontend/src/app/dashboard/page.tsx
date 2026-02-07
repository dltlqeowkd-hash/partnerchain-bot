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
            case 'trial': return 'bg-blue-100 text-blue-800';
            case 'active': return 'bg-green-100 text-green-800';
            case 'expired': return 'bg-red-100 text-red-800';
            default: return 'bg-gray-100 text-gray-800';
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

    if (loading) {
        return (
            <div className="flex min-h-screen items-center justify-center">
                <p className="text-gray-600">로딩 중...</p>
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
                        <p className="text-gray-600 mt-2">대시보드에 오신 것을 환영합니다.</p>
                    </div>

                    {/* 무료 체험 정보 카드 */}
                    {user.subscription_status === 'trial' && (
                        <Card className="mb-8 border-2 border-blue-200 bg-gradient-to-r from-blue-50 to-indigo-50">
                            <CardHeader>
                                <div className="flex items-center justify-between">
                                    <div>
                                        <CardTitle className="text-xl text-gray-900">🎉 무료 체험 중</CardTitle>
                                        <CardDescription className="text-gray-700 mt-1">
                                            {remainingDays > 0 ? (
                                                <span className="font-semibold text-blue-700">
                                                    남은 기간: {remainingDays}일
                                                </span>
                                            ) : (
                                                <span className="font-semibold text-red-700">
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
                                <p className="text-sm text-gray-700 mb-4">
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
                        <Card className="mb-8 border-2 border-green-200 bg-gradient-to-r from-green-50 to-teal-50">
                            <CardHeader>
                                <div className="flex items-center justify-between">
                                    <CardTitle className="text-xl text-gray-900">✅ 구독 활성</CardTitle>
                                    <Badge className={getStatusBadgeColor(user.subscription_status)}>
                                        {getStatusText(user.subscription_status)}
                                    </Badge>
                                </div>
                            </CardHeader>
                            <CardContent>
                                <p className="text-sm text-gray-700">
                                    프리미엄 기능을 모두 이용하실 수 있습니다!
                                </p>
                            </CardContent>
                        </Card>
                    )}

                    <div className="grid gap-8 md:grid-cols-2">
                        {/* User Profile */}
                        <Card>
                            <CardHeader>
                                <CardTitle>내 정보</CardTitle>
                                <CardDescription>계정 및 비즈니스 정보</CardDescription>
                            </CardHeader>
                            <CardContent className="space-y-2">
                                <div className="flex justify-between border-b pb-2">
                                    <span className="font-medium">아이디</span>
                                    <span>{user.username}</span>
                                </div>
                                <div className="flex justify-between border-b pb-2">
                                    <span className="font-medium">회사명</span>
                                    <span>{user.company_name}</span>
                                </div>
                                <div className="flex justify-between border-b pb-2">
                                    <span className="font-medium">담당자</span>
                                    <span>{user.contact_name}</span>
                                </div>
                                <div className="flex justify-between border-b pb-2">
                                    <span className="font-medium">이메일</span>
                                    <span>{user.email}</span>
                                </div>
                            </CardContent>
                        </Card>

                        {/* Subscription & Download */}
                        <Card>
                            <CardHeader>
                                <CardTitle>구독 및 다운로드</CardTitle>
                                <CardDescription>봇 이용 현황</CardDescription>
                            </CardHeader>
                            <CardContent className="space-y-4">
                                <div className="flex items-center justify-between">
                                    <span className="font-medium">구독 상태</span>
                                    <Badge className={getStatusBadgeColor(user.subscription_status)}>
                                        {getStatusText(user.subscription_status)}
                                    </Badge>
                                </div>
                                <div className="rounded-lg bg-gray-100 p-4 text-sm text-gray-600">
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
                                    <Button variant="outline" className="flex-1" onClick={() => router.push('/download/naver-shopping-bot')}>
                                        ⬇️ 봇 다운로드
                                    </Button>
                                </div>
                            </CardContent>
                        </Card>
                    </div>

                    {/* Notification Center */}
                    <Card className="mt-8">
                        <CardHeader>
                            <CardTitle>알림함 (Mailbox)</CardTitle>
                            <CardDescription>시리얼 키 발급 및 중요 공지사항</CardDescription>
                        </CardHeader>
                        <CardContent>
                            {notifications.length === 0 ? (
                                <div className="text-center text-muted-foreground py-8">받은 메시지가 없습니다.</div>
                            ) : (
                                <div className="space-y-4">
                                    {notifications.map((noti) => (
                                        <div key={noti.id} className={`p-4 rounded-lg border ${noti.is_read ? 'bg-gray-50' : 'bg-blue-50 border-blue-200'}`}>
                                            <div className="flex justify-between items-start mb-2">
                                                <h4 className="font-bold text-lg">
                                                    {noti.title} {!noti.is_read && <Badge className="ml-2 bg-red-500">NEW</Badge>}
                                                </h4>
                                                <span className="text-xs text-gray-500">{new Date(noti.created_at).toLocaleString()}</span>
                                            </div>
                                            <p className="whitespace-pre-wrap text-sm text-gray-700">{noti.content}</p>
                                            {!noti.is_read && (
                                                <Button size="sm" variant="ghost" className="mt-2 text-blue-600" onClick={() => markAsRead(noti.id)}>
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
