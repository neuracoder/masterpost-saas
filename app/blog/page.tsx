"use client"

import { useState } from "react"
import Link from "next/link"
import { Search, ArrowRight } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import BlogCard from "@/components/blog/BlogCard"
import { getAllPosts, getAllCategories, getFeaturedPosts } from "@/lib/blog-data"

export default function BlogPage() {
  const [searchQuery, setSearchQuery] = useState("")
  const [activeCategory, setActiveCategory] = useState("All")

  const allPosts = getAllPosts()
  const categories = getAllCategories()
  const featuredPosts = getFeaturedPosts()

  // Filter posts
  const filteredPosts = allPosts.filter(post => {
    const matchesSearch =
      post.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      post.excerpt.toLowerCase().includes(searchQuery.toLowerCase()) ||
      post.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()))

    const matchesCategory = activeCategory === "All" || post.category === activeCategory

    return matchesSearch && matchesCategory
  })

  // Separate featured from regular posts for display
  // Only exclude the first featured post from the grid (the one shown as hero)
  const mainFeaturedPost = featuredPosts[0]
  const regularPosts = filteredPosts.filter(post => post.slug !== mainFeaturedPost?.slug)
  const displayFeatured = activeCategory === "All" && !searchQuery && featuredPosts.length > 0

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="bg-gradient-to-b from-green-50 to-white py-16 md:py-20">
        <div className="container mx-auto px-6">
          <div className="max-w-4xl mx-auto text-center space-y-6">
            <Badge className="bg-green-100 text-green-700 hover:bg-green-100 font-bold">
              Masterpost.io Blog
            </Badge>

            <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold text-gray-900 leading-tight">
              E-commerce Image{" "}
              <span className="text-green-600">Optimization Tips</span>
            </h1>

            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Expert guides on product photography, marketplace compliance, and image editing
              for Amazon, eBay, and beyond.
            </p>

            {/* Search Bar */}
            <div className="max-w-xl mx-auto pt-4">
              <div className="relative">
                <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                <input
                  type="text"
                  placeholder="Search articles..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-12 pr-4 py-3 border-2 border-gray-200 rounded-xl focus:outline-none focus:border-green-500 transition-colors text-gray-900"
                />
              </div>
            </div>

            {/* Category Filters */}
            <div className="flex flex-wrap justify-center gap-2 pt-4">
              {categories.map((category) => (
                <button
                  key={category}
                  onClick={() => setActiveCategory(category)}
                  className={`px-4 py-2 rounded-full text-sm font-medium transition-all ${
                    activeCategory === category
                      ? "bg-green-600 text-white shadow-lg shadow-green-500/25"
                      : "bg-white text-gray-600 border border-gray-200 hover:border-green-300 hover:text-green-600"
                  }`}
                >
                  {category}
                </button>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Blog Posts Grid */}
      <section className="py-16">
        <div className="container mx-auto px-6">
          {filteredPosts.length === 0 ? (
            <div className="text-center py-20">
              <p className="text-gray-500 text-lg mb-4">No articles found matching your search.</p>
              <Button
                variant="outline"
                onClick={() => {
                  setSearchQuery("")
                  setActiveCategory("All")
                }}
              >
                Clear filters
              </Button>
            </div>
          ) : (
            <div className="space-y-12">
              {/* Featured Post */}
              {displayFeatured && featuredPosts[0] && (
                <div className="mb-12">
                  <h2 className="text-sm font-bold text-gray-500 uppercase tracking-wider mb-6">
                    Featured Article
                  </h2>
                  <BlogCard post={featuredPosts[0]} featured />
                </div>
              )}

              {/* Regular Posts Grid */}
              {(displayFeatured ? regularPosts : filteredPosts).length > 0 && (
                <div>
                  <h2 className="text-sm font-bold text-gray-500 uppercase tracking-wider mb-6">
                    {displayFeatured ? "More Articles" : `${filteredPosts.length} Article${filteredPosts.length !== 1 ? 's' : ''}`}
                  </h2>
                  <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
                    {(displayFeatured ? regularPosts : filteredPosts).map((post) => (
                      <BlogCard key={post.slug} post={post} />
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* CTA Section */}
          <div className="mt-20 text-center">
            <div className="inline-block bg-gradient-to-r from-green-50 to-yellow-50 border-2 border-green-200 rounded-2xl p-8 md:p-12 max-w-3xl">
              <h3 className="text-2xl md:text-3xl font-bold text-gray-900 mb-4">
                Ready to Optimize Your Product Images?
              </h3>
              <p className="text-gray-600 mb-6 max-w-xl mx-auto">
                Stop struggling with image compliance. Masterpost.io processes your product
                images in seconds with AI-powered background removal.
              </p>
              <Link href="/app">
                <Button
                  size="lg"
                  className="bg-green-600 hover:bg-green-700 text-white shadow-lg shadow-green-500/25 font-bold"
                >
                  Try 10 Images Free
                  <ArrowRight className="w-5 h-5 ml-2" />
                </Button>
              </Link>
              <p className="text-sm text-gray-500 mt-4">
                No credit card required • 72% cheaper than competitors
              </p>
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}
