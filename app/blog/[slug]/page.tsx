import { Metadata } from "next"
import { notFound } from "next/navigation"
import { getPostBySlug, getAllPosts, getRelatedPosts } from "@/lib/blog-data"
import BlogHeader from "@/components/blog/BlogHeader"
import RelatedPosts, { TableOfContents, NewsletterSidebar } from "@/components/blog/RelatedPosts"
import BlogCTA from "@/components/blog/BlogCTA"

// Import article components
import AmazonImageRequirements2026 from "../posts/amazon-image-requirements-2026"
import EbayImageRequirements2026 from "../posts/ebay-image-requirements-2026"
import InstagramProductImagesGuide from "../posts/instagram-product-images-guide"
import BackgroundRemovalGuide from "../posts/background-removal-guide"

// Map slugs to article components
const articleComponents: Record<string, React.ComponentType> = {
  "amazon-image-requirements-2026": AmazonImageRequirements2026,
  "ebay-image-requirements-2026": EbayImageRequirements2026,
  "instagram-product-images-guide": InstagramProductImagesGuide,
  "background-removal-guide": BackgroundRemovalGuide,
}

// Generate static params for all posts
export async function generateStaticParams() {
  const posts = getAllPosts()
  return posts.map((post) => ({
    slug: post.slug,
  }))
}

// Generate metadata for SEO
export async function generateMetadata({
  params,
}: {
  params: Promise<{ slug: string }>
}): Promise<Metadata> {
  const { slug } = await params
  const post = getPostBySlug(slug)

  if (!post) {
    return {
      title: "Article Not Found",
    }
  }

  return {
    title: post.title,
    description: post.excerpt,
    keywords: post.tags,
    authors: [{ name: post.author }],
    openGraph: {
      title: post.title,
      description: post.excerpt,
      type: "article",
      publishedTime: post.date,
      authors: [post.author],
      images: [
        {
          url: `https://masterpost.io${post.coverImage}`,
          width: 1200,
          height: 630,
          alt: post.title,
        },
      ],
    },
    twitter: {
      card: "summary_large_image",
      title: post.title,
      description: post.excerpt,
      images: [`https://masterpost.io${post.coverImage}`],
    },
    alternates: {
      canonical: `https://masterpost.io/blog/${slug}`,
    },
  }
}

