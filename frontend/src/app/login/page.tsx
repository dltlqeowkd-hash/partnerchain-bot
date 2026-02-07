'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import axios from 'axios'
import { useAuth } from '@/contexts/auth-context'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function LoginPage() {
    const [username, setUsername] = useState('')
    const [password, setPassword] = useState('')
    const [error, setError] = useState('')
    const { login } = useAuth()
    const router = useRouter()

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        setError('')
        try {
            const formData = new FormData()
            formData.append('username', username)
            formData.append('password', password)

            const res = await axios.post(`${API_URL}/token`, formData)
            const token = res.data.access_token

            const userRes = await axios.get(`${API_URL}/users/me`, {
                headers: { Authorization: `Bearer ${token}` }
            })

            login(token, userRes.data)
            router.push('/dashboard')
        } catch (err: any) {
            let msg = '로그인 실패: 아이디 또는 비밀번호를 확인하세요.'
            if (err.code === 'ERR_NETWORK') {
                msg = '⚠️ 서버에 연결할 수 없습니다. 백엔드 서버가 실행 중인지 확인하세요. (uvicorn app.main:app)'
            }
            setError(msg)
            console.error(err)
        }
    }

    return (
        <div className="flex min-h-[calc(100vh-4rem)] items-center justify-center bg-gradient-to-br from-blue-50 via-white to-indigo-50 px-4 py-12 sm:px-6 lg:px-8">
            <Card className="w-full max-w-md shadow-2xl border-0">
                <CardHeader className="space-y-1 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-t-lg">
                    <CardTitle className="text-3xl font-bold text-center">로그인</CardTitle>
                    <CardDescription className="text-center text-blue-100">
                        PartnerChain 서비스에 로그인하세요
                    </CardDescription>
                </CardHeader>
                <form onSubmit={handleSubmit}>
                    <CardContent className="space-y-6 pt-8">
                        {error && (
                            <div className="text-sm text-red-700 font-medium bg-red-50 border-l-4 border-red-500 p-4 rounded">
                                {error}
                            </div>
                        )}

                        <div className="space-y-2">
                            <label htmlFor="username" className="text-sm font-semibold text-gray-900">
                                아이디
                            </label>
                            <Input
                                id="username"
                                type="text"
                                value={username}
                                onChange={(e) => setUsername(e.target.value)}
                                required
                                className="text-gray-900 border-gray-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-200"
                            />
                        </div>

                        <div className="space-y-2">
                            <label htmlFor="password" className="text-sm font-semibold text-gray-900">
                                비밀번호
                            </label>
                            <Input
                                id="password"
                                type="password"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                required
                                className="text-gray-900 border-gray-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-200"
                            />
                        </div>
                    </CardContent>

                    <CardFooter className="flex flex-col space-y-4 pb-6">
                        <Button
                            type="submit"
                            className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-bold py-6 text-lg shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-200"
                        >
                            🔐 로그인
                        </Button>

                        <div className="text-sm text-center text-gray-600">
                            계정이 없으신가요?{' '}
                            <Link href="/signup" className="text-blue-600 hover:text-indigo-600 font-bold hover:underline">
                                회원가입
                            </Link>
                        </div>
                    </CardFooter>
                </form>
            </Card>
        </div>
    )
}
