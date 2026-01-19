"use client"

import { useState } from "react"
import Image from "next/image"
import Link from "next/link"
import { Clock, Calendar, User, Share2, Twitter, Linkedin, Facebook, Link2, Check } from "lucide-react"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from "@/components/ui/breadcrumb"

interface BlogHeaderProps {
  title: string
  excerpt: string
  author: string
  date: string
  readingTime: string
  category: string
  tags: string[]
  coverImage: string
  slug: string
}

export default function BlogHeader({
  title,
  excerpt,
  author,
  date,
  readingTime,
  category,
  tags,
  coverImage,
  slug
}: BlogHeaderProps) {
  const [copied, setCopied] = useState(false)
  const articleUrl = `https://masterpost.io/blog/${slug}`

  const shareOnTwitter = () => {
    window.open(
      `https://twitter.com/intent/tweet?text=${encodeURIComponent(title)}&url=${encodeURIComponent(articleUrl)}`,
      '_blank'
    )
  }

  const shareOnLinkedIn = () => {
    window.open(
      `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(articleUrl)}`,
      '_blank'
    )
  }

  const shareOnFacebook = () => {
    window.open(
      `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(articleUrl)}`,
      '_blank'
    )
  }

  const copyLink = async () => {
    await navigator.clipboard.writeText(articleUrl)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <header className="mb-12">
      {/* Breadcrumbs */}
      <Breadcrumb className="mb-6">
        <BreadcrumbList>
          <BreadcrumbItem>
            <BreadcrumbLink asChild>
              <Link href="/" className="text-gray-500 hover:text-green-600">Home</Link>
            </BreadcrumbLink>
          </BreadcrumbItem>
          <BreadcrumbSeparator />
          <BreadcrumbItem>
            <BreadcrumbLink asChild>
              <Link href="/blog" className="text-gray-500 hover:text-green-600">Blog</Link>
            </BreadcrumbLink>
          </BreadcrumbItem>
          <BreadcrumbSeparator />
          <BreadcrumbItem>
            <BreadcrumbPage className="text-gray-900 font-medium truncate max-w-[200px]">
              {title}
            </BreadcrumbPage>
          </BreadcrumbItem>
        </BreadcrumbList>
      </Breadcrumb>

      {/* Category & Tags */}
      <div className="flex items-center gap-2 flex-wrap mb-4">
        <Badge className="bg-green-100 text-green-700 hover:bg-green-100">
          {category}
        </Badge>
        {tags.slice(0, 3).map((tag) => (
          <Badge key={tag} variant="outline" className="text-gray-600 border-gray-300">
            {tag}
          </Badge>
        ))}
      </div>

      {/* Title */}
      <h1 className="text-3xl md:text-4xl lg:text-5xl font-bold text-gray-900 leading-tight mb-6">
        {title}
      </h1>

      {/* Excerpt */}
      <p className="text-xl text-gray-600 leading-relaxed mb-6">
        {excerpt}
      </p>

      {/* Meta Info */}
      <div className="flex flex-wrap items-center gap-6 pb-6 border-b border-gray-200">
        <div className="flex items-center gap-2">
          <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
            <User className="w-5 h-5 text-green-600" />
          </div>
          <div>
            <p className="font-semibold text-gray-900">{author}</p>
            <p className="text-sm text-gray-500">Author</p>
          </div>
        </div>

        <div className="flex items-center gap-4 text-sm text-gray-600">
          <div className="flex items-center gap-1">
            <Calendar className="w-4 h-4" />
            {new Date(date).toLocaleDateString('en-US', {
              month: 'long',
              day: 'numeric',
              year: 'numeric'
            })}
          </div>
          <div className="flex items-center gap-1">
            <Clock className="w-4 h-4" />
            {readingTime}
          </div>
        </div>

        {/* Share Buttons */}
        <div className="flex items-center gap-2 ml-auto">
          <span className="text-sm text-gray-500 flex items-center gap-1">
            <Share2 className="w-4 h-4" /> Share:
          </span>
          <Button
            variant="outline"
            size="icon"
            className="w-8 h-8 hover:bg-blue-50 hover:border-blue-300 hover:text-blue-600"
            onClick={shareOnTwitter}
          >
            <Twitter className="w-4 h-4" />
          </Button>
          <Button
            variant="outline"
            size="icon"
            className="w-8 h-8 hover:bg-blue-50 hover:border-blue-300 hover:text-blue-700"
            onClick={shareOnLinkedIn}
          >
            <Linkedin className="w-4 h-4" />
          </Button>
          <Button
            variant="outline"
            size="icon"
            className="w-8 h-8 hover:bg-blue-50 hover:border-blue-300 hover:text-blue-600"
            onClick={shareOnFacebook}
          >
            <Facebook className="w-4 h-4" />
          </Button>
          <Button
            variant="outline"
            size="icon"
            className="w-8 h-8 hover:bg-green-50 hover:border-green-300 hover:text-green-600"
            onClick={copyLink}
          >
            {copied ? <Check className="w-4 h-4 text-green-600" /> : <Link2 className="w-4 h-4" />}
          </Button>
        </div>
      </div>

      {/* Cover Image */}
      <div className="relative w-full aspect-video mt-8 rounded-2xl overflow-hidden shadow-xl">
        <Image
          src={coverImage}
          alt={title}
          fill
          className="object-cover"
          priority
        />
      </div>
    </header>
  )
}
