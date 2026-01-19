import BlogContent, { Callout, ComparisonTable, SpecsTable } from "@/components/blog/BlogContent"
import BlogCTA from "@/components/blog/BlogCTA"
import { Check, X } from "lucide-react"

export default function AmazonImageRequirements2026() {
  return (
    <BlogContent>
      {/* Introduction */}
      <section id="introduction">
        <p className="lead text-xl text-gray-700 leading-relaxed">
          If you&apos;re selling on Amazon, you&apos;ve probably experienced the frustration of having product images rejected.
          Amazon rejects <strong>30-40% of submitted product images</strong> from sellers who don&apos;t follow their strict
          guidelines. This isn&apos;t just an inconvenience—it directly impacts your conversion rates and sales.
        </p>

        <p>
          Product images are the first thing customers see when browsing Amazon. Studies show that high-quality,
          compliant images can <strong>increase conversion rates by up to 94%</strong>. On the flip side, rejected
          or poor-quality images can delay your listing, hurt your search rankings, and ultimately cost you sales.
        </p>

        <p>
          In this comprehensive guide, you&apos;ll learn:
        </p>

        <ul>
          <li>Exact specifications for Amazon main and additional images</li>
          <li>The most common rejection reasons and how to avoid them</li>
          <li>Technical deep-dives into background, dimensions, and color modes</li>
          <li>Category-specific requirements you might be missing</li>
          <li>How to automate compliance and save hours of manual work</li>
        </ul>
      </section>

      {/* Official Amazon Image Requirements */}
      <section id="official-requirements">
        <h2>Official Amazon Image Requirements</h2>

        <p>
          Amazon has strict image requirements that apply to all product listings. These are divided into two categories:
          <strong>Main Image</strong> (the primary image shown in search results) and <strong>Additional Images</strong>
          (supporting images on your listing page).
        </p>

        <h3>Main Image Requirements</h3>

        <p>
          Your main image is the most important—it appears in search results and is the first impression customers get of your product.
          Amazon&apos;s main image requirements are non-negotiable:
        </p>

        <SpecsTable
          title="Amazon Main Image Specifications"
          rows={[
            { spec: "Background Color", requirement: "Pure white (RGB 255, 255, 255)", notes: "No off-white, cream, or gray" },
            { spec: "Product Fill", requirement: "85% of image frame", notes: "Product should fill most of the image" },
            { spec: "Minimum Resolution", requirement: "1000px on longest side", notes: "2000px+ recommended for zoom" },
            { spec: "Maximum Resolution", requirement: "10,000px on longest side", notes: "Files up to 10MB" },
            { spec: "File Formats", requirement: "JPEG, PNG, GIF, TIFF", notes: "JPEG preferred for smaller file size" },
            { spec: "Color Mode", requirement: "sRGB or CMYK", notes: "sRGB recommended for web display" },
          ]}
        />

        <Callout type="warning" title="Critical Requirement">
          The background <strong>must</strong> be pure white (RGB 255, 255, 255). Even slightly off-white backgrounds
          (like RGB 254, 254, 254) will be automatically rejected by Amazon&apos;s system.
        </Callout>

        <h3>Additional Image Requirements</h3>

        <p>
          Additional images have more flexibility and allow you to showcase your product in different ways:
        </p>

        <ul>
          <li><strong>Lifestyle shots</strong> showing the product in use</li>
          <li><strong>Infographics</strong> highlighting key features</li>
          <li><strong>Size comparisons</strong> with common objects</li>
          <li><strong>Close-up details</strong> of important features</li>
          <li><strong>Packaging</strong> (when relevant to the purchase decision)</li>
          <li><strong>Multiple angles</strong> of the product</li>
        </ul>

        <Callout type="tip">
          Use all 9 available image slots. Listings with 6+ high-quality images typically see <strong>30% higher conversion rates</strong> than those with only the main image.
        </Callout>
      </section>

      {/* Common Image Rejection Reasons */}
      <section id="common-rejections">
        <h2>Common Image Rejection Reasons</h2>

        <p>
          Understanding why Amazon rejects images is the first step to avoiding costly delays. Here are the most common
          rejection reasons, ranked by frequency:
        </p>

        <div className="my-8 space-y-4">
          <div className="flex items-start gap-3 p-4 bg-red-50 border border-red-200 rounded-lg">
            <X className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
            <div>
              <p className="font-bold text-red-800">Background not pure white (Most Common)</p>
              <p className="text-sm text-red-700">Even slightly off-white, gray, or cream backgrounds will be rejected. Your camera&apos;s auto white balance often produces RGB 250-254 instead of pure 255.</p>
            </div>
          </div>

          <div className="flex items-start gap-3 p-4 bg-red-50 border border-red-200 rounded-lg">
            <X className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
            <div>
              <p className="font-bold text-red-800">Product too small in frame</p>
              <p className="text-sm text-red-700">The product must fill at least 85% of the image. Small products with excessive white space look unprofessional and fail compliance.</p>
            </div>
          </div>

          <div className="flex items-start gap-3 p-4 bg-red-50 border border-red-200 rounded-lg">
            <X className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
            <div>
              <p className="font-bold text-red-800">Low resolution or pixelation</p>
              <p className="text-sm text-red-700">Images under 1000px won&apos;t allow zoom functionality. Blurry or pixelated images hurt customer trust and conversion.</p>
            </div>
          </div>

          <div className="flex items-start gap-3 p-4 bg-red-50 border border-red-200 rounded-lg">
            <X className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
            <div>
              <p className="font-bold text-red-800">Watermarks or logos visible</p>
              <p className="text-sm text-red-700">No seller logos, watermarks, or promotional text on main images. This includes &quot;Best Seller&quot; badges or price overlays.</p>
            </div>
          </div>

          <div className="flex items-start gap-3 p-4 bg-red-50 border border-red-200 rounded-lg">
            <X className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
            <div>
              <p className="font-bold text-red-800">Multiple products in main image</p>
              <p className="text-sm text-red-700">The main image should show only the product included in the purchase. No accessories unless they come with the product.</p>
            </div>
          </div>

          <div className="flex items-start gap-3 p-4 bg-red-50 border border-red-200 rounded-lg">
            <X className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
            <div>
              <p className="font-bold text-red-800">Text overlay on main image</p>
              <p className="text-sm text-red-700">No promotional text, feature callouts, or any text on the main image. Save this for additional images.</p>
            </div>
          </div>

          <div className="flex items-start gap-3 p-4 bg-red-50 border border-red-200 rounded-lg">
            <X className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
            <div>
              <p className="font-bold text-red-800">Visible mannequins</p>
              <p className="text-sm text-red-700">For apparel, mannequins must be invisible (ghost mannequin technique) or the clothing must be flat-lay or on a model.</p>
            </div>
          </div>

          <div className="flex items-start gap-3 p-4 bg-red-50 border border-red-200 rounded-lg">
            <X className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
            <div>
              <p className="font-bold text-red-800">Distracting props</p>
              <p className="text-sm text-red-700">Props that aren&apos;t included with the product can confuse customers about what they&apos;re purchasing.</p>
            </div>
          </div>
        </div>

        <h3>Visual Comparison: Wrong vs Right</h3>

        <ComparisonTable
          rows={[
            { wrong: "Off-white background (RGB 252, 252, 250)", right: "Pure white background (RGB 255, 255, 255)" },
            { wrong: "Product fills 50% of frame", right: "Product fills 85%+ of frame" },
            { wrong: "500px resolution", right: "2000px+ resolution" },
            { wrong: "Company logo watermark", right: "Clean image, no overlays" },
            { wrong: "Multiple products shown", right: "Single product only" },
            { wrong: "\"BEST SELLER!\" text overlay", right: "No text on main image" },
            { wrong: "Visible mannequin", right: "Ghost mannequin or flat lay" },
            { wrong: "Decorative props visible", right: "Product only, no props" },
          ]}
        />
      </section>

      {/* Technical Specifications Deep Dive */}
      <section id="technical-specs">
        <h2>Technical Specifications Deep Dive</h2>

        <h3>White Background: The RGB 255,255,255 Rule</h3>

        <p>
          The pure white background requirement is the #1 cause of image rejections. Here&apos;s why it&apos;s so important
          and how Amazon&apos;s automated checker works:
        </p>

        <p>
          Amazon uses automated image scanning to check background color. The system samples pixels from the edges
          of your image and compares them to pure white (RGB 255, 255, 255). If any sampled pixels fall below a
          certain threshold (typically RGB 250 or below), the image is automatically rejected.
        </p>

        <Callout type="info" title="How to Check Your Background">
          Open your image in any photo editor (Photoshop, GIMP, even online tools). Use the eyedropper tool
          on your background. The RGB values should read exactly 255, 255, 255. Any variation (like 254, 254, 254)
          will likely trigger a rejection.
        </Callout>

        <p><strong>Tips for achieving pure white:</strong></p>

        <ul>
          <li>Don&apos;t rely on camera auto white balance—it rarely produces true white</li>
          <li>Use professional lighting with proper exposure settings</li>
          <li>Always post-process images to ensure RGB 255, 255, 255 background</li>
          <li>Consider using AI background removal tools like Masterpost.io that guarantee pure white output</li>
        </ul>

        <h3>Image Dimensions: Why 2000px+ Matters</h3>

        <p>
          While Amazon&apos;s minimum is 1000px, there&apos;s a significant advantage to using 2000px or higher:
        </p>

        <ul>
          <li><strong>Zoom Feature:</strong> Images 1000px+ enable zoom, but 2000px+ provides clearer zoom detail</li>
          <li><strong>Mobile Experience:</strong> Higher resolution images look better on high-DPI mobile screens</li>
          <li><strong>Future-Proofing:</strong> As screen resolutions increase, your images stay sharp</li>
          <li><strong>Search Ranking:</strong> Amazon may favor listings with higher-quality images</li>
        </ul>

        <SpecsTable
          title="Recommended Dimensions by Product Type"
          rows={[
            { spec: "Standard Products", requirement: "2000 x 2000px (1:1)", notes: "Square format works universally" },
            { spec: "Tall Products", requirement: "1500 x 2000px (3:4)", notes: "Bottles, tall packaging" },
            { spec: "Wide Products", requirement: "2000 x 1500px (4:3)", notes: "Electronics, keyboards" },
            { spec: "Jewelry/Small Items", requirement: "2000 x 2000px", notes: "Zoom is critical for details" },
          ]}
        />

        <h3>Color Mode: sRGB vs CMYK</h3>

        <p>
          Amazon accepts both sRGB and CMYK color modes, but there&apos;s a clear winner for e-commerce:
        </p>

        <ul>
          <li><strong>sRGB (Recommended):</strong> Standard for web displays. Colors appear consistent across devices.</li>
          <li><strong>CMYK:</strong> Designed for print. Colors may appear dull or shifted on screens.</li>
        </ul>

        <p>
          <strong>How to convert properly:</strong> In Photoshop, go to Image → Mode → RGB Color. Then convert to
          sRGB profile via Edit → Convert to Profile → sRGB IEC61966-2.1.
        </p>
      </section>

      {/* Category-Specific Requirements */}
      <section id="category-specific">
        <h2>Category-Specific Requirements</h2>

        <p>
          Beyond the general requirements, certain product categories have additional rules:
        </p>

        <h3>Apparel</h3>
        <ul>
          <li>Ghost mannequin technique required (no visible mannequins)</li>
          <li>Flat lay photography is acceptable</li>
          <li>Human models are allowed but must be standing (no sitting poses)</li>
          <li>No accessories on models that aren&apos;t included with the product</li>
        </ul>

        <h3>Jewelry</h3>
        <ul>
          <li>Size reference may be required for certain items</li>
          <li>Close-up shots showing detail are essential</li>
          <li>Reflective surfaces should be carefully managed</li>
          <li>Consider showing the item worn (in additional images)</li>
        </ul>

        <h3>Electronics</h3>
        <ul>
          <li>Show packaging only if it&apos;s a key selling point</li>
          <li>Include all cables/accessories that come with the product</li>
          <li>Display screens should show generic content (not branded content)</li>
          <li>Power indicators can be lit in images</li>
        </ul>

        <h3>Beauty & Personal Care</h3>
        <ul>
          <li>Ingredient lists may need to be readable in at least one image</li>
          <li>Before/after images may be restricted</li>
          <li>Claims on packaging must match listing claims</li>
          <li>Show product size clearly for customer reference</li>
        </ul>
      </section>

      {/* How to Fix Rejected Images */}
      <section id="fix-rejected">
        <h2>How to Fix Rejected Images</h2>

        <p>
          If your images have been rejected, here&apos;s a systematic approach to fixing them:
        </p>

        <h3>Step 1: Identify the Issue</h3>
        <p>
          Check Amazon&apos;s rejection reason (usually sent via email or shown in Seller Central).
          Common codes include:
        </p>
        <ul>
          <li>MAIN_OFFER_IMAGE_REQUIRES_BACKGROUND_TO_BE_WHITE</li>
          <li>MAIN_OFFER_IMAGE_REQUIRES_NO_ADDITIONAL_TEXT</li>
          <li>IMAGE_RESOLUTION_TOO_LOW</li>
        </ul>

        <h3>Step 2: Tools You&apos;ll Need</h3>
        <ul>
          <li><strong>Photo Editor:</strong> Photoshop, GIMP, or Affinity Photo</li>
          <li><strong>Background Removal:</strong> AI tools like Masterpost.io for quick, accurate results</li>
          <li><strong>Color Checker:</strong> Any tool with an eyedropper to verify RGB values</li>
        </ul>

        <h3>Step 3: Common Photoshop/GIMP Mistakes</h3>
        <ul>
          <li><strong>Wrong layer blending:</strong> Ensure background layer is solid white, not transparent</li>
          <li><strong>Compression artifacts:</strong> Save at quality 85% or higher to avoid edge artifacts</li>
          <li><strong>Wrong color profile:</strong> Always export in sRGB color space</li>
          <li><strong>Anti-aliasing issues:</strong> Edges should be clean, not pixelated</li>
        </ul>

        <h3>Step 4: Batch Processing</h3>
        <p>
          If you have multiple images to fix, manual editing doesn&apos;t scale. Consider:
        </p>
        <ul>
          <li>Photoshop Actions for repetitive tasks</li>
          <li>Lightroom batch exports with presets</li>
          <li>AI-powered tools designed for bulk processing</li>
        </ul>
      </section>

      {/* Automating Compliance */}
      <section id="automating">
        <h2>Automating Compliance</h2>

        <p>
          Manual image editing works for a few products, but it doesn&apos;t scale. If you&apos;re managing
          50+ SKUs or regularly adding new products, the hours add up quickly.
        </p>

        <h3>Why Manual Editing Doesn&apos;t Scale</h3>
        <ul>
          <li><strong>Time:</strong> 5-15 minutes per image for proper background removal</li>
          <li><strong>Consistency:</strong> Hard to maintain exact RGB 255,255,255 across all images</li>
          <li><strong>Skill:</strong> Quality results require photo editing expertise</li>
          <li><strong>Cost:</strong> Professional editors charge $1-5+ per image</li>
        </ul>

        <h3>Benefits of Automation</h3>
        <ul>
          <li><strong>Speed:</strong> Process hundreds of images in minutes, not hours</li>
          <li><strong>Consistency:</strong> Guaranteed pure white backgrounds every time</li>
          <li><strong>Cost:</strong> Significantly cheaper than manual editing or outsourcing</li>
          <li><strong>Scalability:</strong> Handle seasonal spikes and new product launches easily</li>
        </ul>

        <BlogCTA
          variant="inline"
          title="How Masterpost.io Solves This"
          description="1-click Amazon compliance, bulk processing up to 100 images, automatic pure white backgrounds, proper dimensions—72% cheaper than manual editing."
        />
      </section>

      {/* Conclusion */}
      <section id="conclusion">
        <h2>Conclusion</h2>

        <p>
          Amazon&apos;s image requirements might seem strict, but they exist to maintain a consistent, trustworthy
          shopping experience for customers. By following these guidelines, you&apos;re not just avoiding rejections—you&apos;re
          building a professional brand presence that converts browsers into buyers.
        </p>

        <p><strong>Key takeaways:</strong></p>

        <ul>
          <li>Always use pure white backgrounds (RGB 255, 255, 255)</li>
          <li>Ensure your product fills 85%+ of the image frame</li>
          <li>Use 2000px+ resolution for optimal zoom functionality</li>
          <li>No text, watermarks, or logos on main images</li>
          <li>Check category-specific requirements for your products</li>
          <li>Consider automation tools to save time and ensure consistency</li>
        </ul>

        <Callout type="success" title="Ready to Get Started?">
          Stop spending hours on manual image editing. Masterpost.io processes your product images in seconds
          with AI-powered background removal, guaranteed Amazon compliance, and 72% lower costs than competitors.
          <strong> Try 10 images free—no credit card required.</strong>
        </Callout>
      </section>
    </BlogContent>
  )
}
