'use client'

import Link from 'next/link'
import { useAuth } from '@/contexts/auth-context'
import { Button } from '@/components/ui/button'
import { useState, useEffect, useRef } from 'react'

export function Navbar() {
    const { user, logout } = useAuth()
    const [showProductsMenu, setShowProductsMenu] = useState(false)
    const [showDownloadMenu, setShowDownloadMenu] = useState(false)
    const productsRef = useRef<HTMLDivElement>(null)
    const downloadRef = useRef<HTMLDivElement>(null)

    // 현재는 multi_bot (naver-shopping-bot)만 표시
    const products = [
        { id: 'naver-shopping-bot', name: 'NaverShop Pro', description: '네이버 쇼핑 자동화 봇' },
        // 추후 추가할 제품들 (현재는 숨김)
        // { id: 'blog-master-ai', name: 'BlogMaster AI', description: '네이버 블로그 자동 포스팅' },
        // { id: 'sourcing-bot', name: 'Sourcing Bot', description: '소싱 자동화 솔루션' },
    ]

    // 외부 클릭 감지하여 메뉴 닫기
    useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            if (productsRef.current && !productsRef.current.contains(event.target as Node)) {
                setShowProductsMenu(false)
            }
            if (downloadRef.current && !downloadRef.current.contains(event.target as Node)) {
                setShowDownloadMenu(false)
            }
        }

        document.addEventListener('mousedown', handleClickOutside)
        return () => {
            document.removeEventListener('mousedown', handleClickOutside)
        }
    }, [])

    const handleProductsClick = () => {
        setShowProductsMenu(!showProductsMenu)
        setShowDownloadMenu(false) // 다른 메뉴 닫기
    }

    const handleDownloadClick = () => {
        setShowDownloadMenu(!showDownloadMenu)
        setShowProductsMenu(false) // 다른 메뉴 닫기
    }

    return (
        <nav className="border-b bg-white shadow-sm sticky top-0 z-50">
            <div className="container mx-auto px-4">
                <div className="flex h-16 items-center justify-between">
                    <div className="flex items-center space-x-8">
                        <Link href="/" className="text-xl font-bold text-gray-900 hover:text-blue-600 transition">
                            PartnerChain.com
                        </Link>

                        <div className="hidden md:flex space-x-6">
                            {/* 회사소개 */}
                            <Link href="/about" className="text-sm font-medium text-gray-700 hover:text-blue-600 transition">
                                회사소개
                            </Link>

                            {/* 제품소개 (Click Dropdown) */}
                            <div className="relative" ref={productsRef}>
                                <button
                                    className="text-sm font-medium text-gray-700 hover:text-blue-600 transition flex items-center"
                                    onClick={handleProductsClick}
                                >
                                    제품소개
                                    <svg
                                        className={`ml-1 w-4 h-4 transition-transform duration-200 ${showProductsMenu ? 'rotate-180' : ''}`}
                                        fill="none"
                                        stroke="currentColor"
                                        viewBox="0 0 24 24"
                                    >
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                                    </svg>
                                </button>
                                {showProductsMenu && (
                                    <div className="absolute left-0 mt-2 w-56 bg-white border border-gray-200 rounded-md shadow-lg z-50">
                                        {products.map((product) => (
                                            <Link
                                                key={product.id}
                                                href={`/products/${product.id}`}
                                                className="block px-4 py-3 text-sm text-gray-700 hover:bg-blue-50 hover:text-blue-600 transition border-b last:border-b-0"
                                                onClick={() => setShowProductsMenu(false)}
                                            >
                                                <div className="font-semibold">{product.name}</div>
                                                <div className="text-xs text-gray-500">{product.description}</div>
                                            </Link>
                                        ))}
                                    </div>
                                )}
                            </div>

                            {/* 다운로드 (Click Dropdown) */}
                            <div className="relative" ref={downloadRef}>
                                <button
                                    className="text-sm font-medium text-gray-700 hover:text-blue-600 transition flex items-center"
                                    onClick={handleDownloadClick}
                                >
                                    다운로드
                                    <svg
                                        className={`ml-1 w-4 h-4 transition-transform duration-200 ${showDownloadMenu ? 'rotate-180' : ''}`}
                                        fill="none"
                                        stroke="currentColor"
                                        viewBox="0 0 24 24"
                                    >
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                                    </svg>
                                </button>
                                {showDownloadMenu && (
                                    <div className="absolute left-0 mt-2 w-56 bg-white border border-gray-200 rounded-md shadow-lg z-50">
                                        {products.map((product) => (
                                            <Link
                                                key={product.id}
                                                href={`/download/${product.id}`}
                                                className="block px-4 py-3 text-sm text-gray-700 hover:bg-blue-50 hover:text-blue-600 transition border-b last:border-b-0"
                                                onClick={() => setShowDownloadMenu(false)}
                                            >
                                                <div className="font-semibold">{product.name}</div>
                                                <div className="text-xs text-gray-500 flex items-center">
                                                    <svg className="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M9 19l3 3m0 0l3-3m-3 3V10" />
                                                    </svg>
                                                    프로그램 받기
                                                </div>
                                            </Link>
                                        ))}
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>

                    <div className="flex items-center space-x-4">
                        {user ? (
                            <>
                                <Link href="/dashboard">
                                    <Button variant="ghost" className="text-gray-700 hover:text-blue-600">대시보드</Button>
                                </Link>
                                <span className="text-sm text-gray-600">{user.username}</span>
                                <Button variant="outline" onClick={logout} className="text-gray-700 hover:text-red-600 border-gray-300">
                                    로그아웃
                                </Button>
                            </>
                        ) : (
                            <>
                                <Link href="/login">
                                    <Button variant="ghost" className="text-gray-700 hover:text-blue-600">로그인</Button>
                                </Link>
                                <Link href="/signup">
                                    <Button className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-semibold">
                                        회원가입
                                    </Button>
                                </Link>
                            </>
                        )}
                    </div>
                </div>
            </div>
        </nav>
    )
}
