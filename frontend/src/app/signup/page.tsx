'use client'

import React, { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import axios from 'axios'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'

// 환경 변수에서 API 주소 가져오기 (없으면 localhost 사용)
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function SignupPage() {
    const [formData, setFormData] = useState({
        username: '',
        email: '',
        password: '',
        confirmPassword: '',
        contact_name: '',
        phone_number: '',
        company_name: '',
        business_number: ''
    })
    const [error, setError] = useState('')
    const router = useRouter()

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setFormData({ ...formData, [e.target.id]: e.target.value })
    }

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        setError('')

        if (formData.password !== formData.confirmPassword) {
            setError('비밀번호가 일치하지 않습니다.')
            return
        }

        try {
            await axios.post(`${API_URL}/signup`, {
                username: formData.username,
                email: formData.email,
                password: formData.password,
                contact_name: formData.contact_name,
                phone_number: formData.phone_number,
                company_name: formData.company_name,
                business_number: formData.business_number || null
            })

            alert('회원가입이 완료되었습니다. 로그인해주세요.')
            router.push('/login')
        } catch (err: any) {
            let msg = '회원가입 중 오류가 발생했습니다.'
            if (err.code === 'ERR_NETWORK') {
                msg = '⚠️ 서버에 연결할 수 없습니다. 백엔드 서버가 실행 중인지 확인하세요. (uvicorn app.main:app)'
            } else if (err.response?.data?.detail) {
                msg = err.response.data.detail
            }
            setError(typeof msg === 'string' ? msg : JSON.stringify(msg))
            console.error('회원가입 오류:', err)
        }
    }

    return (
        <div className="flex min-h-[calc(100vh-4rem)] items-center justify-center bg-gradient-to-br from-blue-50 via-white to-purple-50 px-4 py-12 sm:px-6 lg:px-8">
            <Card className="w-full max-w-lg shadow-2xl border-0">
                <CardHeader className="space-y-1 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-t-lg">
                    <CardTitle className="text-3xl font-bold text-center">회원가입</CardTitle>
                    <CardDescription className="text-center text-blue-100">
                        비즈니스 파트너로 함께하세요
                    </CardDescription>
                </CardHeader>
                <form onSubmit={handleSubmit}>
                    <CardContent className="space-y-4 pt-6">
                        {error && (
                            <div className="text-sm text-red-700 font-medium bg-red-50 border-l-4 border-red-500 p-4 rounded">
                                {error}
                            </div>
                        )}

                        <div className="grid grid-cols-2 gap-4">
                            <div className="space-y-2">
                                <label htmlFor="username" className="text-sm font-semibold text-gray-900">아이디 *</label>
                                <Input id="username" value={formData.username} onChange={handleChange} required className="text-gray-900 border-gray-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-200" />
                            </div>
                            <div className="space-y-2">
                                <label htmlFor="email" className="text-sm font-semibold text-gray-900">이메일 *</label>
                                <Input id="email" type="email" value={formData.email} onChange={handleChange} required className="text-gray-900 border-gray-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-200" />
                            </div>
                        </div>

                        <div className="grid grid-cols-2 gap-4">
                            <div className="space-y-2">
                                <label htmlFor="password" className="text-sm font-semibold text-gray-900">비밀번호 *</label>
                                <Input id="password" type="password" value={formData.password} onChange={handleChange} required className="text-gray-900 border-gray-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-200" />
                            </div>
                            <div className="space-y-2">
                                <label htmlFor="confirmPassword" className="text-sm font-semibold text-gray-900">비밀번호 확인 *</label>
                                <Input id="confirmPassword" type="password" value={formData.confirmPassword} onChange={handleChange} required className="text-gray-900 border-gray-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-200" />
                            </div>
                        </div>

                        <div className="space-y-2">
                            <label htmlFor="company_name" className="text-sm font-semibold text-gray-900">회사명/상호 *</label>
                            <Input id="company_name" value={formData.company_name} onChange={handleChange} required className="text-gray-900 border-gray-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-200" />
                        </div>

                        <div className="grid grid-cols-2 gap-4">
                            <div className="space-y-2">
                                <label htmlFor="contact_name" className="text-sm font-semibold text-gray-900">담당자명 *</label>
                                <Input id="contact_name" value={formData.contact_name} onChange={handleChange} required className="text-gray-900 border-gray-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-200" />
                            </div>
                            <div className="space-y-2">
                                <label htmlFor="phone_number" className="text-sm font-semibold text-gray-900">연락처 *</label>
                                <Input id="phone_number" value={formData.phone_number} onChange={handleChange} required className="text-gray-900 border-gray-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-200" />
                            </div>
                        </div>

                        <div className="space-y-2">
                            <label htmlFor="business_number" className="text-sm font-semibold text-gray-900">사업자등록번호 (선택)</label>
                            <Input id="business_number" value={formData.business_number} onChange={handleChange} placeholder="000-00-00000" className="text-gray-900 border-gray-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-200" />
                        </div>

                    </CardContent>
                    <CardFooter className="flex flex-col space-y-4 pb-6">
                        <Button
                            type="submit"
                            className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-bold py-6 text-lg shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-200"
                        >
                            🚀 가입하기
                        </Button>
                        <div className="text-sm text-center text-gray-600">
                            이미 계정이 있으신가요?{' '}
                            <Link href="/login" className="text-blue-600 hover:text-purple-600 font-bold hover:underline">
                                로그인
                            </Link>
                        </div>
                    </CardFooter>
                </form>
            </Card>
        </div>
    )
}
