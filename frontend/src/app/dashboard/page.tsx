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
        IMP.init('imp12345678'); // 테스트용 가맹점 식별코드

        const today = new Date();
        const merchant_uid = `mid_${today.getTime()}`;

        IMP.request_pay({
            pg: 'html5_inicis',
            pay_method: 'card',
            merchant_uid: merchant_uid, // 상점에서 관리하는 주문 번호
            name: '파트너체인 월간 구독 (30일)',
            amount: 100, // 테스트 결제 금액
            buyer_email: user?.email,
            buyer_name: user?.username,
            buyer_tel: user?.phone_number,
            buyer_company: user?.company_name,
        }, async (rsp: any) => {
            if (rsp.success) {
                try {
                    // 백엔드 검증 및 라이선스 발급 요청
                    await axios.post(`${API_URL}/payment/complete`, {
                        imp_uid: rsp.imp_uid,
                        merchant_uid: rsp.merchant_uid,
                        amount: rsp.paid_amount
                    });

                    alert('결제가 정상적으로 완료되었습니다!\n알림함에서 라이선스 키를 확인하세요.');
                    fetchNotifications(); // 알림함 갱신
                } catch (err: any) {
                    alert('결제는 완료되었으나 서버 검증에 실패했습니다.\n고객센터에 문의해주세요.\n' + (err.response?.data?.detail || err.message));
                }
            } else {
                alert('결제에 실패하였습니다.\n' + rsp.error_msg);
            }
        });
    }

    if (loading || !user) return <div className="p-8 text-center">Loading...</div>

    return (
        <div className="container mx-auto p-4 space-y-8">
            <Script src="https://cdn.iamport.kr/v1/iamport.js" />

            <h1 className="text-3xl font-bold">대시보드</h1>

            <div className="grid gap-6 md:grid-cols-2">
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
                            <Badge variant="default" className="bg-green-500">Active (Trial)</Badge>
                        </div>
                        <div className="rounded-lg bg-gray-100 p-4 text-sm text-gray-600">
                            현재 체험판 라이선스를 이용 중입니다. (100원 테스트 결제 가능)
                            <br />
                            정식 버전을 이용하시려면 구독을 갱신해주세요.
                        </div>
                        <div className="flex gap-2">
                            <Button className="flex-1 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white border-0" onClick={handlePayment}>
                                💳 구독 연장 (100원 결제)
                            </Button>
                            <Button variant="outline" className="flex-1" onClick={() => alert('봇 다운로드 링크 제공 예정')}>⬇️ 봇 다운로드</Button>
                        </div>
                    </CardContent>
                </Card>
            </div>

            {/* Notification Center (Mailbox) */}
            <Card>
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
                                        <h4 className="font-bold text-lg">{noti.title} {!noti.is_read && <Badge className="ml-2 bg-red-500">NEW</Badge>}</h4>
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
    )
}
