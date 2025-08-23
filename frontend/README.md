Frontend: Next.js, and deploy with Vercel
Backend: Flask, and run on an EC2 instance

User workflow:
1. User visits the site on their browser. Vercel serves the web pages
2. They choose some options to filter the videos by. This sends an API request to the Flask backend server, which gets the filtered videos from the database and then they can be displayed to the user

Scaling:
1. Vercel automatically handles scaling and caching for the frontend server
2. One EC2 instance for the Flask should be sufficient for now. If the Flask server starts to receive too many requests, then we can create a load balancer in AWS and scale horizontally by increasing the number of EC2 instances and running the Flask server on each of them. The load balancer will distribute traffic to each of the servers.