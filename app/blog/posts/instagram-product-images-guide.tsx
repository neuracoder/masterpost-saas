import BlogContent, { Callout, ComparisonTable, SpecsTable } from "@/components/blog/BlogContent"
import BlogCTA from "@/components/blog/BlogCTA"
import { Check, X } from "lucide-react"

export default function InstagramProductImagesGuide() {
  return (
    <BlogContent>
      {/* Introduction */}
      <section id="introduction">
        <p className="lead text-xl text-gray-700 leading-relaxed">
          Instagram Shopping has transformed from a simple photo-sharing feature into a
          <strong> $37 billion social commerce channel</strong>. For e-commerce sellers, Instagram
          represents a massive opportunity—but only if your product images can stop the scroll.
        </p>

        <p>
          Unlike traditional marketplaces, Instagram is a visual-first platform where aesthetics matter
          as much as product quality. Your images need to meet technical requirements while also fitting
          Instagram&apos;s unique visual language and user expectations.
        </p>

        <p>
          In this guide, you&apos;ll learn Instagram Shopping&apos;s image requirements, format specifications
          for Feed, Stories, and Reels, and proven strategies for creating product photos that drive sales.
        </p>
      </section>

      {/* Official Requirements */}
      <section id="official-requirements">
        <h2>Instagram Shopping Image Requirements</h2>

        <p>
          Instagram has specific technical requirements for product images in their Shopping feature.
          Meeting these ensures your products display correctly across all devices.
        </p>

        <h3>Technical Specifications</h3>

        <SpecsTable
          title="Instagram Image Specifications"
          rows={[
            { spec: "Minimum Resolution", requirement: "500 x 500px", notes: "Square format minimum" },
            { spec: "Recommended Resolution", requirement: "1080 x 1080px", notes: "Optimal for all devices" },
            { spec: "Square (1:1)", requirement: "1080 x 1080px", notes: "Best for Feed posts" },
            { spec: "Vertical (4:5)", requirement: "1080 x 1350px", notes: "Maximum Feed real estate" },
            { spec: "Horizontal (1.91:1)", requirement: "1080 x 566px", notes: "Landscape format" },
            { spec: "Stories/Reels", requirement: "1080 x 1920px (9:16)", notes: "Full-screen vertical" },
            { spec: "Max File Size (Feed)", requirement: "30MB", notes: "JPEG or PNG" },
            { spec: "Max File Size (Stories)", requirement: "4MB", notes: "Optimized for mobile" },
          ]}
        />

        <h3>Product Commerce Policy</h3>

        <p>
          Instagram has strict policies for products sold through Shopping:
        </p>

        <ul>
          <li><strong>Clear product view</strong> - The product must be clearly visible and recognizable</li>
          <li><strong>Accurate representation</strong> - Images must show actual product, not misleading renders</li>
          <li><strong>No text-heavy images</strong> - Minimal overlaid text (less than 20% of image)</li>
          <li><strong>Branded content rules</strong> - Must comply with partnership disclosures</li>
          <li><strong>No prohibited items</strong> - Follows Instagram&apos;s commerce policies</li>
        </ul>

        <Callout type="warning" title="Important">
          Instagram may reject or limit distribution of Shopping posts that violate these guidelines.
          Repeated violations can result in losing Shopping privileges entirely.
        </Callout>
      </section>

      {/* Feed vs Stories vs Reels */}
      <section id="formats">
        <h2>Instagram Feed vs Stories vs Reels</h2>

        <p>
          Different Instagram formats have different specifications and best practices. Understanding
          these helps you optimize your product content for each placement.
        </p>

        <h3>Feed Posts</h3>

        <ul>
          <li><strong>Best aspect ratio:</strong> 4:5 (vertical) for maximum screen real estate</li>
          <li><strong>Carousel posts:</strong> Up to 10 images/videos per post</li>
          <li><strong>Lifespan:</strong> Permanent (stays on your profile grid)</li>
          <li><strong>Best for:</strong> Hero product shots, detailed carousels, curated aesthetics</li>
        </ul>

        <h3>Stories</h3>

        <ul>
          <li><strong>Aspect ratio:</strong> 9:16 (full vertical)</li>
          <li><strong>Resolution:</strong> 1080 x 1920px</li>
          <li><strong>Lifespan:</strong> 24 hours (unless saved to Highlights)</li>
          <li><strong>Best for:</strong> Flash sales, behind-the-scenes, product launches</li>
        </ul>

        <h3>Reels</h3>

        <ul>
          <li><strong>Aspect ratio:</strong> 9:16 (full vertical)</li>
          <li><strong>Length:</strong> Up to 90 seconds</li>
          <li><strong>Best for:</strong> Product demos, tutorials, trending content</li>
          <li><strong>Algorithm boost:</strong> Currently favored by Instagram&apos;s algorithm</li>
        </ul>

        <Callout type="tip" title="Pro Tip">
          Use 4:5 vertical images for Feed posts—they take up more screen space than square images,
          increasing visibility and engagement by up to <strong>20%</strong>.
        </Callout>

        <h3>Format Comparison</h3>

        <ComparisonTable
          rows={[
            { wrong: "Square (1:1) in Feed - 1080x1080", right: "Vertical (4:5) in Feed - 1080x1350" },
            { wrong: "Landscape in Stories - gets cropped", right: "Full vertical (9:16) - fills screen" },
            { wrong: "Static images in Reels", right: "Video or animated content in Reels" },
            { wrong: "One product image only", right: "Carousel with multiple angles/details" },
          ]}
        />
      </section>

      {/* Creating Scroll-Stopping Images */}
      <section id="scroll-stopping">
        <h2>Creating Scroll-Stopping Product Images</h2>

        <p>
          Instagram users scroll through hundreds of posts daily. Your product images need to stand out
          in a fraction of a second. Here&apos;s how to create images that stop the scroll:
        </p>

        <h3>1. Lifestyle Photography That Fits</h3>

        <p>
          Instagram isn&apos;t a traditional marketplace—it&apos;s a visual platform where aesthetics matter.
          Your product photos should feel native to Instagram&apos;s visual language:
        </p>

        <ul>
          <li><strong>Real-world context</strong> - Show products in use, not just on white backgrounds</li>
          <li><strong>Aspirational settings</strong> - Create scenes buyers want to be part of</li>
          <li><strong>Cohesive aesthetic</strong> - Match your brand&apos;s visual identity</li>
          <li><strong>Natural, not salesy</strong> - Content should feel organic, not like an ad</li>
        </ul>

        <h3>2. User-Generated Content (UGC)</h3>

        <p>
          UGC is incredibly powerful on Instagram—it provides social proof and authentic representation:
        </p>

        <ul>
          <li>Reshare customer photos (with permission)</li>
          <li>Encourage customers to tag your products</li>
          <li>Create a branded hashtag for user submissions</li>
          <li>Feature real customers using your products</li>
        </ul>

        <h3>3. Consistent Visual Branding</h3>

        <p>
          Your Instagram profile should have a cohesive visual identity:
        </p>

        <ul>
          <li><strong>Color palette</strong> - Stick to 3-5 brand colors</li>
          <li><strong>Editing style</strong> - Consistent filters/presets across all images</li>
          <li><strong>Composition patterns</strong> - Recognizable photo style</li>
          <li><strong>Grid aesthetics</strong> - Consider how images look together on your profile</li>
        </ul>

        <h3>4. White Space and Composition</h3>

        <p>
          Don&apos;t overcrowd your images:
        </p>

        <ul>
          <li>Give your product room to breathe</li>
          <li>Use negative space strategically</li>
          <li>Follow the rule of thirds for composition</li>
          <li>Avoid cluttered, busy backgrounds</li>
        </ul>

        <h3>5. Color Psychology</h3>

        <p>
          Colors evoke emotions and influence engagement:
        </p>

        <ul>
          <li><strong>Bright colors</strong> - Higher engagement but must match brand</li>
          <li><strong>Pastels</strong> - Soft, aspirational feel</li>
          <li><strong>Contrast</strong> - Product should pop from background</li>
          <li><strong>Seasonal colors</strong> - Align with current trends and seasons</li>
        </ul>
      </section>

      {/* Best Practices */}
      <section id="best-practices">
        <h2>Instagram Shopping Best Practices</h2>

        <h3>Maximize Carousel Posts</h3>

        <p>
          Carousel posts have the highest engagement on Instagram. Use them to showcase products:
        </p>

        <ul>
          <li><strong>Slide 1:</strong> Hero shot (best angle)</li>
          <li><strong>Slide 2-3:</strong> Product in use / lifestyle shots</li>
          <li><strong>Slide 4-5:</strong> Detail shots / close-ups</li>
          <li><strong>Slide 6:</strong> Size reference or comparison</li>
          <li><strong>Final slide:</strong> Clear CTA or product info</li>
        </ul>

        <h3>Product Tagging Tips</h3>

        <ul>
          <li>Tag products clearly visible in the image</li>
          <li>Don&apos;t over-tag (2-5 products per image)</li>
          <li>Place tags where they don&apos;t obstruct the product</li>
          <li>Tag all variants if applicable</li>
        </ul>

        <h3>Consistent Editing Style</h3>

        <p>
          Use the same editing approach for all product photos:
        </p>

        <ul>
          <li>Create and save presets in your editing app</li>
          <li>Maintain consistent exposure and white balance</li>
          <li>Apply the same level of sharpening and clarity</li>
          <li>Keep color grading uniform across your catalog</li>
        </ul>

        <h3>Lighting for Instagram</h3>

        <ul>
          <li><strong>Natural light preferred</strong> - Soft, diffused daylight</li>
          <li><strong>Golden hour</strong> - Warm, flattering light</li>
          <li><strong>Avoid harsh shadows</strong> - Use reflectors or fill light</li>
          <li><strong>Consistent lighting setup</strong> - For product photography</li>
        </ul>

        <h3>Mobile-First Mindset</h3>

        <p>
          97% of Instagram users access the platform via mobile. Always consider:
        </p>

        <ul>
          <li>How images look on small screens</li>
          <li>Text readability at mobile size</li>
          <li>Tap-friendly product tag placement</li>
          <li>Load times (optimize file sizes)</li>
        </ul>

        <Callout type="tip" title="A/B Testing">
          Test different image styles to see what resonates with your audience. Try different backgrounds,
          compositions, and editing styles. Track engagement to identify what works best.
        </Callout>
      </section>

      {/* Common Mistakes */}
      <section id="common-mistakes">
        <h2>Common Instagram Image Mistakes</h2>

        <div className="my-8 space-y-4">
          <div className="flex items-start gap-3 p-4 bg-red-50 border border-red-200 rounded-lg">
            <X className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
            <div>
              <p className="font-bold text-red-800">Over-filtering and heavy editing</p>
              <p className="text-sm text-red-700">Excessive filters distort product colors and create unrealistic expectations. Keep editing natural and accurate.</p>
            </div>
          </div>

          <div className="flex items-start gap-3 p-4 bg-red-50 border border-red-200 rounded-lg">
            <X className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
            <div>
              <p className="font-bold text-red-800">Inconsistent brand aesthetic</p>
              <p className="text-sm text-red-700">Randomly styled images create a messy profile grid. Maintain visual consistency for a professional appearance.</p>
            </div>
          </div>

          <div className="flex items-start gap-3 p-4 bg-red-50 border border-red-200 rounded-lg">
            <X className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
            <div>
              <p className="font-bold text-red-800">Poor lighting and shadows</p>
              <p className="text-sm text-red-700">Dark, poorly lit photos look unprofessional and make products unappealing. Always prioritize good lighting.</p>
            </div>
          </div>

          <div className="flex items-start gap-3 p-4 bg-red-50 border border-red-200 rounded-lg">
            <X className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
            <div>
              <p className="font-bold text-red-800">Cluttered backgrounds</p>
              <p className="text-sm text-red-700">Busy backgrounds distract from your product. Keep backgrounds simple and let your product be the focus.</p>
            </div>
          </div>

          <div className="flex items-start gap-3 p-4 bg-red-50 border border-red-200 rounded-lg">
            <X className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
            <div>
              <p className="font-bold text-red-800">Text-heavy images</p>
              <p className="text-sm text-red-700">Instagram penalizes images with too much text. Keep overlaid text minimal and use captions instead.</p>
            </div>
          </div>
        </div>
      </section>

      {/* Bulk Processing */}
      <section id="bulk-processing">
        <h2>Bulk Processing for Instagram Sellers</h2>

        <p>
          Maintaining a consistent visual style across dozens or hundreds of products requires efficient
          workflows. Automation helps you:
        </p>

        <ul>
          <li><strong>Consistent formatting</strong> - Every image sized correctly for Instagram</li>
          <li><strong>Uniform backgrounds</strong> - Clean, professional look across your catalog</li>
          <li><strong>Faster turnaround</strong> - Launch new products quickly</li>
          <li><strong>Scale content creation</strong> - Handle large product catalogs</li>
        </ul>

        <BlogCTA
          variant="inline"
          title="Masterpost.io for Instagram Sellers"
          description="Perfect square format (1080x1080), clean background removal for consistent aesthetics, and batch processing for your entire catalog."
        />
      </section>

      {/* Conclusion */}
      <section id="conclusion">
        <h2>Conclusion</h2>

        <p>
          Instagram Shopping success comes down to visual quality and consistency. Unlike traditional
          marketplaces, Instagram rewards brands that understand its visual language and create content
          that feels native to the platform.
        </p>

        <p><strong>Key takeaways:</strong></p>

        <ul>
          <li>Use 4:5 vertical format for Feed posts to maximize screen real estate</li>
          <li>Maintain consistent visual branding across all images</li>
          <li>Leverage carousel posts for maximum engagement</li>
          <li>Think mobile-first—97% of users are on phones</li>
          <li>Keep editing natural and colors accurate</li>
          <li>Use lifestyle photography that fits Instagram&apos;s aesthetic</li>
        </ul>

        <Callout type="success" title="Ready to Elevate Your Instagram Shop?">
          Create professional, consistent product images for Instagram with Masterpost.io.
          <strong> Try 10 images free—no credit card required.</strong>
        </Callout>
      </section>
    </BlogContent>
  )
}
