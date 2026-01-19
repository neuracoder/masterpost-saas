import Link from "next/link"
import Image from "next/image"
import { Clock, ArrowRight } from "lucide-react"
import { Card, CardContent, CardHeader } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { BlogPost } from "./BlogCard"

interface RelatedPostsProps {
  posts: BlogPost[]
  currentSlug: string
}

export default function RelatedPosts({ posts, currentSlug }: RelatedPostsProps) {
  // Filter out current post and limit to 3
  const relatedPosts = posts
    .filter(post => post.slug !== currentSlug)
    .slice(0, 3)

  if (relatedPosts.length === 0) return null

  return (
    <Card className="border-2 border-gray-100 sticky top-24 bg-white shadow-sm">
      <CardHeader className="pb-4">
        <h3 className="text-lg font-bold text-gray-900">Related Articles</h3>
      </CardHeader>
      <CardContent className="space-y-4">
        {relatedPosts.map((post) => (
          <Link key={post.slug} href={`/blog/${post.slug}`}>
            <div className="group flex gap-3 p-2 -mx-2 rounded-lg hover:bg-gray-50 transition-colors">
              <div className="relative w-16 h-16 flex-shrink-0 rounded-lg overflow-hidden">
                <Image
                  src={post.coverImage}
                  alt={post.title}
                  fill
                  className="object-cover group-hover:scale-105 transition-transform duration-300"
                />
              </div>
              <div className="flex-1 min-w-0">
                <h4 className="text-sm font-semibold text-gray-900 line-clamp-2 group-hover:text-green-600 transition-colors leading-tight">
                  {post.title}
                </h4>
                <div className="flex items-center gap-2 mt-1 text-xs text-gray-500">
                  <Clock className="w-3 h-3" />
                  {post.readingTime}
                </div>
              </div>
            </div>
          </Link>
        ))}

        <Link
          href="/blog"
          className="flex items-center justify-center gap-1 text-sm font-semibold text-green-600 hover:text-green-700 pt-4 border-t border-gray-100"
        >
          View all articles <ArrowRight className="w-4 h-4" />
        </Link>
      </CardContent>
    </Card>
  )
}

// Table of Contents Component
interface TOCItem {
  id: string
  text: string
  level: number
}

interface TableOfContentsProps {
  items: TOCItem[]
}

export function TableOfContents({ items }: TableOfContentsProps) {
  return (
    <Card className="border-2 border-gray-100 sticky top-24 bg-white shadow-sm">
      <CardHeader className="pb-3">
        <h3 className="text-lg font-bold text-gray-900">Table of Contents</h3>
      </CardHeader>
      <CardContent>
        <nav className="space-y-2">
          {items.map((item) => (
            <a
              key={item.id}
              href={`#${item.id}`}
              className={`block text-sm text-gray-600 hover:text-green-600 transition-colors ${
                item.level === 2 ? 'font-medium' : 'pl-4 text-gray-500'
              }`}
            >
              {item.text}
            </a>
          ))}
        </nav>
      </CardContent>
    </Card>
  )
}

// Newsletter CTA Sidebar Component
export function NewsletterSidebar() {
  return (
    <Card className="border-2 border-green-200 bg-gradient-to-br from-green-50 to-white">
      <CardContent className="p-6 space-y-4">
        <div className="text-center space-y-2">
          <Badge className="bg-green-100 text-green-700">Free Newsletter</Badge>
          <h3 className="text-lg font-bold text-gray-900">E-commerce Tips Weekly</h3>
          <p className="text-sm text-gray-600">
            Get the latest tips on product photography, image optimization, and marketplace compliance.
          </p>
        </div>
        <form className="space-y-3">
          <input
            type="email"
            placeholder="your@email.com"
            className="w-full px-4 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
          />
          <button
            type="submit"
            className="w-full bg-green-600 hover:bg-green-700 text-white font-semibold py-2 px-4 rounded-lg transition-colors text-sm"
          >
            Subscribe Free
          </button>
        </form>
        <p className="text-xs text-gray-500 text-center">
          No spam. Unsubscribe anytime.
        </p>
      </CardContent>
    </Card>
  )
}
