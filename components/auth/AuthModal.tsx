"use client"

import { useState } from 'react'
import { createClientComponentClient } from '@supabase/auth-helpers-nextjs'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Loader2, CheckCircle2, AlertCircle } from 'lucide-react'
import { cn } from "@/lib/utils"

interface AuthModalProps {
    isOpen: boolean
    onClose: () => void
}

type AuthView = 'sign_in' | 'sign_up'

export default function AuthModal({ isOpen, onClose }: AuthModalProps) {
    const supabase = createClientComponentClient()
    const [view, setView] = useState<AuthView>('sign_in')
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState<string | null>(null)
    const [successMessage, setSuccessMessage] = useState<string | null>(null)

    // Form states
    const [fullName, setFullName] = useState('')
    const [email, setEmail] = useState('')
    const [password, setPassword] = useState('')
    const [confirmPassword, setConfirmPassword] = useState('')

    const resetForm = () => {
        setError(null)
        setSuccessMessage(null)
        setFullName('')
        setEmail('')
        setPassword('')
        setConfirmPassword('')
    }

    const toggleView = () => {
        setView(view === 'sign_in' ? 'sign_up' : 'sign_in')
        resetForm()
    }

    const handleSignUp = async (e: React.FormEvent) => {
        e.preventDefault()
        setError(null)
        setLoading(true)

        if (password !== confirmPassword) {
            setError("Passwords do not match")
            setLoading(false)
            return
        }

        try {
            const { error } = await supabase.auth.signUp({
                email,
                password,
                options: {
                    data: {
                        full_name: fullName,
                    },
                    emailRedirectTo: `${window.location.origin}/auth/callback`,
                },
            })

            if (error) throw error

            setSuccessMessage("Check your email for the confirmation link.")
        } catch (err: any) {
            setError(err.message)
        } finally {
            setLoading(false)
        }
    }

    const handleSignIn = async (e: React.FormEvent) => {
        e.preventDefault()
        setError(null)
        setLoading(true)

        try {
            const { error } = await supabase.auth.signInWithPassword({
                email,
                password,
            })

            if (error) throw error

            onClose()
            window.location.reload() // Refresh to update auth state
        } catch (err: any) {
            setError(err.message)
        } finally {
            setLoading(false)
        }
    }

    return (
        <Dialog open={isOpen} onOpenChange={(open) => {
            if (!open) resetForm()
            onClose()
        }}>
            <DialogContent className="sm:max-w-md bg-white border-t-4 border-t-emerald-500 shadow-2xl">
                <DialogHeader>
                    <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-emerald-100">
                        <CheckCircle2 className="h-6 w-6 text-emerald-600" />
                    </div>
                    <DialogTitle className="text-center text-2xl font-bold text-gray-900">
                        {view === 'sign_in' ? 'Welcome Back' : 'Create Account'}
                    </DialogTitle>
                    <DialogDescription className="text-center text-gray-500">
                        {view === 'sign_in'
                            ? 'Enter your credentials to access your account'
                            : 'Sign up to start using Masterpost.io'}
                    </DialogDescription>
                </DialogHeader>

                <div className="flex flex-col space-y-4 py-4">
                    {/* Decorative Line */}
                    <div className="w-full h-1 bg-gradient-to-r from-emerald-200 via-emerald-400 to-emerald-200 rounded-full opacity-50 mb-2" />

                    {error && (
                        <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-md flex items-center gap-2 text-sm">
                            <AlertCircle className="h-4 w-4" />
                            {error}
                        </div>
                    )}

                    {successMessage && (
                        <div className="bg-emerald-50 border border-emerald-200 text-emerald-600 px-4 py-3 rounded-md flex items-center gap-2 text-sm">
                            <CheckCircle2 className="h-4 w-4" />
                            {successMessage}
                        </div>
                    )}

                    <form onSubmit={view === 'sign_in' ? handleSignIn : handleSignUp} className="space-y-4">
                        {view === 'sign_up' && (
                            <div className="space-y-2">
                                <Label htmlFor="fullName">Full Name</Label>
                                <Input
                                    id="fullName"
                                    placeholder="John Doe"
                                    value={fullName}
                                    onChange={(e) => setFullName(e.target.value)}
                                    required
                                    className="focus-visible:outline-none focus-visible:border-green-500 focus-visible:ring-1 focus-visible:ring-green-500 transition-colors duration-200"
                                />
                            </div>
                        )}

                        <div className="space-y-2">
                            <Label htmlFor="email">Email</Label>
                            <Input
                                id="email"
                                type="email"
                                placeholder="name@example.com"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                required
                                className="focus-visible:outline-none focus-visible:border-green-500 focus-visible:ring-1 focus-visible:ring-green-500 transition-colors duration-200"
                            />
                        </div>

                        <div className="space-y-2">
                            <Label htmlFor="password">Password</Label>
                            <Input
                                id="password"
                                type="password"
                                placeholder="••••••••"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                required
                                className="focus-visible:outline-none focus-visible:border-green-500 focus-visible:ring-1 focus-visible:ring-green-500 transition-colors duration-200"
                            />
                        </div>

                        {view === 'sign_up' && (
                            <div className="space-y-2">
                                <Label htmlFor="confirmPassword">Confirm Password</Label>
                                <Input
                                    id="confirmPassword"
                                    type="password"
                                    placeholder="••••••••"
                                    value={confirmPassword}
                                    onChange={(e) => setConfirmPassword(e.target.value)}
                                    required
                                    className="focus-visible:outline-none focus-visible:border-green-500 focus-visible:ring-1 focus-visible:ring-green-500 transition-colors duration-200"
                                />
                            </div>
                        )}

                        <Button
                            type="submit"
                            className="w-full bg-emerald-600 hover:bg-emerald-700 text-white font-semibold shadow-md hover:shadow-lg transition-all duration-300 relative overflow-hidden group"
                            disabled={loading}
                        >
                            {loading ? (
                                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                            ) : (
                                <span className="relative z-10">{view === 'sign_in' ? 'Sign In' : 'Sign Up'}</span>
                            )}
                            {/* Subtle yellow sheen on hover */}
                            <div className="absolute inset-0 h-full w-full scale-0 rounded-md transition-all duration-300 group-hover:scale-100 group-hover:bg-emerald-400/10" />
                        </Button>
                    </form>

                    <div className="text-center text-sm">
                        <span className="text-gray-500">
                            {view === 'sign_in' ? "Don't have an account? " : "Already have an account? "}
                        </span>
                        <button
                            onClick={toggleView}
                            className="font-semibold text-emerald-600 hover:text-emerald-500 hover:underline transition-colors"
                        >
                            {view === 'sign_in' ? 'Sign up' : 'Sign in'}
                        </button>
                    </div>
                </div>
            </DialogContent>
        </Dialog>
    )
}
