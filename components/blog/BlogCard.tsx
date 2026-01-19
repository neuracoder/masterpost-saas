import Link from "next/link"
import Image from "next/image"
import { Clock, Calendar, ArrowRight } from "lucide-react"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"

export interface BlogPost {
  title: string
  slug: string
  excerpt: string
  author: string
  date: string
  readingTime: string
  category: string
  tags: string[]
  featured: boolean
  coverImage: string
}

interface BlogCardProps {
  post: BlogPost
  featured?: boolean
}

export default function BlogCard({ post, featured = false }: BlogCardProps) {
  if (featured) {
    return (
      <Link href={`/blog/${post.slug}`}>
        <Card className="group overflow-hidden border-2 border-green-100 hover:border-green-300 transition-all duration-300 hover:shadow-xl bg-gradient-to-br from-green-50 to-white">
          <div className="grid md:grid-cols-2 gap-0">
            {/* Image */}
            <div className="relative h-64 md:h-full min-h-[300px] overflow-hidden">
              <Image
                src={post.coverImage}
                alt={post.title}
                fill
                className="object-cover group-hover:scale-105 transition-transform duration-500"
              />
              <div className="absolute top-4 left-4">
                <Badge className="bg-yellow-400 text-gray-900 font-bold">Featured</Badge>
              </div>
            </div>

            {/* Content */}
            <CardContent className="p-8 flex flex-col justify-center space-y-4">
              <div className="flex items-center gap-2 flex-wrap">
                <Badge variant="outline" className="border-green-300 text-green-700">
                  {post.category}
                </Badge>
                <div className="flex items-center text-sm text-gray-500">
                  <Calendar className="w-4 h-4 mr-1" />
                  {new Date(post.date).toLocaleDateString('en-US', {
                    month: 'short',
                    day: 'numeric',
                    year: 'numeric'
                  })}
                </div>
              </div>

              <h2 className="text-2xl md:text-3xl font-bold text-gray-900 group-hover:text-green-600 transition-colors leading-tight">
                {post.title}
              </h2>

              <p className="text-gray-600 leading-relaxed line-clamp-3">
                {post.excerpt}
              </p>

              <div className="flex items-center justify-between pt-4">
                <div className="flex items-center gap-4 text-sm text-gray-500">
                  <span className="font-medium text-gray-700">{post.author}</span>
                  <div className="flex items-center">
                    <Clock className="w-4 h-4 mr-1" />
                    {post.readingTime}
                  </div>
                </div>

                <span className="flex items-center text-green-600 font-semibold group-hover:translate-x-1 transition-transform">
                  Read more <ArrowRight className="w-4 h-4 ml-1" />
                </span>
              </div>
            </CardContent>
          </div>
        </Card>
      </Link>
    )
  }

  return (
    <Link href={`/blog/${post.slug}`}>
      <Card className="group h-full overflow-hidden border border-gray-200 hover:border-green-300 transition-all duration-300 hover:shadow-lg">
        {/* Image */}
        <div className="relative h-48 overflow-hidden">
          <Image
            src={post.coverImage}
            alt={post.title}
            fill
            className="object-cover group-hover:scale-105 transition-transform duration-500"
          />
          <div className="absolute top-3 left-3">
            <Badge variant="outline" className="bg-white/90 backdrop-blur-sm border-green-300 text-green-700 text-xs">
              {post.category}
            </Badge>
          </div>
        </div>

        {/* Content */}
        <CardContent className="p-5 space-y-3">
          <div className="flex items-center gap-3 text-xs text-gray-500">
            <div className="flex items-center">
              <Calendar className="w-3 h-3 mr-1" />
              {new Date(post.date).toLocaleDateString('en-US', {
                month: 'short',
                day: 'numeric',
                year: 'numeric'
              })}
            </div>
            <div className="flex items-center">
              <Clock className="w-3 h-3 mr-1" />
              {post.readingTime}
            </div>
          </div>

          <h3 className="text-lg font-bold text-gray-900 group-hover:text-green-600 transition-colors leading-tight line-clamp-2">
            {post.title}
          </h3>

          <p className="text-sm text-gray-600 line-clamp-2">
            {post.excerpt}
          </p>

          <div className="flex items-center justify-between pt-2">
            <span className="text-xs font-medium text-gray-700">{post.author}</span>
            <span className="flex items-center text-green-600 text-sm font-semibold group-hover:translate-x-1 transition-transform">
              Read <ArrowRight className="w-3 h-3 ml-1" />
            </span>
          </div>
        </CardContent>
      </Card>
    </Link>
  )
}
