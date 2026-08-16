# Chat: auth refactor

Started 2026-03-04. Goal: move session handling off the ad-hoc cookie code and onto one library.

## Decided

- Use the framework's own session middleware. No custom signing.
- Keep the existing cookie name so live sessions survive the deploy.
- Token TTL stays 14 days — changing it is a separate discussion with the product side.

## Ruled out

- Rolling our own JWT layer. We tried it in `spike/jwt-auth`; refresh-token rotation
  needed a store anyway, which removes the only reason to avoid the middleware.
- Logging users out on deploy. Support said no.

## Where it stopped

`login()` and `logout()` are ported. `require_user()` still reads the old cookie directly —
that is the next thing. After that, delete `auth/legacy_cookie.py`.

## Promote before closing this chat

- "Cookie name is load-bearing, do not rename" → Layer 2, room 204.
