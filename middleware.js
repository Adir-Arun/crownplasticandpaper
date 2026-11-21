// The AR-branded /catalog/ flipbook was taken down. Send /catalog, /catalog/ and anything under it
// to /products/ in one permanent 301 hop (middleware runs before the trailing-slash redirect).
export const config = { matcher: ['/catalog', '/catalog/', '/catalog/:path*'] };

export default function middleware(request) {
  return Response.redirect(new URL('/products/', request.url), 301);
}
