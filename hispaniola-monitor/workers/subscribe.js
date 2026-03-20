/**
 * Hispaniola Monitor — Subscribe Worker
 * Deploy to Cloudflare Workers (free plan)
 * 
 * wrangler deploy
 * 
 * Set secrets:
 *   wrangler secret put RESEND_API_KEY
 *   wrangler secret put RESEND_AUDIENCE_ID
 * 
 * Then update index.html to point to your worker URL:
 *   fetch('https://subscribe.YOUR_WORKER.workers.dev', ...)
 */

export default {
  async fetch(request, env) {
    // CORS headers
    const corsHeaders = {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
    };

    if (request.method === 'OPTIONS') {
      return new Response(null, { headers: corsHeaders });
    }

    if (request.method !== 'POST') {
      return new Response('Method not allowed', { status: 405, headers: corsHeaders });
    }

    try {
      const { email } = await request.json();

      if (!email || !email.includes('@') || email.length > 255) {
        return new Response(
          JSON.stringify({ ok: false, error: 'Invalid email' }),
          { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
        );
      }

      // Add to Resend audience
      const res = await fetch(
        `https://api.resend.com/audiences/${env.RESEND_AUDIENCE_ID}/contacts`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${env.RESEND_API_KEY}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            email,
            unsubscribed: false,
          }),
        }
      );

      if (res.ok || res.status === 409) { // 409 = already subscribed
        return new Response(
          JSON.stringify({ ok: true, message: 'Subscribed!' }),
          { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
        );
      }

      const errText = await res.text();
      console.error('Resend error:', errText);
      return new Response(
        JSON.stringify({ ok: false, error: 'Subscription failed' }),
        { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      );

    } catch (e) {
      return new Response(
        JSON.stringify({ ok: false, error: 'Server error' }),
        { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      );
    }
  },
};
