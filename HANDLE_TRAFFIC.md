# Here are some caveats how to properly handle traffics:

- The basic idea is our infrastructure & application must be ready to serve users regardless of the number. We might to use Traffic Shaping, Having Warm Pool Instances, Having scheduled scaling plan, Having predictable scaling, Malicious Traffic filtering (Firewall or similar), Having Rate limit and ensure the client side able to handle it with exponential backoff or similar, Having edge / caching mechanism.
- You have to understand the current user behaviour e.g when they usually access our website/application. On daily basis or just in specific time e.g an events, new feature, yearly events like black friday, end of year, eve festival etc.
- You need to work together with product team / PM so you understand when they will ship new feature that might gain attention from many users.
