// lib/paddle.ts - Paddle Payment Integration

export const PADDLE_CONFIG = {
  environment: process.env.NEXT_PUBLIC_PADDLE_ENVIRONMENT as 'sandbox' | 'production',
  sellerId: process.env.NEXT_PUBLIC_PADDLE_SELLER_ID!,
  clientToken: process.env.NEXT_PUBLIC_PADDLE_CLIENT_TOKEN!,
  products: {
    starter: {
      id: process.env.NEXT_PUBLIC_PADDLE_PRODUCT_STARTER!,
      credits: parseInt(process.env.NEXT_PUBLIC_CREDITS_STARTER || '50'),
      price: parseFloat(process.env.NEXT_PUBLIC_PRICE_STARTER || '4.99'),
      name: 'Starter Pack',
      description: '50 image processing credits'
    },
    pro: {
      id: process.env.NEXT_PUBLIC_PADDLE_PRODUCT_PRO!,
      credits: parseInt(process.env.NEXT_PUBLIC_CREDITS_PRO || '200'),
      price: parseFloat(process.env.NEXT_PUBLIC_PRICE_PRO || '17.99'),
      name: 'Pro Pack',
      description: '200 credits with Qwen AI processing'
    },
    business: {
      id: process.env.NEXT_PUBLIC_PADDLE_PRODUCT_BUSINESS!,
      credits: parseInt(process.env.NEXT_PUBLIC_CREDITS_BUSINESS || '500'),
      price: parseFloat(process.env.NEXT_PUBLIC_PRICE_BUSINESS || '39.99'),
      name: 'Business Pack',
      description: '500 credits with priority processing'
    }
  }
};

// Initialize Paddle.js SDK
export const initializePaddle = () => {
  if (typeof window === 'undefined') return;

  // Check if already loaded
  if (window.Paddle) {
    console.log('Paddle already initialized');
    return;
  }

  const script = document.createElement('script');
  script.src = 'https://cdn.paddle.com/paddle/v2/paddle.js';
  script.async = true;

  script.onload = () => {
    console.log('Paddle SDK loaded');

    if (window.Paddle) {
      try {
        // Initialize Paddle with client token
        window.Paddle.Initialize({
          token: PADDLE_CONFIG.clientToken,
          eventCallback: (event: any) => {
            console.log('Paddle Event:', event);

            // Handle checkout completion
            if (event.name === 'checkout.completed') {
              console.log('Payment successful:', event.data);

              // Redirect to success page with transaction ID
              const transactionId = event.data?.transaction_id;
              if (transactionId) {
                window.location.href = `/payment-success?transaction_id=${transactionId}`;
              }
            }

            // Handle checkout closed
            if (event.name === 'checkout.closed') {
              console.log('Checkout closed by user');
            }
          }
        });

        console.log(`Paddle initialized in ${PADDLE_CONFIG.environment?.toUpperCase() || 'UNKNOWN'} mode`);
      } catch (error) {
        console.error('Paddle initialization error:', error);
      }
    }
  };

  script.onerror = () => {
    console.error('Failed to load Paddle SDK');
  };

  document.head.appendChild(script);
};

// Open Paddle checkout
export const openPaddleCheckout = (
  productId: string,
  userEmail?: string,
  customData?: Record<string, any>
) => {
  if (!window.Paddle) {
    console.error('Paddle not initialized');
    return;
  }

  try {
    console.log('Opening Paddle checkout for:', productId);

    window.Paddle.Checkout.open({
      items: [
        {
          priceId: productId,
          quantity: 1
        }
      ],
      customer: userEmail ? { email: userEmail } : undefined,
      customData: customData
    });
  } catch (error) {
    console.error('Paddle checkout error:', error);
  }
};

// TypeScript declarations
declare global {
  interface Window {
    Paddle?: any;
  }
}
