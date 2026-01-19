import { BlogPost } from "@/components/blog/BlogCard"

// Blog posts data - centralized for easy management
export const blogPosts: BlogPost[] = [
  {
    title: "Amazon Product Image Requirements 2026: Complete Compliance Guide",
    slug: "amazon-image-requirements-2026",
    excerpt: "Everything you need to know about Amazon's product image requirements. Learn exact specs, common rejection reasons, and how to ensure compliance.",
    author: "Masterpost.io",
    date: "2026-01-17",
    readingTime: "8 min read",
    category: "Amazon Selling",
    tags: ["Amazon FBA", "Product Images", "E-commerce", "Image Editing"],
    featured: true,
    coverImage: "/blog/amazon-requirements-cover.jpg",
  },
  {
    title: "eBay Product Image Requirements 2026: Complete Seller Guide",
    slug: "ebay-image-requirements-2026",
    excerpt: "Master eBay's photo requirements and best practices. Learn how to create product images that comply with eBay's guidelines and boost your sales.",
    author: "Masterpost.io",
    date: "2026-01-18",
    readingTime: "7 min read",
    category: "eBay Selling",
    tags: ["eBay", "Product Photography", "E-commerce", "Image Optimization"],
    featured: false,
    coverImage: "/blog/ebay-requirements-cover.jpg",
  },
  {
    title: "Instagram Shopping Image Requirements: Complete Guide for Sellers",
    slug: "instagram-product-images-guide",
    excerpt: "Complete guide to Instagram Shopping image requirements. Learn technical specs, best practices, and how to create product photos that convert.",
    author: "Masterpost.io",
    date: "2026-01-18",
    readingTime: "6 min read",
    category: "Social Commerce",
    tags: ["Instagram", "Social Selling", "Product Photography", "E-commerce"],
    featured: false,
    coverImage: "/blog/instagram-guide-cover.jpg",
  },
  {
    title: "How to Remove Image Backgrounds: Complete Guide for E-commerce (2026)",
    slug: "background-removal-guide",
    excerpt: "Complete guide to removing backgrounds from product images. Compare manual methods, AI tools, and automated solutions. Find the best approach for your business.",
    author: "Masterpost.io",
    date: "2026-01-18",
    readingTime: "7 min read",
    category: "Image Editing",
    tags: ["Background Removal", "Image Editing", "Product Photography", "AI Tools"],
    featured: true,
    coverImage: "/blog/background-removal-cover.jpg",
  },
]

// Get all posts
export function getAllPosts(): BlogPost[] {
  return blogPosts.sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime())
}

// Get featured posts
export function getFeaturedPosts(): BlogPost[] {
  return blogPosts.filter(post => post.featured)
}

// Get post by slug
export function getPostBySlug(slug: string): BlogPost | undefined {
  return blogPosts.find(post => post.slug === slug)
}

// Get posts by category
export function getPostsByCategory(category: string): BlogPost[] {
  return blogPosts.filter(post => post.category === category)
}

// Get all categories
export function getAllCategories(): string[] {
  const categories = new Set(blogPosts.map(post => post.category))
  return ['All', ...Array.from(categories)]
}

// Get related posts (by category, excluding current)
export function getRelatedPosts(currentSlug: string, limit: number = 3): BlogPost[] {
  const currentPost = getPostBySlug(currentSlug)
  if (!currentPost) return []

  return blogPosts
    .filter(post => post.slug !== currentSlug)
    .filter(post => post.category === currentPost.category || post.tags.some(tag => currentPost.tags.includes(tag)))
    .slice(0, limit)
}

// SEO metadata for the Amazon article
export const amazonArticleMetadata = {
  title: "Amazon Product Image Requirements 2026: Complete Compliance Guide",
  slug: "amazon-image-requirements-2026",
  excerpt: "Everything you need to know about Amazon's product image requirements. Learn exact specs, common rejection reasons, and how to ensure compliance.",
  author: "Masterpost.io",
  date: "2026-01-17",
  readingTime: "8 min read",
  category: "Amazon Selling",
  tags: ["Amazon FBA", "Product Images", "E-commerce", "Image Editing"],
  featured: true,
  coverImage: "/blog/amazon-requirements-cover.jpg",
  seo: {
    keywords: [
      "amazon product image requirements",
      "amazon image rejected",
      "amazon white background",
      "amazon product photo requirements 2026",
      "amazon main image requirements"
    ],
    ogTitle: "Amazon Product Image Requirements 2026: Complete Guide",
    ogDescription: "Master Amazon's strict image requirements. Learn exact specifications, avoid common mistakes, and ensure your product images meet compliance standards."
  }
}