export default async function BlogPostPage({
  params,
}: {
  params: Promise<{ slug: string }>
}) {
  const { slug } = await params
  const post = getPostBySlug(slug)

  if (!post) {
    notFound()
  }

  const ArticleComponent = articleComponents[slug]
  const relatedPosts = getRelatedPosts(slug, 3)
  const allPosts = getAllPosts()

  // Table of contents per article
  const tocItemsMap: Record<string, { id: string; text: string; level: number }[]> = {
    "amazon-image-requirements-2026": [
      { id: "introduction", text: "Introduction", level: 2 },
      { id: "official-requirements", text: "Official Amazon Image Requirements", level: 2 },
      { id: "common-rejections", text: "Common Image Rejection Reasons", level: 2 },
      { id: "technical-specs", text: "Technical Specifications Deep Dive", level: 2 },
      { id: "category-specific", text: "Category-Specific Requirements", level: 2 },
      { id: "fix-rejected", text: "How to Fix Rejected Images", level: 2 },
      { id: "automating", text: "Automating Compliance", level: 2 },
      { id: "conclusion", text: "Conclusion", level: 2 },
    ],
    "ebay-image-requirements-2026": [
      { id: "introduction", text: "Introduction", level: 2 },
      { id: "official-requirements", text: "Official eBay Image Requirements", level: 2 },
      { id: "ebay-vs-amazon", text: "eBay vs Amazon: Key Differences", level: 2 },
      { id: "best-practices", text: "Best Practices for High-Converting Listings", level: 2 },
      { id: "category-tips", text: "Category-Specific Tips", level: 2 },
      { id: "common-mistakes", text: "Common eBay Image Mistakes", level: 2 },
      { id: "automating", text: "Automating eBay Image Optimization", level: 2 },
      { id: "conclusion", text: "Conclusion", level: 2 },
    ],
    "instagram-product-images-guide": [
      { id: "introduction", text: "Introduction", level: 2 },
      { id: "official-requirements", text: "Instagram Shopping Image Requirements", level: 2 },
      { id: "formats", text: "Feed vs Stories vs Reels", level: 2 },
      { id: "scroll-stopping", text: "Creating Scroll-Stopping Images", level: 2 },
      { id: "best-practices", text: "Instagram Shopping Best Practices", level: 2 },
      { id: "common-mistakes", text: "Common Instagram Image Mistakes", level: 2 },
      { id: "bulk-processing", text: "Bulk Processing for Instagram", level: 2 },
      { id: "conclusion", text: "Conclusion", level: 2 },
    ],
    "background-removal-guide": [
      { id: "introduction", text: "Introduction", level: 2 },
      { id: "why-it-matters", text: "Why E-commerce Needs Background Removal", level: 2 },
      { id: "manual-methods", text: "Manual Background Removal Methods", level: 2 },
      { id: "ai-methods", text: "AI-Powered Background Removal", level: 2 },
      { id: "automated-solutions", text: "Bulk/Automated Solutions", level: 2 },
      { id: "best-practices", text: "Best Practices", level: 2 },
      { id: "common-problems", text: "Common Problems and Solutions", level: 2 },
      { id: "conclusion", text: "Conclusion", level: 2 },
    ],
  }

  const tocItems = tocItemsMap[slug] || []

  return (
    <div className="min-h-screen bg-white">
      {/* Article Schema Markup */}
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify({
            "@context": "https://schema.org",
            "@type": "Article",
            headline: post.title,
            description: post.excerpt,
            image: `https://masterpost.io${post.coverImage}`,
            datePublished: post.date,
            dateModified: post.date,
            author: {
              "@type": "Person",
              name: post.author,
            },
            publisher: {
              "@type": "Organization",
              name: "Masterpost.io",
              logo: {
                "@type": "ImageObject",
                url: "https://masterpost.io/favicon.svg",
              },
            },
            mainEntityOfPage: {
              "@type": "WebPage",
              "@id": `https://masterpost.io/blog/${slug}`,
            },
          }),
        }}
      />

      {/* Breadcrumb Schema */}
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify({
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            itemListElement: [
              {
                "@type": "ListItem",
                position: 1,
                name: "Home",
                item: "https://masterpost.io",
              },
              {
                "@type": "ListItem",
                position: 2,
                name: "Blog",
                item: "https://masterpost.io/blog",
              },
              {
                "@type": "ListItem",
                position: 3,
                name: post.title,
                item: `https://masterpost.io/blog/${slug}`,
              },
            ],
          }),
        }}
      />

      {/* Main Content */}
      <div className="container mx-auto px-6 py-12">
        <div className="grid lg:grid-cols-[1fr_300px] gap-12">
          {/* Article Content */}
          <div className="max-w-3xl">
            <BlogHeader
              title={post.title}
              excerpt={post.excerpt}
              author={post.author}
              date={post.date}
              readingTime={post.readingTime}
              category={post.category}
              tags={post.tags}
              coverImage={post.coverImage}
              slug={slug}
            />

            {/* Article Body */}
            {ArticleComponent ? (
              <ArticleComponent />
            ) : (
              <div className="prose prose-lg max-w-none">
                <p>Article content coming soon...</p>
              </div>
            )}

            {/* Bottom CTA */}
            <BlogCTA variant="full" />
          </div>

          {/* Sidebar */}
          <aside className="hidden lg:block space-y-6">
            <TableOfContents items={tocItems} />
            <RelatedPosts posts={allPosts} currentSlug={slug} />
            <NewsletterSidebar />
          </aside>
        </div>
      </div>
    </div>
  )
}
