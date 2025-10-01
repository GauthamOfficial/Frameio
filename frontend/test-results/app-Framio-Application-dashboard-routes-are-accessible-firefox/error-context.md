# Page snapshot

```yaml
- generic [active] [ref=e1]:
  - link "Skip to Clerk keyless mode content" [ref=e2] [cursor=pointer]:
    - /url: "#--clerk-keyless-prompt-button"
  - paragraph [ref=e6]: Loading...
  - button "Open Next.js Dev Tools" [ref=e12] [cursor=pointer]:
    - img [ref=e13] [cursor=pointer]
  - alert [ref=e17]
  - generic [ref=e18]:
    - button "Missing environment keys" [expanded] [ref=e19]:
      - generic [ref=e20]:
        - img [ref=e21]
        - paragraph [ref=e23] [cursor=pointer]: Missing environment keys
    - generic [ref=e24]:
      - region "Missing environment keys" [ref=e25]:
        - paragraph [ref=e26]: You claimed this application but haven't set keys in your environment. Get them from the Clerk Dashboard.
      - link "Get API keys" [ref=e28] [cursor=pointer]:
        - /url: https://dashboard.clerk.com/apps/app_33SF1V30mDGeDVCnLqmK0nLlLvl/instances/ins_33SF1WjZBeipK6bE7KSkvU62sTY/api-keys
```