-- Passwords are MD5 hashed (VULN: CWE-916)
-- admin:admin123  ->  0192023a7bbd73250516f069df18b500
-- alice:password   ->  5f4dcc3b5aa765d61d8327deb882cf99
-- bob:letmein      ->  0d107d09f5bbe40cade3de5c71e9e9b7

INSERT INTO users (username, password, bio, role) VALUES
    ('admin', '0192023a7bbd73250516f069df18b500', 'Site administrator. I keep the lights on.', 'admin'),
    ('alice', '5f4dcc3b5aa765d61d8327deb882cf99', 'Security researcher and coffee enthusiast.', 'user'),
    ('bob', '0d107d09f5bbe40cade3de5c71e9e9b7', 'Full-stack developer. I break things so you don''t have to.', 'user');

INSERT INTO posts (title, slug, body, author_id, status, tags, reading_time) VALUES
    ('Welcome to VulnPy',
     'welcome-to-vulnpy',
     'Welcome to VulnPy — a modern blogging platform built with Flask. We''re excited to share our thoughts on security, development, and everything in between.

This platform is designed to be a space for thoughtful discussion about web security topics. Feel free to explore, leave comments, and contribute your own posts.

Happy reading!',
     1, 'published', 'announcements,welcome', 2),

    ('Understanding SQL Injection',
     'understanding-sql-injection',
     'SQL injection remains one of the most critical web application vulnerabilities. At its core, SQLi occurs when user input is concatenated directly into SQL queries without proper sanitization.

Consider a login form that builds its query using string formatting:

query = "SELECT * FROM users WHERE username = ''%s'' AND password = ''%s''" % (user_input, pass_input)

An attacker could supply: '' OR 1=1 -- as the username to bypass authentication entirely. The query becomes logically true for all rows, and the password check is commented out.

The defense is straightforward: use parameterized queries. Every modern database driver supports them. There is no excuse for string concatenation in SQL.

We''ll explore more advanced injection techniques — UNION-based extraction, blind injection, and second-order injection — in future posts.',
     2, 'published', 'security,sqli,owasp', 5),

    ('XSS: The Gift That Keeps on Giving',
     'xss-the-gift-that-keeps-on-giving',
     'Cross-Site Scripting (XSS) has been on the OWASP Top 10 for over two decades, and it isn''t going anywhere. Modern frameworks provide auto-escaping, but developers still find ways to introduce XSS — usually by explicitly marking content as "safe" or by injecting into JavaScript contexts.

There are three main types:

**Reflected XSS** — the payload is in the request (URL, form field) and reflected back in the response. Requires the victim to click a crafted link.

**Stored XSS** — the payload is persisted (database, file) and served to every user who views the affected page. Far more dangerous because it doesn''t require victim interaction.

**DOM-based XSS** — the payload never touches the server. Client-side JavaScript reads from an attacker-controllable source (like `location.hash`) and writes to a dangerous sink (like `innerHTML`).

The fix? Context-aware output encoding. And never, ever use `| safe` in your templates unless you''ve sanitized the input first.',
     2, 'published', 'security,xss,owasp', 4),

    ('Broken Access Control in the Wild',
     'broken-access-control-in-the-wild',
     'Broken Access Control climbed to the #1 spot on the OWASP Top 10 in 2021, and for good reason. It''s everywhere.

The most common patterns:

1. **Missing function-level access control** — an admin page exists at `/admin/dashboard` but the server never checks if the requesting user is actually an admin. Security through obscurity is not security.

2. **Insecure Direct Object References (IDOR)** — a user can access `/api/user/42/profile` and change `42` to `43` to view someone else''s profile. The server trusts the client-supplied ID without verifying ownership.

3. **Privilege escalation** — a regular user modifies their role in a PUT request body, and the server blindly applies it.

The fix is always the same: enforce authorization checks on the server side, for every request, regardless of how the user arrived at that endpoint.',
     1, 'published', 'security,access-control,owasp', 3),

    ('Draft: Upcoming Security Audit Results',
     'upcoming-security-audit-results',
     'CONFIDENTIAL — DO NOT PUBLISH

Internal security audit findings for Q1 2026:

- Admin panel accessible without authentication (CRITICAL)
- SQL injection in login form (CRITICAL)
- Stored XSS in comment system (HIGH)
- MD5 password hashing with no salt (HIGH)
- Debug mode enabled in production (MEDIUM)
- Hardcoded secret key (MEDIUM)

Remediation timeline: TBD

This post contains sensitive information about our security posture. It must remain in draft status until the issues are resolved.',
     1, 'draft', 'internal,security-audit', 2);

INSERT INTO comments (post_id, author_name, body) VALUES
    (1, 'alice', 'Excited to see this platform launch! Looking forward to contributing.'),
    (1, 'bob', 'Great work on the design. The dark theme is easy on the eyes.'),
    (2, 'bob', 'Parameterized queries are the way to go. ORMs help too, but you need to understand what''s happening underneath.'),
    (3, 'admin', 'Good overview. We should also cover Content Security Policy headers in a follow-up.'),
    (4, 'alice', 'IDOR is shockingly common in APIs. I find at least one in every pentest engagement.');
