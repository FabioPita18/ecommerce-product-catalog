/**
 * Product Placeholder Images
 *
 * Maps each product to a relevant Unsplash photo URL.
 * Uses Unsplash's image CDN with resize parameters for performance.
 * If a product has an uploaded image, that is used instead.
 */

const productImageMap: Record<string, string> = {
  // Electronics
  'wireless-bluetooth-headphones':
    'https://images.unsplash.com/photo-1505740420928-5e560c06d30e',
  'smartphone-stand-wireless-charger':
    'https://images.unsplash.com/photo-1586953208270-767fc68f083e',
  'mechanical-keyboard-rgb':
    'https://images.unsplash.com/photo-1618384887929-16ec33fab9ef',
  '4k-webcam-ring-light':
    'https://images.unsplash.com/photo-1611532736597-de2d4265fba3',

  // Clothing
  'classic-denim-jacket':
    'https://images.unsplash.com/photo-1576995853123-5a10305d93c0',
  'cotton-crew-neck-tshirt-pack':
    'https://images.unsplash.com/photo-1521572163474-6864f9cf17ab',
  'running-sneakers':
    'https://images.unsplash.com/photo-1542291026-7eec264c27ff',

  // Books
  'the-art-of-programming':
    'https://images.unsplash.com/photo-1532012197267-da84d127e765',
  'mystery-novel-collection':
    'https://images.unsplash.com/photo-1512820790803-83ca734da794',

  // Home & Garden
  'modern-minimalist-desk-lamp':
    'https://images.unsplash.com/photo-1507473885765-e6ed057ab788',
  'indoor-plant-starter-kit':
    'https://images.unsplash.com/photo-1416879595882-3373a0480b5b',
  'cozy-throw-blanket':
    'https://images.unsplash.com/photo-1555041469-a586c61ea9bc',

  // Sports & Outdoors
  'yoga-mat-premium':
    'https://images.unsplash.com/photo-1601925260368-ae2f83cf8b7f',
  'resistance-bands-set':
    'https://images.unsplash.com/photo-1598289431512-b97b0917affc',
  'insulated-water-bottle':
    'https://images.unsplash.com/photo-1602143407151-7111542de6e8',
};

/**
 * Get image URL for a product.
 * Returns the uploaded image if available, otherwise an Unsplash photo.
 */
export function getProductImage(
  slug: string,
  actualImage: string | null,
  width = 400,
  height = 300
): string {
  if (actualImage) return actualImage;

  const baseUrl = productImageMap[slug];
  if (baseUrl) {
    return `${baseUrl}?w=${width}&h=${height}&fit=crop&auto=format`;
  }

  // Fallback for unknown products
  return `https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=${width}&h=${height}&fit=crop&auto=format`;
}
